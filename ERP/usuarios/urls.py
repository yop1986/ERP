from django.contrib.auth import views as views_auth
from django.urls import path, include
from django.utils.translation import gettext as _

from .views import Inicio_Template, Login, Perfil_Login, Perfil_Update, PasswordChangeView

urlpatterns = [
    path('', Inicio_Template.as_view(), name='index'),
    #login/ [name='login']
    path('login/', Login.as_view(), name='login'),
    path('perfil', Perfil_Login.as_view(), name='perfil'),
    path('actualizar_pefil', Perfil_Update.as_view(), name='actualizar_perfil'),
    #password_change/ [name='password_change']
    path('password/', PasswordChangeView.as_view(), name='password_change'),

    #logout/ [name='logout']
    path('logout/', views_auth.LogoutView.as_view(), name='logout'),
    #password_change/done/ [name='password_change_done']
    #password_reset/ [name='password_reset']
    #password_reset/done/ [name='password_reset_done']
    #reset/<uidb64>/<token>/ [name='password_reset_confirm']
    #reset/done/ [name='password_reset_complete']
    
    #path('', include('django.contrib.auth.urls')),
]
