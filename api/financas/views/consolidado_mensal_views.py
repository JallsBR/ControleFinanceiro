from datetime import datetime

from app.financas_subject import get_financas_subject_user
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from financas import services as financas_services
from financas.models import ConsolidadoMensal
from financas.serializers import ConsolidadoMensalSerializer
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

CONSOLIDADOS_ULTIMOS_MESES = 12


class ConsolidadoMensalListCreateView(generics.ListCreateAPIView):
    serializer_class = ConsolidadoMensalSerializer
    permission_classes = [IsAuthenticated]
    # Filtros e ordenação
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        'ano': ['exact'],           # ?ano=2025
        'mes': ['exact'],           # ?mes=1
        'total_entradas': ['exact'],           # ?total_entradas=1000.00
        'total_saidas': ['exact'],           # ?total_saidas=1000.00
    }
    ordering_fields = [
        'ano',
        'mes',
        'total_entradas',
        'total_saidas',
    ]
    ordering = ['-ano', '-mes']  # padrão: mais recentes primeiro

    def get_queryset(self):
        return ConsolidadoMensal.objects.filter(
            created_by=get_financas_subject_user(self.request)
        )

    def list(self, request, *args, **kwargs):
        user = get_financas_subject_user(request)
        todos = str(request.query_params.get("todos", "")).lower() in (
            "1",
            "true",
            "yes",
        )
        di = request.query_params.get("data_inicio")
        df = request.query_params.get("data_fim")

        if todos:
            data = financas_services.consolidados_mensais_todos_calculados(user)
            return Response(data)

        if di and df:
            try:
                d0 = datetime.strptime(di.strip(), "%Y-%m-%d").date()
                d1 = datetime.strptime(df.strip(), "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {
                        "detail": "Parâmetros data_inicio e data_fim devem estar no formato YYYY-MM-DD.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if d0 > d1:
                return Response(
                    {"detail": "data_inicio não pode ser posterior a data_fim."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data = financas_services.consolidados_mensais_por_intervalo(user, d0, d1)
            return Response(data)

        data = financas_services.consolidados_mensais_ultimos_n(
            user, CONSOLIDADOS_ULTIMOS_MESES
        )
        return Response(data)
    def perform_create(self, serializer):
        serializer.save(created_by=get_financas_subject_user(self.request))


class ConsolidadoMensalRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ConsolidadoMensalSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return ConsolidadoMensal.objects.filter(
            created_by=get_financas_subject_user(self.request)
        )
    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        return obj
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {"detail": "Consolidado Mensal removido com sucesso."},
            status=status.HTTP_200_OK
        )


"""
Modo de Uso
    Listagem (GET):
    - Sem parâmetros: até os últimos 12 meses com movimentações (totais calculados).
    - ?todos=1 — todos os meses com movimentações (análise).
    - ?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD — meses civis que intersectam o período (totais por mês calculados a partir das movimentações).

    Trazer todos os consolidados mensais (12 últimos por omissão):
    /api/consolidados-mensais/
    Criar um novo consolidado mensal:
    /api/consolidados-mensais/
    {
        "ano": 2025,
        "mes": 1,
        "total_entradas": 1000.00,
        "total_saidas": 1000.00
    }
    Atualizar um consolidado mensal:
    /api/consolidados-mensais/1/
    {
        "ano": 2025,
        "mes": 1,
        "total_entradas": 1000.00,
        "total_saidas": 1000.00
    }
    Remover um consolidado mensal:
    /api/consolidados-mensais/1/
    {
        "ano": 2025,
        "mes": 1,
        "total_entradas": 1000.00,
        "total_saidas": 1000.00
    }
"""