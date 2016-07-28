from django.shortcuts import render
from django.views import generic
from ss.models import SSUser, InviteCode, Node


# Create your views here.
class SSUserCreate(generic.CreateView):
    model = SSUser
    fields = '__all__'


class NodeList(generic.ListView):
    model = Node
