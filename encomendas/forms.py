from django import forms
from .models import Encomenda

class EncomendaForm(forms.ModelForm):
    class Meta:
        model = Encomenda
        fields = ['descricao', 'local_armazenado']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Caixa média, frágil…'}),
            'local_armazenado': forms.Select(attrs={'class': 'form-select'}),
        }

class EntregaForm(forms.Form):
    retirado_por = forms.CharField(
        label="Quem retirou",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Nome de quem recebeu"
        })
    )

    assinatura_base64 = forms.CharField(widget=forms.HiddenInput())
