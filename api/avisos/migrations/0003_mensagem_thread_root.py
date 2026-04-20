from django.db import migrations, models


def backfill_thread_root(apps, schema_editor):
    Mensagem = apps.get_model("avisos", "Mensagem")
    # .values() evita SELECT * com colunas do estado histórico (ex.: assunto) que a
    # tabela tenant pode ainda não ter se o schema foi criado a partir do modelo atual.
    rows = list(
        Mensagem.objects.order_by("created_at").values(
            "id", "resposta_id", "thread_root_id"
        )
    )
    by_pk = {r["id"]: r for r in rows}
    for m in rows:
        if m["thread_root_id"]:
            continue
        current = m
        seen = set()
        while current["resposta_id"] and current["resposta_id"] not in seen:
            seen.add(current["id"])
            parent = by_pk.get(current["resposta_id"])
            if not parent:
                break
            current = parent
        Mensagem.objects.filter(pk=m["id"]).update(thread_root_id=current["id"])


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
