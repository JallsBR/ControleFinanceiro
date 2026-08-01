from django.contrib import admin
from users.models import (
    AceiteTermoUso,
    Assinatura,
    Consultoria,
    PasswordResetChallenge,
    TermoUso,
    TwoFactorChallenge,
    User,
)


def _excluir_objetos_relacionados(queryset):
    """Exclui em cascata todos os objetos de finanças vinculados ao(s) usuário(s).
    Ícones são tratados com cuidado: categorias de qualquer usuário que referenciem
    ícones deste usuário têm icone anulado antes, para não bloquear por PROTECT.
    """
    from financas.models import (
        Movimentacao,
        MovimentacaoRecorrente,
        Meta,
        Reserva,
        ConsolidadoMensal,
        Investimento,
        Categoria,
        Icone,
    )
    for user in queryset:
        Movimentacao.objects.filter(created_by=user).delete()
        MovimentacaoRecorrente.objects.filter(created_by=user).delete()
        Meta.objects.filter(created_by=user).delete()
        Reserva.objects.filter(created_by=user).delete()
        ConsolidadoMensal.objects.filter(created_by=user).delete()
        Investimento.objects.filter(usuario=user).delete()
        Investimento.objects.filter(created_by=user).delete()
        # Remove referência a ícones deste usuário em QUALQUER categoria (evita PROTECT ao deletar ícones)
        Categoria.objects.filter(icone__created_by=user).update(icone=None)
        Categoria.objects.filter(created_by=user).delete()
        Icone.objects.filter(created_by=user).delete()


@admin.register(Consultoria)
class ConsultoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "gerente", "cliente", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("gerente__username", "gerente__email", "cliente__username", "cliente__email")
    raw_id_fields = ("gerente", "cliente")


@admin.register(Assinatura)
class AssinaturaAdmin(admin.ModelAdmin):
    list_display = ("user", "plano", "status", "plano_slug", "current_period_end", "updated_at")
    list_filter = ("plano", "status")
    search_fields = ("user__username", "user__email", "stripe_customer_id", "stripe_subscription_id")
    raw_id_fields = ("user",)


@admin.register(TermoUso)
class TermoUsoAdmin(admin.ModelAdmin):
    list_display = ("version", "titulo", "ativo", "vigente_desde", "created_at")
    list_filter = ("ativo",)
    search_fields = ("version", "titulo")
    readonly_fields = ("created_at",)


@admin.register(AceiteTermoUso)
class AceiteTermoUsoAdmin(admin.ModelAdmin):
    list_display = ("user", "termo", "aceito_em", "ip_address")
    list_filter = ("termo__version",)
    search_fields = ("user__username", "user__email")
    raw_id_fields = ("user", "termo")
    readonly_fields = ("aceito_em",)


@admin.register(PasswordResetChallenge)
class PasswordResetChallengeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "expires_at", "consumed_at", "created_at")
    list_filter = ("consumed_at",)
    search_fields = ("user__username", "user__email", "id")
    raw_id_fields = ("user",)
    readonly_fields = ("id", "token_hash", "created_at")


@admin.register(TwoFactorChallenge)
class TwoFactorChallengeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "expires_at", "consumed_at", "attempts", "created_at")
    list_filter = ("consumed_at",)
    search_fields = ("user__username", "user__email", "id")
    raw_id_fields = ("user",)
    readonly_fields = ("id", "code_hash", "created_at")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "last_name",
        "email",
        "is_gerente",
        "two_factor_enabled",
        "tenant_db_name",
    )
    search_fields = ("username", "last_name", "email")
    list_filter = ("is_staff", "is_superuser", "is_gerente", "two_factor_enabled")
    ordering = ('email',)

    def save_model(self, request, obj, form, change):
        obj.save()

    def get_deleted_objects(self, objs, request):
        """Permite confirmar a exclusão: os relacionados serão removidos em cascata pelo delete_queryset."""
        deleted_objects, model_count, perms_needed, protected = super().get_deleted_objects(
            objs, request
        )
        return deleted_objects, model_count, perms_needed, []

    def delete_model(self, request, obj):
        _excluir_objetos_relacionados([obj])
        obj.delete()

    def delete_queryset(self, request, queryset):
        _excluir_objetos_relacionados(queryset)
        queryset.delete()