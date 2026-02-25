from financas.models import MovimentacaoRecorrente
from rest_framework import generics
from financas.serializers import MovimentacaoRecorrenteSerializer
from rest_framework.permissions import IsAuthenticated


class MovimentacaoRecorrenteListCreateView(generics.ListCreateAPIView): 
    queryset = MovimentacaoRecorrente.objects.all()
    serializer_class = MovimentacaoRecorrenteSerializer
    permission_classes = [IsAuthenticated]

class MovimentacaoRecorrenteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MovimentacaoRecorrente.objects.all()
    serializer_class = MovimentacaoRecorrenteSerializer
    permission_classes = [IsAuthenticated]