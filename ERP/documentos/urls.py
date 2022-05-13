from django.urls import path, include

from . import views

app_name='documentos'
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

    path('cajas/', views.Caja_ListView.as_view(), name='cajas_inhabilitadas'),
    path('cajas/<uuid:pk>/', views.Caja_DetailView.as_view(), name='caja_view'),
    path('cajas/delete/<uuid:pk>', views.Caja_DeleteView.as_view(), name='caja_delete'),
    path('cajas/etiquetas/<uuid:pk>/', views.Caja_Etiqueta.as_view(), name='caja_labels'),

    path('creditos/carga/', views.CargaMasiva_Form.as_view(), name='carga'),
    path('creditos/buscar/', views.buscar_credito, name='credito_search'),
    path('creditos/<uuid:pk>/', views.Credito_DetailView.as_view(), name='credito_view'),
    path('creditos/etiquetas/<uuid:pk>/', views.Credito_Etiqueta.as_view(), name='credito_labels'),

    path('tomos/opera/', views.operaciones_tomo, name='opera_tomo'), #agrega/habilita o deshabilita tomo
    path('tomos/opera/<uuid:pk>', views.operaciones_tomo, name='opera_tomo'), #agrega/habilita o deshabilita tomo
    path('tomos/ingreso/', views.Tomo_Ingreso.as_view(), name='ingreso_tomo'), 
    path('tomos/envio/', views.Tomo_Template.as_view(), name='envio_tomo'), # visualiza el ilstado de tomos a procesar
    path('tomos/trasladar/', views.salida_tomo, name='salida_tomo'), # proceso las salidas
    path('tomos/etiquetas/<uuid:pk>/', views.Tomo_Etiqueta.as_view(), name='tomo_labels'),


]