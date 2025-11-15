from django import forms
from .models import Bloco, Apartamento, Morador

class BlocoForm(forms.ModelForm):
    class Meta:
        model = Bloco
        fields = ["nome"]
        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Bloco A, Torre 1…"
            })
        }


class ApartamentoForm(forms.ModelForm):
    class Meta:
        model = Apartamento
        fields = ["bloco", "numero"]
        widgets = {
            "bloco": forms.Select(attrs={"class": "form-select"}),
            "numero": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: 101, 202, 801…"
            }),
        }

class MoradorForm(forms.ModelForm):
    class Meta:
        model = Morador
        fields = ["nome", "apartamentos"]
        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do morador"
            }),

            # Select múltiplo para os apartamentos
            "apartamentos": forms.SelectMultiple(attrs={
                "class": "form-select",
                "size": 5   # bom para mobile e desktop
            }),
        }