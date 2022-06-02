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

    path('solicitantes/', views.Solicitante_ListView.as_view(), name='solicitante_list'),
    #path('solicitantes/detail/<uuid:pk>/', views.Solicitante_DetailView.as_view(), name='solicitante_view'),
    path('solicitantes/create/', views.Solicitante_CreateView.as_view(), name='solicitante_create'),
    path('solicitantes/update/<uuid:pk>/', views.Solicitante_UpdateView.as_view(), name='solicitante_update'),
    path('solicitantes/delete/<uuid:pk>/', views.Solicitante_DeleteView.as_view(), name='solicitante_delete'),

    path('motivos/', views.Motivo_ListView.as_view(), name='motivo_list'),
    #path('motivos/detail/<uuid:pk>/', views.Motivo_DetailView.as_view(), name='motivo_view'),
    path('motivos/create/', views.Motivo_CreateView.as_view(), name='motivo_create'),
    path('motivos/update/<uuid:pk>/', views.Motivo_UpdateView.as_view(), name='motivo_update'),
    path('motivos/delete/<uuid:pk>/', views.Motivo_DeleteView.as_view(), name='motivo_delete'),

    path('documentosfha/delete/<uuid:pk>/', views.DocumentoFHA_DeleteView.as_view(), name='documentofha_delete'),

    path('solicitudfha/create/<uuid:doc>/', views.SolicitudFHA_CreateView.as_view(), name='solicitudfha_create'),
    path('solicitudfha/consulta_motivo/', views.ajax_consulta_motivo, name='solicitudfha_consulta_motivo')
]