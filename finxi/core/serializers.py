from .models import Demandas
from rest_framework import serializers
from django.contrib.auth.models import User

class DemandaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Demandas
        fields = ("id", "descricao", "endereco", "contato")
        extra_kwargs = {"anunciante_id": {"write-only": True}}


class AnuncianteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'get_full_name')


class DemandaSerializer(serializers.ModelSerializer):
    anunciante = AnuncianteSerializer()

    class Meta:
        model = Demandas
        fields = ("id", "descricao", "endereco", "contato", "anunciante", "finalizado")
        depth = 1

