from django.urls import path
from .views import (
    lista_blocos, novo_bloco,
    lista_apartamentos, novo_apartamento,
    lista_moradores, novo_morador, editar_morador

)

urlpatterns = [
    path("blocos/", lista_blocos, name="lista_blocos"),
    path("blocos/novo/", novo_bloco, name="novo_bloco"),

    path("apartamentos/", lista_apartamentos, name="lista_apartamentos"),
    path("apartamentos/novo/", novo_apartamento, name="novo_apartamento"),
    path("moradores/", lista_moradores, name="lista_moradores"),
    path("moradores/novo/", novo_morador, name="novo_morador"),
    path("moradores/<int:pk>/editar/", editar_morador, name="editar_morador"),
]
