from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from financas.service import criar_categorias_iniciais


@receiver(post_save, sender=get_user_model())
def criar_categorias_usuario(sender, instance, created, **kwargs):
    if created:
        criar_categorias_iniciais(instance)
