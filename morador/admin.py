from django.contrib import admin
from .models import Bloco, Apartamento, Morador

@admin.register(Bloco)
class BlocoAdmin(admin.ModelAdmin):
    list_display = ("nome",)

@admin.register(Apartamento)
class ApartamentoAdmin(admin.ModelAdmin):
    list_display = ("numero", "bloco")
    list_filter = ("bloco",)

@admin.register(Morador)
class MoradorAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    filter_horizontal = ("apartamentos",)
