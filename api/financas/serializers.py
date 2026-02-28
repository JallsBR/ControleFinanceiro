from rest_framework import serializers
from .models import *

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'last_updated']

class MovimentacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimentacao
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'last_updated']

class MovimentacaoRecorrenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimentacaoRecorrente
        fields = '__all__'  
        read_only_fields = ['created_by', 'created_at', 'last_updated']

