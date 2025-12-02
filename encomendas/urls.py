from django.urls import path
from .views import  (
    nova_encomenda, lista_encomendas, buscar_encomendas, detalhes_encomenda, entregar_encomenda, etiqueta_encomenda,
    historico_entregas, dashboard_view, imprimir_etiquetas_lote, confirmar_entrega_view,
    ler_qrcode_view, processar_qrcode_view, ler_identificador_view,
    selecao_impressao, imprimir_encomendas, editar_encomenda,
    ler_identificador_busca_view
    )
from .assinatura_views import listar_assinaturas, download_assinatura, baixar_assinaturas_zip, confirmar_apagar_assinaturas, executar_apagar_assinaturas

urlpatterns = [
    path('', lista_encomendas, name='lista_encomendas'),
    path('nova/', nova_encomenda, name='nova_encomenda'),
    path('buscar/', buscar_encomendas, name='buscar_encomendas'),
    path('<int:pk>/detalhes/', detalhes_encomenda, name='detalhes_encomenda'),
    path('<int:pk>/editar/', editar_encomenda, name='editar_encomenda'),


    path('<int:pk>/entregar/', entregar_encomenda, name='entregar_encomenda'),
    path('<int:pk>/etiqueta/', etiqueta_encomenda, name='etiqueta_encomenda'),
    path('etiquetas/lote/', imprimir_etiquetas_lote, name='imprimir_etiquetas_lote'),
    path("<int:pk>/confirmar/", confirmar_entrega_view, name="confirmar_entrega"),
    path("scan/", ler_qrcode_view, name="ler_qrcode"),
    path("scan/processar/", processar_qrcode_view, name="processar_qrcode"),

    path("scan-identificador/", ler_identificador_view, name="ler_identificador"),
    path("ler-identificador-busca/", ler_identificador_busca_view, name="ler_identificador_busca"),


    path("impressao/", selecao_impressao, name="selecao_impressao"),
    path("imprimir/", imprimir_encomendas, name="imprimir_encomendas"),



    path('historico/', historico_entregas, name='historico_entregas'),

    path("assinaturas/", listar_assinaturas, name="listar_assinaturas"),
    path("assinaturas/<int:pk>/download/", download_assinatura, name="download_assinatura"),
    path("assinaturas/download-zip/", baixar_assinaturas_zip, name="baixar_assinaturas_zip"),
    path("assinaturas/apagar/", confirmar_apagar_assinaturas, name="confirmar_apagar_assinaturas"),
    path("assinaturas/apagar/executar/", executar_apagar_assinaturas, name="executar_apagar_assinaturas"),



    path('dashboard/', dashboard_view, name='dashboard'),



    
]
