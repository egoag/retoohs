from django.shortcuts import render
from django.views import generic
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from ss.models import SSUser, InviteCode, Node
from ss import forms


class SSUserCreate(LoginRequiredMixin, generic.CreateView):
    model = SSUser
    form_class = forms.SSUserForm

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'ss_user'):
            raise PermissionDenied('已经注册过啦')
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


class InviteCodeList(generic.ListView):
    model = InviteCode


class NodeList(generic.ListView):
    model = Node
