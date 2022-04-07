from django.urls import path, include

from . import views

app_name='expedientes'
urlpatterns = [
    path('', views.Inicio_Template.as_view(), name='index'),

    path('bodegas/', views.Bodega_ListView.as_view(), name='bodega_list'),
    path('bodegas/<uuid:pk>/', views.Bodega_DetailView.as_view(), name='bodega_view'),
    path('bodegas/create/', views.Bodega_CreateView.as_view(), name='bodega_create'),
    path('bodegas/update/<uuid:pk>', views.Bodega_UpdateView.as_view(), name='bodega_update'),
    path('bodegas/delete/<uuid:pk>', views.Bodega_DeleteView.as_view(), name='bodega_delete'),

    path('estantes/<uuid:pk>/', views.Estante_DetailView.as_view(), name='estante_view'),
    path('estantes/etiquetas/<uuid:pk>/', views.Estante_Etiqueta.as_view(), name='estante_labels'),
    
    path('niveles/<uuid:pk>/', views.Nivel_DetailView.as_view(), name='nivel_view'),
    path('niveles/etiquetas/<uuid:pk>/', views.Nivel_Etiqueta.as_view(), name='nivel_labels'),

    path('posiciones/<uuid:pk>/', views.Posicion_DetailView.as_view(), name='posicion_view'),
    path('posiciones/etiquetas/<uuid:pk>/', views.Posicion_Etiqueta.as_view(), name='posicion_labels'),

    path('cajas/<uuid:pk>/', views.Caja_DetailView.as_view(), name='caja_view'),
    path('cajas/etiquetas/<uuid:pk>/', views.Caja_Etiqueta.as_view(), name='caja_labels'),
]