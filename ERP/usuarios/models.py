from django.contrib.auth.models import AbstractUser
from django.urls import reverse

class Usuario(AbstractUser):
    def get_absolute_url(self):
        return reverse('usuarios:perfil')