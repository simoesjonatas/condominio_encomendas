from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from morador.models import Morador, Apartamento
from django.core.files.base import ContentFile
import base64


class Encomenda(models.Model): 
    apartamento = models.ForeignKey(Apartamento, on_delete=models.CASCADE)
    morador = models.ForeignKey(Morador, on_delete=models.SET_NULL, null=True, blank=True)
    sequencial_do_dia = models.IntegerField()
    data_recebimento = models.DateField(auto_now_add=True)
    
    descricao = models.CharField(max_length=255, blank=True, null=True)  # Tipo do pacote
    local_armazenado = models.CharField(max_length=50, choices=[
        ('estante', 'Estante'),
        ('chao', 'Chão'),
        ('outro', 'Outro local')
    ], default='estante')

    recebido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    retirado = models.BooleanField(default=False)
    data_retirada = models.DateTimeField(null=True, blank=True)
    retirado_por = models.CharField(max_length=100, null=True, blank=True)
    assinatura = models.ImageField(upload_to='assinaturas/', null=True, blank=True)

    def __str__(self):
        return f"#{self.sequencial_do_dia} - {self.morador}"
