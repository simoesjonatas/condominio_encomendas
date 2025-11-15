from django.contrib import admin
from .models import Encomenda


@admin.register(Encomenda)
class EncomendaAdmin(admin.ModelAdmin):

    # Quais colunas aparecem na lista
    list_display = (
        "id",
        "get_bloco",
        "get_apartamento",
        "get_morador",
        "sequencial_do_dia",
        "data_recebimento",
        "retirado",
    )

    # Filtros laterais
    list_filter = (
        "retirado",
        "data_recebimento",
        "apartamento__bloco",
    )

    # Caixa de busca
    search_fields = (
        "morador__nome",
        "apartamento__numero",
        "apartamento__bloco__nome",
        "descricao",
    )

    # Ordenação padrão
    ordering = ("-data_recebimento", "-sequencial_do_dia")

    # Mostrar o campo como somente leitura
    readonly_fields = (
        "data_recebimento",
        "sequencial_do_dia",
        "data_retirada",
        "assinatura",
    )

    # Agrupar campos na página de edição
    fieldsets = (
        ("Informações da Encomenda", {
            "fields": (
                "apartamento",
                "morador",
                "descricao",
                "local_armazenado",
            )
        }),
        ("Controle e Registro", {
            "fields": (
                "sequencial_do_dia",
                "data_recebimento",
                "recebido_por",
                "retirado",
                "retirado_por",
                "data_retirada",
                "assinatura",
            )
        }),
    )

    # Métodos para exibir informações relacionadas
    def get_bloco(self, obj):
        return obj.apartamento.bloco.nome
    get_bloco.short_description = "Bloco"

    def get_apartamento(self, obj):
        return obj.apartamento.numero
    get_apartamento.short_description = "Apto"

    def get_morador(self, obj):
        return obj.morador.nome if obj.morador else "—"
    get_morador.short_description = "Morador"
