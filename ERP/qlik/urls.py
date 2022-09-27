from django.urls import path

from . import views

app_name = 'qlik'
urlpatterns = [
    path('', views.Inicio_Template.as_view(), name='index'),

    path('streams/', views.Stream_ListView.as_view(), name='stream_list'),
    path('streams/<uuid:pk>/', views.Stream_DetailView.as_view(), name='stream_view'),
    path('streams/create/', views.Stream_CreateView.as_view(), name='stream_create'),
    path('streams/update/<uuid:pk>', views.Stream_UpdateView.as_view(), name='stream_update'),
    path('streams/delete/<uuid:pk>', views.Stream_DeleteView.as_view(), name='stream_delete'),

    path('modelo/', views.Modelo_ListView.as_view(), name='modelo_list'),
    path('modelo/<uuid:pk>/', views.Modelo_DetailView.as_view(), name='modelo_view'),
    path('modelo/create/', views.Modelo_CreateView.as_view(), name='modelo_create'),
    path('modelo/update/<uuid:pk>', views.Modelo_UpdateView.as_view(), name='modelo_update'),
    path('modelo/delete/<uuid:pk>', views.Modelo_DeleteView.as_view(), name='modelo_delete'),

    path('repositorio/', views.Repositorio_ListView.as_view(), name='repositorio_list'),
    path('repositorio/<int:pk>/', views.Repositorio_DetailView.as_view(), name='repositorio_view'),
    path('repositorio/create/', views.Repositorio_CreateView.as_view(), name='repositorio_create'),
    path('repositorio/update/<int:pk>', views.Repositorio_UpdateView.as_view(), name='repositorio_update'),
    path('repositorio/delete/<int:pk>', views.Repositorio_DeleteView.as_view(), name='repositorio_delete'),

    path('origenes/', views.OrigenDato_ListView.as_view(), name='origendato_list'),
    path('origenes/<uuid:pk>/', views.OrigenDato_DetailView.as_view(), name='origendato_view'),
    path('origenes/create/', views.OrigenDato_CreateView.as_view(), name='origendato_create'),
    path('origenes/update/<uuid:pk>', views.OrigenDato_UpdateView.as_view(), name='origendato_update'),
    path('origenes/delete/<uuid:pk>', views.OrigenDato_DeleteView.as_view(), name='origendato_delete'),
    path('origenes/delete/<uuid:pk>/<uuid:modelo>/', views.OrigenDato_DeleteView.as_view(), name='origendato_delete'),
    path('ajax/origenes/', views.ajax_origenes_asociados, name='ajax_origenes'),

    path('origenmodelo/delete/<int:pk>', views.OrigenDatoModelo_DeleteView.as_view(), name='origendatomodelo_delete'),

    path('tipolicencia/', views.TipoLicencia_ListView.as_view(), name='tipolicencia_list'),
    path('tipolicencia/<uuid:pk>/', views.TipoLicencia_DetailView.as_view(), name='tipolicencia_view'),
    path('tipolicencia/create/', views.TipoLicencia_CreateView.as_view(), name='tipolicencia_create'),
    path('tipolicencia/update/<uuid:pk>', views.TipoLicencia_UpdateView.as_view(), name='tipolicencia_update'),
    path('tipolicencia/delete/<uuid:pk>', views.TipoLicencia_DeleteView.as_view(), name='tipolicencia_delete'),

    path('licencia/', views.Licencia_ListView.as_view(), name='licencia_list'),
    path('licencia/<uuid:pk>/', views.Licencia_DetailView.as_view(), name='licencia_view'),
    path('licencia/create/', views.Licencia_CreateView.as_view(), name='licencia_create'),
    path('licencia/update/<uuid:pk>', views.Licencia_UpdateView.as_view(), name='licencia_update'),
    path('licencia/delete/<uuid:pk>', views.Licencia_DeleteView.as_view(), name='licencia_delete'),

    path('permiso/', views.Permiso_ListView.as_view(), name='permiso_list'),
    path('permiso/<uuid:pk>/', views.Permiso_DetailView.as_view(), name='permiso_view'),
    path('permiso/create/', views.Permiso_CreateView.as_view(), name='permiso_create'),
    path('permiso/update/<uuid:pk>', views.Permiso_UpdateView.as_view(), name='permiso_update'),
    path('permiso/delete/<uuid:pk>', views.Permiso_DeleteView.as_view(), name='permiso_delete'),
    path('ajax/objetos/', views.ajax_permisos_objetos, name='ajax_permiso_origenes'),
]
