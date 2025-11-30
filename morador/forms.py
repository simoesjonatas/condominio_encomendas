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
    bloco = forms.ModelChoiceField(
        queryset=Bloco.objects.all(),
        required=True,
        label="Bloco",
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "bloco-select",
        }),
    )

    apartamento = forms.ModelChoiceField(
        queryset=Apartamento.objects.none(),
        required=True,
        label="Apartamento",
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "apartamento-select",
        }),
    )

    class Meta:
        model = Morador
        fields = ["nome", "apartamentos"]
        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do morador",
            }),
            "apartamentos": forms.SelectMultiple(attrs={
                "class": "d-none",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # SE FOR POST → pegar bloco selecionado
        if "bloco" in self.data:
            try:
                bloco_id = int(self.data.get("bloco"))
                self.fields["apartamento"].queryset = Apartamento.objects.filter(bloco_id=bloco_id)
            except (ValueError, TypeError):
                pass

        # SE FOR EDIÇÃO
        elif self.instance.pk:
            apartamentos = self.instance.apartamentos.all()
            if apartamentos:
                bloco = apartamentos.first().bloco
                self.fields["bloco"].initial = bloco
                self.fields["apartamento"].queryset = Apartamento.objects.filter(bloco=bloco)
                self.fields["apartamento"].initial = apartamentos.first()
