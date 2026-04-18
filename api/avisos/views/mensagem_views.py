from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.financas_subject import get_financas_subject_user
from avisos.filters import MensagemFilter
from avisos.models import Mensagem
from avisos.serializers import MensagemSerializer, UserBriefSerializer
from avisos.mensagens_permissoes import destinatarios_permitidos_queryset, user_e_helpdesk
from users.models import User


def get_remetente_mensagem(request):
    """
    Em modo consultor (só leitura no cliente), o remetente real é o JWT (gerente),
    não o utilizador monitorizado (cliente).
    """
    if getattr(request, "_financas_subject_readonly", False):
        return request.user
    return get_financas_subject_user(request)


class MensagemListCreateView(generics.ListCreateAPIView):
    serializer_class = MensagemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = MensagemFilter

    def get_queryset(self):
        subject = get_financas_subject_user(self.request)
        return (
            Mensagem.objects.filter(Q(remetente=subject) | Q(destino=subject))
            .select_related("remetente", "destino")
            .order_by("created_at")
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        ctx["remetente_efetivo"] = get_remetente_mensagem(self.request)
        return ctx

    def perform_create(self, serializer):
        serializer.save(remetente=get_remetente_mensagem(self.request))


class MensagemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MensagemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        subject = get_financas_subject_user(self.request)
        return Mensagem.objects.filter(
            Q(remetente=subject) | Q(destino=subject)
        ).select_related("remetente", "destino")

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        ctx["remetente_efetivo"] = get_remetente_mensagem(self.request)
        return ctx

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs["pk"])

    def perform_destroy(self, instance):
        if instance.remetente_id != get_remetente_mensagem(self.request).id:
            raise PermissionDenied("Só o remetente pode eliminar a mensagem.")
        super().perform_destroy(instance)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Mensagem removida com sucesso."},
            status=status.HTTP_200_OK,
        )


class MensagemDestinatariosView(APIView):
    """Lista utilizadores que o remetente efetivo pode contactar."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        rem = get_remetente_mensagem(request)
        qs = destinatarios_permitidos_queryset(rem)
        limit = 500 if user_e_helpdesk(rem) else 200
        data = UserBriefSerializer(qs[:limit], many=True).data
        return Response({"results": data})


class MensagemNaoLidasCountView(APIView):
    """Contagem de mensagens não lidas na caixa do contexto atual."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        subject = get_financas_subject_user(request)
        n = Mensagem.objects.filter(destino_id=subject.id, lido=False).count()
        return Response({"count": n})


class MensagemConversasView(APIView):
    """Lista de conversas (threads) para o inbox."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        subject = get_financas_subject_user(request)
        nome = (request.query_params.get("nome") or "").strip()
        q = (request.query_params.get("q") or "").strip()
        favorita = str(request.query_params.get("favorita", "")).lower() in (
            "1",
            "true",
            "yes",
            "on",
        )

        base = Mensagem.objects.filter(
            Q(remetente_id=subject.id) | Q(destino_id=subject.id)
        ).filter(thread_root_id__isnull=False)

        fb = base
        if q:
            fb = fb.filter(mensagem__icontains=q)
        if nome:
            v = nome
            fb = fb.filter(
                Q(remetente__first_name__icontains=v)
                | Q(remetente__last_name__icontains=v)
                | Q(remetente__username__icontains=v)
                | Q(remetente__email__icontains=v)
                | Q(destino__first_name__icontains=v)
                | Q(destino__last_name__icontains=v)
                | Q(destino__username__icontains=v)
                | Q(destino__email__icontains=v)
            )
        if favorita:
            fb = fb.filter(destino_id=subject.id, star=True)

        rows = (
            fb.values("thread_root_id")
            .annotate(
                last_at=Max("created_at"),
                nao_lidas=Count(
                    "id", filter=Q(destino_id=subject.id, lido=False)
                ),
            )
            .order_by("-last_at")[:400]
        )

        out = []
        for row in rows:
            tid = row["thread_root_id"]
            last = (
                base.filter(thread_root_id=tid)
                .order_by("-created_at")
                .select_related("remetente", "destino")
                .first()
            )
            if not last:
                continue
            oid = (
                last.destino_id
                if last.remetente_id == subject.id
                else last.remetente_id
            )
            try:
                other = User.objects.get(pk=oid)
            except User.DoesNotExist:
                continue
            out.append(
                {
                    "thread_root_id": tid,
                    "outro_utilizador": UserBriefSerializer(other).data,
                    "ultima_mensagem_em": last.created_at,
                    "preview": (last.mensagem or "")[:180],
                    "nao_lidas": row["nao_lidas"],
                }
            )
        return Response({"results": out})


class MensagemMarcarThreadLidasView(APIView):
    """Marca todas as mensagens não lidas de uma thread como lidas."""

    permission_classes = [IsAuthenticated]

    def post(self, request, thread_root_id):
        subject = get_financas_subject_user(request)
        try:
            tid = int(thread_root_id)
        except (TypeError, ValueError):
            return Response({"detail": "Identificador inválido."}, status=400)
        if tid <= 0:
            return Response({"detail": "Identificador inválido."}, status=400)
        if not Mensagem.objects.filter(
            thread_root_id=tid,
        ).filter(Q(remetente_id=subject.id) | Q(destino_id=subject.id)).exists():
            return Response({"detail": "Conversa não encontrada."}, status=404)
        n = Mensagem.objects.filter(
            thread_root_id=tid,
            destino_id=subject.id,
            lido=False,
        ).update(lido=True)
        return Response({"marcadas": n}, status=status.HTTP_200_OK)
