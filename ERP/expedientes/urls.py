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
    
    path('niveles/<uuid:pk>/', views.Nivel_DetailView.as_view(), name='nivel_view'),
    
    path('posiciones/<uuid:pk>/', views.Posicion_DetailView.as_view(), name='posicion_view'),
    
    path('cajas/<uuid:pk>/', views.Caja_DetailView.as_view(), name='caja_view'),
]