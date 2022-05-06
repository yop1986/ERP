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

    path('tipodato/', views.TipoDato_ListView.as_view(), name='tipodato_list'),
    path('tipodato/<int:pk>/', views.TipoDato_DetailView.as_view(), name='tipodato_view'),
    path('tipodato/create/', views.TipoDato_CreateView.as_view(), name='tipodato_create'),
    path('tipodato/update/<int:pk>', views.TipoDato_UpdateView.as_view(), name='tipodato_update'),
    path('tipodato/delete/<int:pk>', views.TipoDato_DeleteView.as_view(), name='tipodato_delete'),

    path('origenes/', views.OrigenDato_ListView.as_view(), name='origendato_list'),
    path('origenes/<uuid:pk>/', views.OrigenDato_DetailView.as_view(), name='origendato_view'),
    path('origenes/create/', views.OrigenDato_CreateView.as_view(), name='origendato_create'),
    path('origenes/update/<uuid:pk>', views.OrigenDato_UpdateView.as_view(), name='origendato_update'),
    path('origenes/delete/<uuid:pk>', views.OrigenDato_DeleteView.as_view(), name='origendato_delete'),
    path('ajax/origenes/', views.ajax_origenes_asociados, name='ajax_origenes'),

    path('origenmodelo/delete/<int:pk>', views.OrigenDatoModelo_DeleteView.as_view(), name='origendatomodelo_delete'),
]
