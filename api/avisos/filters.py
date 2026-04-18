from django.db.models import Q
from django_filters import rest_framework as filters

from avisos.models import Mensagem


class MensagemFilter(filters.FilterSet):
    """Filtros para listagem de mensagens (inbox / thread)."""

    nome = filters.CharFilter(method="filter_nome")
    q = filters.CharFilter(method="filter_q")

    class Meta:
        model = Mensagem
        fields = {
            "lido": ["exact"],
            "star": ["exact"],
            "destino": ["exact"],
            "remetente": ["exact"],
            "thread_root_id": ["exact"],
        }

    def filter_nome(self, queryset, name, value):
        v = (value or "").strip()
        if not v:
            return queryset
        uq = (
            Q(remetente__first_name__icontains=v)
            | Q(remetente__last_name__icontains=v)
            | Q(remetente__username__icontains=v)
            | Q(remetente__email__icontains=v)
            | Q(destino__first_name__icontains=v)
            | Q(destino__last_name__icontains=v)
            | Q(destino__username__icontains=v)
            | Q(destino__email__icontains=v)
        )
        return queryset.filter(uq)

    def filter_q(self, queryset, name, value):
        v = (value or "").strip()
        if not v:
            return queryset
        return queryset.filter(mensagem__icontains=v)
