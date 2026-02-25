from rest_framework import serializers
from .models import *

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class MovimentacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimentacao
        fields = '__all__'

class MovimentacaoRecorrenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimentacaoRecorrente
        fields = '__all__'  

