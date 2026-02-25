from financas.models import Movimentacao
from rest_framework import generics
from financas.serializers import MovimentacaoSerializer
from rest_framework.permissions import IsAuthenticated

class MovimentacaoListCreateView(generics.ListCreateAPIView):
    queryset = Movimentacao.objects.all()
    serializer_class = MovimentacaoSerializer
    permission_classes = [IsAuthenticated]

class MovimentacaoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movimentacao.objects.all()
    serializer_class = MovimentacaoSerializer
    permission_classes = [IsAuthenticated]