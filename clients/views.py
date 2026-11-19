# from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Client
from .forms import ClientForm
from auxiliary.mixins import OwnerQuerysetMixin, ManagerRequiredMixin
from auxiliary.constants import CAN_VIEW_ALL_CLIENTS


class ClientListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Client
    owner_permission = CAN_VIEW_ALL_CLIENTS
    context_object_name = 'clients'
    template_name = 'clients/client_list.html'


class ClientDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    model = Client
    owner_permission = CAN_VIEW_ALL_CLIENTS
    context_object_name = 'client_data'
    template_name = 'clients/client_detail.html'


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('clients:index')


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    context_object_name = 'client'
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:index')

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)
