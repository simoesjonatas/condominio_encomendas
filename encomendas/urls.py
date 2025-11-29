from django.urls import path
from .views import  (
    nova_encomenda, lista_encomendas, buscar_encomendas, detalhes_encomenda, entregar_encomenda, etiqueta_encomenda,
    historico_entregas, dashboard_view, imprimir_etiquetas_lote, confirmar_entrega_view,
    ler_qrcode_view, processar_qrcode_view, ler_identificador_view,
    )

urlpatterns = [
    path('', lista_encomendas, name='lista_encomendas'),
    path('nova/', nova_encomenda, name='nova_encomenda'),
    path('buscar/', buscar_encomendas, name='buscar_encomendas'),
    path('<int:pk>/detalhes/', detalhes_encomenda, name='detalhes_encomenda'),

    path('<int:pk>/entregar/', entregar_encomenda, name='entregar_encomenda'),
    path('<int:pk>/etiqueta/', etiqueta_encomenda, name='etiqueta_encomenda'),
    path('etiquetas/lote/', imprimir_etiquetas_lote, name='imprimir_etiquetas_lote'),
    path("<int:pk>/confirmar/", confirmar_entrega_view, name="confirmar_entrega"),
    path("scan/", ler_qrcode_view, name="ler_qrcode"),
    path("scan/processar/", processar_qrcode_view, name="processar_qrcode"),

    path("scan-identificador/", ler_identificador_view, name="ler_identificador"),




    path('historico/', historico_entregas, name='historico_entregas'),

    path('dashboard/', dashboard_view, name='dashboard'),



    
]
