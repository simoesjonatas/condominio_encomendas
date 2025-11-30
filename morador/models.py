from django.db import models

class Bloco(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.nome


class Apartamento(models.Model):
    numero = models.CharField(max_length=10)
    bloco = models.ForeignKey(Bloco, on_delete=models.CASCADE, related_name="apartamentos")

    class Meta:
        unique_together = ("numero", "bloco")
        ordering = ["bloco__id", "numero"]

    def __str__(self):
        return f"{self.bloco.nome} - Apto {self.numero}"


class Morador(models.Model):
    nome = models.CharField(max_length=100)
    apartamentos = models.ManyToManyField(Apartamento, related_name="moradores", blank=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        if self.apartamentos.exists():
            lista = ", ".join([str(a) for a in self.apartamentos.all()])
            return f"{self.nome} ({lista})"
        return self.nome
