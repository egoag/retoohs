from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from ss.models import SSUser, InviteCode, Node
from ss import forms


class SSUserCreate(LoginRequiredMixin, generic.CreateView):
    model = SSUser
    form_class = forms.SSUserForm

    def get_form_kwargs(self):
        # add request.user to form init kwargs
        kwargs = super(SSUserCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class InviteCodeCreate(generic.CreateView):
    model = InviteCode
    form_class = forms.InviteCodeForm


class NodeList(generic.ListView):
    model = Node
