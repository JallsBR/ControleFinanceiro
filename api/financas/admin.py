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

@admin.register(Meta)
class MetaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor_meta', 'data_meta', 'prioridade', 'created_by')
    search_fields = ('nome', 'valor_meta', 'data_meta', 'prioridade', 'created_by')
    ordering = ('data_meta',)

@admin.register(ConsolidadoMensal)
class ConsolidadoMensalAdmin(admin.ModelAdmin):
    list_display = ('ano', 'mes', 'total_entradas', 'total_saidas', 'created_by')
    search_fields = ('ano', 'mes', 'total_entradas', 'total_saidas', 'created_by')
    ordering = ('ano', 'mes',)

@admin.register(Icone)
class IconeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'classe_css', 'categoria_visual', 'created_by')
    search_fields = ('nome', 'classe_css', 'categoria_visual', 'created_by')
    ordering = ('nome',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor', 'created_by')
    search_fields = ('nome', 'valor', 'created_by')
    ordering = ('nome',)

@admin.register(Investimento)
class InvestimentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'valor_inicial', 'taxa_rendimento', 'data_aplicacao', 'data_vencimento', 'ativo', 'created_by')
    search_fields = ('nome', 'tipo', 'valor_inicial', 'taxa_rendimento', 'data_aplicacao', 'data_vencimento', 'ativo', 'created_by')
    ordering = ('nome',)