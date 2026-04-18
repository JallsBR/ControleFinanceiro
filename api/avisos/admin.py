from django.contrib import admin

from .models import Mensagem, SolicitacaoConsultoria


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "thread_root_id",
        "remetente",
        "destino",
        "lido",
        "star",
        "created_at",
    )
    list_filter = ("lido", "star", "created_at")
    search_fields = ("mensagem",)
    raw_id_fields = ("remetente", "destino", "resposta")
    ordering = ("-created_at",)


@admin.register(SolicitacaoConsultoria)
class SolicitacaoConsultoriaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "usuario",
        "consultor",
        "aceito",
        "vinculo_encerrado",
        "created_at",
    )
    list_filter = ("aceito", "vinculo_encerrado", "created_at")
    search_fields = ("mensagem",)
    raw_id_fields = ("usuario", "consultor")
    ordering = ("-created_at",)
