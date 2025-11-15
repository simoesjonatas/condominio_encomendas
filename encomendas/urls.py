from django.urls import path
from .views import  (
    nova_encomenda, lista_encomendas, buscar_encomendas, detalhes_encomenda, entregar_encomenda, etiqueta_encomenda,
    historico_entregas, dashboard_view, imprimir_etiquetas_lote
    )

urlpatterns = [
    path('', lista_encomendas, name='lista_encomendas'),
    path('nova/', nova_encomenda, name='nova_encomenda'),
    path('buscar/', buscar_encomendas, name='buscar_encomendas'),
    path('<int:pk>/detalhes/', detalhes_encomenda, name='detalhes_encomenda'),

    path('<int:pk>/entregar/', entregar_encomenda, name='entregar_encomenda'),
    path('<int:pk>/etiqueta/', etiqueta_encomenda, name='etiqueta_encomenda'),
    path('etiquetas/lote/', imprimir_etiquetas_lote, name='imprimir_etiquetas_lote'),

    path('historico/', historico_entregas, name='historico_entregas'),

    path('dashboard/', dashboard_view, name='dashboard'),



    
]
