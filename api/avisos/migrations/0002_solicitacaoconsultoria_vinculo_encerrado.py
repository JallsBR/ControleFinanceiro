from django.db import migrations, models


def sync_vinculo_encerrado_from_consultoria(apps, schema_editor):
    SolicitacaoConsultoria = apps.get_model("avisos", "SolicitacaoConsultoria")
    Consultoria = apps.get_model("users", "Consultoria")
    for s in SolicitacaoConsultoria.objects.filter(aceito=True, vinculo_encerrado=False):
        if Consultoria.objects.filter(
            gerente_id=s.consultor_id,
            cliente_id=s.usuario_id,
            status="encerrada",
        ).exists():
            SolicitacaoConsultoria.objects.filter(pk=s.pk).update(vinculo_encerrado=True)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("avisos", "0001_initial"),
        ("users", "0005_consultoria_assinatura_is_gerente"),
    ]

    operations = [
        migrations.AddField(
            model_name="solicitacaoconsultoria",
            name="vinculo_encerrado",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="Verdadeiro quando o pedido foi aceite mas a consultoria (vínculo) já não está ativa.",
                verbose_name="vínculo de consultoria encerrado",
            ),
        ),
        migrations.RunPython(
            sync_vinculo_encerrado_from_consultoria,
            noop_reverse,
        ),
    ]
