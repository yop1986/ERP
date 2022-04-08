from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView


class TemplateView_Login(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')

class ListView_Login(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = reverse_lazy('login')

class DetailView_Login(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    login_url = reverse_lazy('login')

class CreateView_Login(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = reverse_lazy('login')
    success_message = _('Registro guardado correctamente')

    def get_success_url(self):
        return self.object.list_url()

class UpdateView_Login(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = reverse_lazy('login')
    success_message = _('Registro actualizado correctamente')

    def get_success_url(self):
        return self.object.detail_url()

class DeleteView_Login(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    login_url = reverse_lazy('login')
    success_message = _('Registro modificado correctamente')

    def get_success_url(self, estado=True):
        if estado:
            return self.object.list_url()
        else:
            return self.object.detail_url()

class FormView_Login(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, FormView):
    login_url = reverse_lazy('login')
    success_message = _('Registro actualizado correctamente')