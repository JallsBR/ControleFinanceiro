from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


def publicar_termo_v1(apps, schema_editor):
    TermoUso = apps.get_model("users", "TermoUso")
    from users.legal.termo_uso_v1 import CONTEUDO, TITULO, VERSAO
    from django.utils import timezone

    if TermoUso.objects.filter(version=VERSAO).exists():
        return

    agora = timezone.now()
    TermoUso.objects.filter(ativo=True).update(ativo=False)
    TermoUso.objects.create(
        version=VERSAO,
        titulo=TITULO,
        conteudo=CONTEUDO,
        vigente_desde=agora,
        ativo=True,
    )


def remover_termo_v1(apps, schema_editor):
    TermoUso = apps.get_model("users", "TermoUso")
    TermoUso.objects.filter(version="1.0.0").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_user_pagina_inicial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TermoUso",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", models.CharField(max_length=32, unique=True, verbose_name="versão")),
                ("titulo", models.CharField(max_length=255, verbose_name="título")),
                ("conteudo", models.TextField(verbose_name="conteúdo")),
                ("vigente_desde", models.DateTimeField(db_index=True, verbose_name="vigente desde")),
                ("ativo", models.BooleanField(db_index=True, default=False, verbose_name="ativo")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "termo de uso",
                "verbose_name_plural": "termos de uso",
                "ordering": ["-vigente_desde"],
            },
        ),
        migrations.CreateModel(
            name="AceiteTermoUso",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("aceito_em", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="aceito em")),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True, unpack_ipv4=True, verbose_name="endereço IP")),
                ("user_agent", models.CharField(blank=True, default="", max_length=512, verbose_name="user agent")),
                (
                    "termo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aceites",
                        to="users.termouso",
                        verbose_name="termo",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aceites_termo",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "aceite de termo de uso",
                "verbose_name_plural": "aceites de termo de uso",
                "ordering": ["-aceito_em"],
            },
        ),
        migrations.AddConstraint(
            model_name="aceitetermouso",
            constraint=models.UniqueConstraint(fields=("user", "termo"), name="uniq_aceite_user_termo"),
        ),
        migrations.RunPython(publicar_termo_v1, remover_termo_v1),
    ]
