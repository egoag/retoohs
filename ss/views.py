import random
import qrcode
import base64
import datetime
from io import StringIO
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.http.response import JsonResponse, HttpResponse
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from ss.models import SSUser, InviteCode, Node
from ss import forms


class StaffMixin(object):
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated() or not user.is_staff:
            raise PermissionDenied

        return super(StaffMixin, self).dispatch(request, *args, **kwargs)


class EmailVerifiedRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('my')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated() or not request.user.email_verified:
            messages.add_message(request, messages.WARNING, '邮箱未激活')
            return self.handle_no_permission()
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class SSLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('ss:create')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated() or not getattr(request.user, 'ss_user', None):
            messages.add_message(request, messages.WARNING, '需要激活Shadowsocks账号')
            return self.handle_no_permission()
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class Index(SSLoginRequiredMixin, TemplateView):
    template_name = 'ss/index.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context.update({'page_msg': 'User Center', 'page_header': '用户中心'})
        return context


class SSUserCreate(EmailVerifiedRequiredMixin, generic.CreateView):
    model = SSUser
    form_class = forms.SSUserForm

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'ss_user'):
            return redirect('ss:index')
        return super(SSUserCreate, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        # add request.user to form init kwargs
        kwargs = super(SSUserCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        if self.request.GET.get('code'):
            kwargs['code'] = self.request.GET.get('code')
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(SSUserCreate, self).get_context_data(**kwargs)
        context.update({'page_msg': 'Initial Shadowsocks', 'page_header': '开始科学上网'})
        return context


class InviteCodeCreate(LoginRequiredMixin, StaffMixin, generic.CreateView):
    model = InviteCode
    form_class = forms.InviteCodeForm
    success_url = reverse_lazy('ss:invite_code_list')

    def dispatch(self, request, *args, **kwargs):
        return super(InviteCodeCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InviteCodeCreate, self).get_context_data(**kwargs)
        context.update({'page_msg': 'Add Invitation Codes', 'page_header': '添加邀请码'})
        return context


class InviteCodeList(LoginRequiredMixin, generic.ListView):
    model = InviteCode

    def get_queryset(self):
        return InviteCode.objects.filter(user=None).order_by('time_created')[:15]

    def get_context_data(self, **kwargs):
        context = super(InviteCodeList, self).get_context_data(**kwargs)
        context.update({'page_msg': 'Invitation Codes', 'page_header': '邀请码'})
        return context


class NodeList(SSLoginRequiredMixin, generic.ListView):
    model = Node

    def get_context_data(self, **kwargs):
        context = super(NodeList, self).get_context_data(**kwargs)
        context.update({'page_header': '节点列表', 'page_msg': 'Node List'})
        return context


class NodeCreate(LoginRequiredMixin, StaffMixin, generic.CreateView):
    model = Node
    form_class = forms.NodeForm
    success_url = reverse_lazy('ss:node_list')

    def get_context_data(self, **kwargs):
        context = super(NodeCreate, self).get_context_data(**kwargs)
        context.update({'page_msg': 'Create Node', 'page_header': '添加节点'})
        return context


class CheckIn(SSLoginRequiredMixin, generic.View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CheckIn, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        user = getattr(request.user, 'ss_user', None)
        if timezone.now() - datetime.timedelta(days=1) > user.last_check_in_time:
            if user.transfer_enable < 2 * 1024 * 1024 * 1024:
                traffic = int(1024 * 1024 * 1024 + random.random() * 100 * 1024 * 1024)
            else:
                traffic = int(random.random() * 100 * 1024 * 1024)
            user.transfer_enable += traffic
            user.last_check_in_time = timezone.now()
            user.save()
            return JsonResponse({'msg': '获得了{:.2f}MB流量'.format(traffic / 1024 / 1024)})
        else:
            raise PermissionDenied('24小时内签到一次')


def get_ss_qr(request):
    if request.user.is_anonymous():
        return JsonResponse({'error': 'unauthorized'})

    if not hasattr(request.user, 'ss_user'):
        return JsonResponse({'error': 'no linked shadowsocks account'})
    ss_user = request.user.ss_user

    if request.GET.get('nid'):
        try:
            node = Node.objects.get(pk=request.GET.get('nid'))
        except Node.DoesNotExist:
            return JsonResponse({'error': 'node not exist'})
    else:
        node = Node.objects.all().order_by('-weight')
        if node:
            node = node[0]
        else:
            return JsonResponse({'error': 'no node at all'})

    password = '{}:{}@{}:{}'.format(node.method, ss_user.password, node.server, ss_user.port)
    img = qrcode.make('ss://{}'.format(base64.b64encode(bytes(password, 'utf8')).decode('ascii')))
    response = HttpResponse(content_type="image/png")
    img.save(response)
    return response
