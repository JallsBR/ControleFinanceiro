from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Obrigatório. 150 caracteres ou menos. Letras, dígitos e @/./+/-/_ apenas."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("Já existe um usuário com esse nome."),
        },
    )
    email = models.EmailField(unique=True)
    is_gerente = models.BooleanField(
        _("é gerente de contas"),
        default=False,
        help_text=_(
            "Se verdadeiro, pode ser responsável por clientes com consultoria ativa "
            "e acessar os dados deles (com header X-Financas-Subject-User)."
        ),
    )
    tenant_db_name = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")
        ordering = ["username"]

    def __str__(self):
        return self.username


class Consultoria(models.Model):
    """
    Vínculo gerente ↔ cliente no banco **default** (não vai ao tenant).
    Um par (gerente, cliente) é único; o status controla o ciclo de vida.
    """

    class Status(models.TextChoices):
        PENDENTE = "pendente", _("Pendente de aceite")
        ATIVA = "ativa", _("Ativa")
        ENCERRADA = "encerrada", _("Encerrada")

    gerente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consultorias_como_gerente",
        verbose_name=_("gerente"),
    )
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consultorias_como_cliente",
        verbose_name=_("cliente"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("consultoria")
        verbose_name_plural = _("consultorias")
        constraints = [
            models.UniqueConstraint(
                fields=("gerente", "cliente"),
                name="uniq_consultoria_gerente_cliente",
            ),
        ]

    def __str__(self):
        return f"{self.gerente_id} → {self.cliente_id} ({self.status})"


class Assinatura(models.Model):
    """
    Assinatura no banco **default** (plataforma). Campos Stripe opcionais para depois.
    """

    class Plano(models.TextChoices):
        COMUM = "comum", _("Comum")
        PREMIUM = "premium", _("Premium")

    class Status(models.TextChoices):
        ATIVA = "ativa", _("Ativa")
        EXPIRADA = "expirada", _("Expirada")
        CANCELADA = "cancelada", _("Cancelada")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assinatura",
        verbose_name=_("usuário"),
    )
    plano = models.CharField(
        _("plano"),
        max_length=16,
        choices=Plano.choices,
        default=Plano.COMUM,
        db_index=True,
    )
    status = models.CharField(
        _("status"),
        max_length=16,
        choices=Status.choices,
        default=Status.ATIVA,
        db_index=True,
    )
    plano_slug = models.CharField(
        _("identificador Stripe / legado"),
        max_length=64,
        blank=True,
        help_text=_("Opcional: price id ou slug legado da Stripe."),
    )
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    current_period_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("fim do período atual (fatura)"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("assinatura")
        verbose_name_plural = _("assinaturas")

    def __str__(self):
        return f"{self.user_id} — {self.plano} ({self.status})"
