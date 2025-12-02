from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from morador.models import Morador, Apartamento
from django.core.files.base import ContentFile
import base64
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
from django.conf import settings



class Encomenda(models.Model): 
    apartamento = models.ForeignKey(Apartamento, on_delete=models.CASCADE)
    morador = models.ForeignKey(Morador, on_delete=models.SET_NULL, null=True, blank=True)
    sequencial_do_dia = models.IntegerField()
    data_recebimento = models.DateField(auto_now_add=True)
    
    descricao = models.CharField(max_length=255, blank=True, null=True)  # Tipo do pacote
    local_armazenado = models.CharField(max_length=50, choices=[
        ('estante', 'Estante'),
        ('chao', 'Chão'),
        ('carta', 'Carta'),
        ('outro', 'Outro local')
    ], default='estante')

    recebido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    retirado = models.BooleanField(default=False)
    data_retirada = models.DateTimeField(null=True, blank=True)
    retirado_por = models.CharField(max_length=100, null=True, blank=True)
    assinatura = models.ImageField(upload_to='assinaturas/', null=True, blank=True)
    qr_code = models.ImageField(upload_to="qrcodes/", null=True, blank=True)
    identificador_pacote = models.CharField(
            max_length=100,
            null=True,
            blank=True,
            help_text="Código lido do pacote (QR ou código de barras)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_apartamento_id = self.apartamento_id

    def gerar_qrcode(self):
        # 1. Deleta o arquivo anterior (se existir)
        if self.qr_code:
            self.qr_code.delete(save=False)

        # 2. Gera novo código
        bloco = self.apartamento.bloco.nome.replace(" ", "").upper()
        apto = self.apartamento.numero.replace(" ", "")
        codigo = f"{bloco}-{apto}-{self.pk}"

        qr = qrcode.make(codigo)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        # 3. Nome fixo para não criar arquivos duplicados
        file_name = f"qrcode_{self.pk}.png"

        self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)
        super().save(update_fields=["qr_code"])

    def save(self, *args, **kwargs):
        apartamento_mudou = self.apartamento_id != self._old_apartamento_id

        super().save(*args, **kwargs)

        if apartamento_mudou:
            self.gerar_qrcode()

        self._old_apartamento_id = self.apartamento_id