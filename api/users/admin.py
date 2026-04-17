from django.contrib import admin
from users.models import Assinatura, Consultoria, User


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
    list_display = ("user", "status", "plano_slug", "current_period_end", "updated_at")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email", "stripe_customer_id", "stripe_subscription_id")
    raw_id_fields = ("user",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "last_name", "email", "is_gerente", "tenant_db_name")
    search_fields = ("username", "last_name", "email")
    list_filter = ("is_staff", "is_superuser", "is_gerente")
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