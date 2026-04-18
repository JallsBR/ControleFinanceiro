"""Endpoints REST de consultoria (vínculo ativo, clientes do gerente, contadores)."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.financas_subject import get_financas_subject_user
from avisos.models import SolicitacaoConsultoria
from users.models import Consultoria, User


def _user_brief(u: User) -> dict:
    if u is None:
        return None
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "first_name": u.first_name or "",
        "last_name": u.last_name or "",
    }


def _nome_exibicao(u: User) -> str:
    if u is None:
        return ""
    fn = (u.first_name or "").strip()
    ln = (u.last_name or "").strip()
    full = f"{fn} {ln}".strip()
    if full:
        return full
    return u.username or str(u.pk)


class ConsultoriaVinculoAtualView(APIView):
    """Consultoria ativa em que o utilizador autenticado é cliente (gerente = consultor)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        subject = get_financas_subject_user(request)
        row = (
            Consultoria.objects.filter(
                cliente_id=subject.id,
                status=Consultoria.Status.ATIVA,
            )
            .select_related("gerente")
            .first()
        )
        if not row:
            return Response({"consultor": None, "consultoria_id": None})
        g = row.gerente
        data = _user_brief(g)
        if data is not None:
            data["nome_exibicao"] = _nome_exibicao(g)
        return Response({"consultor": data, "consultoria_id": row.id})


class ConsultoriaClientesView(APIView):
    """Clientes com consultoria ativa para o gerente autenticado."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        subject = get_financas_subject_user(request)
        if not getattr(subject, "is_gerente", False):
            return Response(
                {"detail": "Apenas consultores (gerentes) podem listar clientes."},
                status=403,
            )
        qs = (
            Consultoria.objects.filter(
                gerente_id=subject.id,
                status=Consultoria.Status.ATIVA,
            )
            .select_related("cliente")
            .order_by("-updated_at")
        )
        out = []
        for c in qs:
            u = c.cliente
            item = _user_brief(u)
            if item is not None:
                item["nome_exibicao"] = _nome_exibicao(u)
                item["consultoria_id"] = c.id
            out.append(item)
        return Response({"results": out})


class ConsultoriaSolicitacoesPendentesCountView(APIView):
    """Contagem de solicitações em avisos ainda não aceites (recebidas + enviadas)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        uid = get_financas_subject_user(request).id
        recebidas = SolicitacaoConsultoria.objects.filter(
            consultor_id=uid, aceito=False
        ).count()
        enviadas = SolicitacaoConsultoria.objects.filter(
            usuario_id=uid, aceito=False
        ).count()
        total = recebidas + enviadas
        return Response(
            {"recebidas": recebidas, "enviadas": enviadas, "total": total}
        )


class ConsultoriaVinculoEncerrarView(APIView):
    """
    Encerra uma consultoria ativa (cliente ou consultor/gerente).
    O registo mantém-se com status ``encerrada``.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        row = get_object_or_404(Consultoria, pk=pk)
        if row.status != Consultoria.Status.ATIVA:
            return Response(
                {"detail": "Esta consultoria já não está ativa."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subject = get_financas_subject_user(request)
        uid = subject.id
        if row.gerente_id != uid and row.cliente_id != uid:
            return Response(
                {"detail": "Não tem permissão para encerrar este vínculo."},
                status=status.HTTP_403_FORBIDDEN,
            )
        row.status = Consultoria.Status.ENCERRADA
        row.save(update_fields=["status", "updated_at"])
        SolicitacaoConsultoria.objects.filter(
            consultor_id=row.gerente_id,
            usuario_id=row.cliente_id,
            aceito=True,
        ).update(vinculo_encerrado=True)
        return Response(
            {"detail": "Consultoria encerrada com sucesso."},
            status=status.HTTP_200_OK,
        )
