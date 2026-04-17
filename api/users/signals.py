import re
from datetime import timedelta

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db import connections
from django.utils import timezone

from app.db_router import get_skip_categorias_signal
from financas.service import criar_categorias_iniciais
from users.models import Assinatura


def _drop_tenant_db_if_exists(db_name):
    """Remove o banco do tenant. Ignora erros (ex.: banco já não existir)."""
    if not db_name or not db_name.strip():
        return
    if not re.match(r"^[a-zA-Z0-9_]+$", db_name):
        return
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
    except Exception:
        pass


@receiver(pre_delete, sender=get_user_model())
def drop_tenant_db_on_user_delete(sender, instance, **kwargs):
    """Ao deletar um usuário que tem banco dedicado (tenant_db_name), remove o banco."""
    if getattr(instance, "tenant_db_name", None):
        _drop_tenant_db_if_exists(instance.tenant_db_name)


@receiver(post_save, sender=get_user_model())
def criar_categorias_usuario(sender, instance, created, **kwargs):
    if created and not get_skip_categorias_signal():
        criar_categorias_iniciais(instance)


@receiver(post_save, sender=get_user_model())
def criar_assinatura_inicial(sender, instance, created, **kwargs):
    """Novo usuário: plano Comum, status ativa, período de 30 dias a partir da criação."""
    if not created:
        return
    if Assinatura.objects.filter(user_id=instance.pk).exists():
        return
    Assinatura.objects.create(
        user=instance,
        plano=Assinatura.Plano.COMUM,
        status=Assinatura.Status.ATIVA,
        current_period_end=timezone.now() + timedelta(days=30),
    )
