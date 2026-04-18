import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Mensagem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "assunto",
                    models.CharField(max_length=150, verbose_name="assunto"),
                ),
                (
                    "lido",
                    models.BooleanField(default=False, verbose_name="lido"),
                ),
                (
                    "mensagem",
                    models.CharField(max_length=500, verbose_name="mensagem"),
                ),
                (
                    "link",
                    models.CharField(
                        blank=True, max_length=155, verbose_name="link"
                    ),
                ),
                (
                    "star",
                    models.BooleanField(
                        default=False, verbose_name="destacar (estrela)"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="criado em"
                    ),
                ),
                (
                    "destino",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mensagens_recebidas",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="destino",
                    ),
                ),
                (
                    "remetente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mensagens_enviadas",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="remetente",
                    ),
                ),
                (
                    "resposta",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="respostas",
                        to="avisos.mensagem",
                        verbose_name="resposta a",
                    ),
                ),
            ],
            options={
                "verbose_name": "mensagem",
                "verbose_name_plural": "mensagens",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="SolicitacaoConsultoria",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "mensagem",
                    models.CharField(max_length=250, verbose_name="mensagem"),
                ),
                (
                    "aceito",
                    models.BooleanField(default=False, verbose_name="aceito"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="criado em"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="atualizado em"
                    ),
                ),
                (
                    "consultor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="solicitacoes_consultoria_como_consultor",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="consultor",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="solicitacoes_consultoria_como_usuario",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="usuário",
                    ),
                ),
            ],
            options={
                "verbose_name": "solicitação de consultoria",
                "verbose_name_plural": "solicitações de consultoria",
                "ordering": ["-created_at"],
            },
        ),
    ]
