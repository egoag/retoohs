from django.views import generic
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from ss.models import SSUser, InviteCode, Node
from ss import forms


class SSUserCreate(LoginRequiredMixin, generic.CreateView):
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


class InviteCodeCreate(generic.CreateView):
    model = InviteCode
    form_class = forms.InviteCodeForm
    success_url = '/ss/invites'

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(InviteCodeCreate, self).dispatch(request, *args, **kwargs)


class InviteCodeList(generic.ListView):
    model = InviteCode

    def get_queryset(self):
        return InviteCode.objects.filter(user=None)


class NodeList(generic.ListView):
    model = Node
