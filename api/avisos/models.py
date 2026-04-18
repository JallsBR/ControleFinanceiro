from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Mensagem(models.Model):
    remetente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mensagens_enviadas",
        verbose_name=_("remetente"),
    )
    destino = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mensagens_recebidas",
        verbose_name=_("destino"),
    )
    lido = models.BooleanField(_("lido"), default=False)
    resposta = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="respostas",
        verbose_name=_("resposta a"),
    )
    thread_root_id = models.PositiveIntegerField(
        _("id raiz da conversa"),
        db_index=True,
        null=True,
        blank=True,
        help_text=_("Identificador da primeira mensagem da conversa (thread)."),
    )
    mensagem = models.CharField(_("mensagem"), max_length=500)
    star = models.BooleanField(_("destacar (estrela)"), default=False)
    created_at = models.DateTimeField(_("criado em"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("mensagem")
        verbose_name_plural = _("mensagens")

    def __str__(self):
        return f"{self.remetente_id} → {self.destino_id}"


class SolicitacaoConsultoria(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="solicitacoes_consultoria_como_usuario",
        verbose_name=_("usuário"),
    )
    consultor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="solicitacoes_consultoria_como_consultor",
        verbose_name=_("consultor"),
    )
    mensagem = models.CharField(_("mensagem"), max_length=250)
    aceito = models.BooleanField(_("aceito"), default=False)
    vinculo_encerrado = models.BooleanField(
        _("vínculo de consultoria encerrado"),
        default=False,
        db_index=True,
        help_text=_(
            "Verdadeiro quando o pedido foi aceite mas a consultoria (vínculo) já não está ativa."
        ),
    )
    created_at = models.DateTimeField(_("criado em"), auto_now_add=True)
    updated_at = models.DateTimeField(_("atualizado em"), auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("solicitação de consultoria")
        verbose_name_plural = _("solicitações de consultoria")

    def __str__(self):
        if not self.aceito:
            st = "pendente"
        elif self.vinculo_encerrado:
            st = "encerrada"
        else:
            st = "aceito"
        return f"{self.usuario_id} → {self.consultor_id} ({st})"
