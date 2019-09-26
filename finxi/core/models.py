from django.db import models
from django.contrib.auth.models import User


class Demandas(models.Model):
    descricao = models.CharField(verbose_name='Descrição',max_length=150)
    endereco = models.CharField(verbose_name="endereço", max_length=60)
    contato = models.CharField(verbose_name='Contato',max_length=150)
    anunciante = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    finalizado = models.BooleanField(default=False)

    def __str__(self):
        return self.descricao

    class Meta:
        verbose_name = 'Demanda'
        verbose_name_plural = 'Demandas'

