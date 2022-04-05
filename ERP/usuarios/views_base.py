from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView


class TemplateView_Login(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')

class ListView_Login(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = reverse_lazy('login')

class DetailView_Login(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    login_url = reverse_lazy('login')

class CreateView_Login(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    login_url = reverse_lazy('login')

class UpdateView_Login(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')

class DeleteView_Login(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
