from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users import services as user_services


class TermoUsoAtualView(APIView):
    """Retorna o Termo de Uso vigente para exibição antes do cadastro."""

    permission_classes = [AllowAny]

    def get(self, request):
        termo = user_services.obter_termo_vigente()
        if termo is None:
            return Response(
                {"detail": "Nenhum Termo de Uso está publicado no momento."},
                status=404,
            )
        return Response(
            {
                "version": termo.version,
                "titulo": termo.titulo,
                "conteudo": termo.conteudo,
                "vigente_desde": termo.vigente_desde,
            }
        )
