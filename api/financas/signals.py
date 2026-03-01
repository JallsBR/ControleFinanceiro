from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver
from django.db.models import Sum
from .models import Movimentacao, ConsolidadoMensal

# Antes de salvar a movimentação, atualiza o consolidado mensal
@receiver(pre_save, sender=Movimentacao)
def atualizar_consolidado_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return  # é criação, trata no post_save

    antiga = Movimentacao.objects.get(pk=instance.pk)

    # Remove efeito antigo
    ajustar_consolidado(antiga, remover=True)


# Depois de salvar a movimentação, atualiza o consolidado mensal
@receiver(post_save, sender=Movimentacao)
def atualizar_consolidado_post_save(sender, instance, created, **kwargs):
    ajustar_consolidado(instance, remover=False)


# Depois de deletar a movimentação, atualiza o consolidado mensal
@receiver(post_delete, sender=Movimentacao)
def atualizar_consolidado_delete(sender, instance, **kwargs):
    ajustar_consolidado(instance, remover=True)


# Função para ajustar o consolidado mensal
def ajustar_consolidado(mov, remover=False):
    ano = mov.data.year
    mes = mov.data.month

    consolidado, _ = ConsolidadoMensal.objects.get_or_create(
        ano=ano,
        mes=mes,
        created_by=mov.created_by
    )

    valor = mov.valor if not remover else -mov.valor

    if mov.tipo == 'E':
        consolidado.total_entradas += valor
    else:
        consolidado.total_saidas += valor

    consolidado.save()