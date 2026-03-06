from django.contrib import admin
from users.models import User


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


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'last_name', 'email')
    search_fields = ('username', 'last_name', 'email')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
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