from django.contrib import admin
from .models import *

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'created_by')
    search_fields = ('nome', 'tipo')
    ordering = ('nome',)

@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('valor', 'tipo', 'data', 'categoria', 'created_by')
    search_fields = ('valor', 'tipo', 'data', 'categoria', 'created_by')
    ordering = ('data',)

@admin.register(MovimentacaoRecorrente)
class MovimentacaoRecorrenteAdmin(admin.ModelAdmin):
    list_display = ('valor', 'tipo', 'data_inicio', 'data_fim', 'categoria', 'created_by')
    search_fields = ('valor', 'tipo', 'data_inicio', 'data_fim', 'categoria', 'created_by')
    ordering = ('data_inicio',)
