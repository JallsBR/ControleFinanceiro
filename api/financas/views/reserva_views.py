from app.financas_subject import get_financas_subject_user
from financas.models import Reserva
from financas.serializers import ReservaSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework import status

class ReservaListCreateView(generics.ListCreateAPIView):
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]
    # Filtros e ordenação
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        'ativa': ['exact'],           # ?ativa=True ou ?ativa=False
    }
    ordering_fields = [
        'id',
        'nome',
        'valor',
        'ativa',
        'created_at',
        'created_by',
    ]
    ordering = ['-created_at']  # padrão
    def get_queryset(self):
        return Reserva.objects.filter(created_by=get_financas_subject_user(self.request))

    def perform_create(self, serializer):
        serializer.save(created_by=get_financas_subject_user(self.request))


class ReservaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Reserva.objects.filter(created_by=get_financas_subject_user(self.request))
    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        return obj
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {"detail": "Reserva removida com sucesso."},
            status=status.HTTP_200_OK
        )


"""
    Trazer só ativas:
    /api/reservas/?ativa=True

    Trazer só inativas:
    /api/reservas/?ativa=False

    Ordenar por valor crescente:
    /api/reservas/?ordering=valor

    Ordenar por valor decrescente:
    /api/reservas/?ordering=-valor
"""