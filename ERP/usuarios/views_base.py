from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView


class TemplateView_Login(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')

class ListView_Login(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = reverse_lazy('login')

class DetailView_Login(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    login_url = reverse_lazy('login')

class CreateView_Login(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = reverse_lazy('login')
    success_message = _('Registro guardado correctamente')

class UpdateView_Login(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = reverse_lazy('login')
    success_message = _('Registro actualizado correctamente')

class DeleteView_Login(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
