from django.db import migrations, models


def backfill_thread_root(apps, schema_editor):
    Mensagem = apps.get_model("avisos", "Mensagem")
    for m in Mensagem.objects.all().order_by("created_at"):
        if m.thread_root_id:
            continue
        root = m
        seen = set()
        while root.resposta_id and root.resposta_id not in seen:
            seen.add(root.pk)
            try:
                root = Mensagem.objects.get(pk=root.resposta_id)
            except Mensagem.DoesNotExist:
                break
        Mensagem.objects.filter(pk=m.pk).update(thread_root_id=root.pk)


class Migration(migrations.Migration):

    dependencies = [
        ("avisos", "0002_solicitacaoconsultoria_vinculo_encerrado"),
    ]

    operations = [
        migrations.AddField(
            model_name="mensagem",
            name="thread_root_id",
            field=models.PositiveIntegerField(
                db_index=True,
                null=True,
                verbose_name="id raiz da conversa",
                help_text="Identificador da primeira mensagem da conversa (thread).",
            ),
        ),
        migrations.RunPython(backfill_thread_root, migrations.RunPython.noop),
    ]
