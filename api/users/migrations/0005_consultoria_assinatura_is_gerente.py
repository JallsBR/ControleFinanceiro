from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_alter_user_username"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_gerente",
            field=models.BooleanField(
                default=False,
                help_text="Se verdadeiro, pode ser responsável por clientes com consultoria ativa e acessar os dados deles (com header X-Financas-Subject-User).",
                verbose_name="é gerente de contas",
            ),
        ),
        migrations.CreateModel(
            name="Consultoria",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("pendente", "Pendente de aceite"),
                            ("ativa", "Ativa"),
                            ("encerrada", "Encerrada"),
                        ],
                        db_index=True,
                        default="pendente",
                        max_length=20,
                        verbose_name="status",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "cliente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consultorias_como_cliente",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="cliente",
                    ),
                ),
                (
                    "gerente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consultorias_como_gerente",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="gerente",
                    ),
                ),
            ],
            options={
                "verbose_name": "consultoria",
                "verbose_name_plural": "consultorias",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Assinatura",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("inativa", "Inativa"),
                            ("trial", "Período de teste"),
                            ("ativa", "Ativa"),
                            ("pagamento_pendente", "Pagamento pendente"),
                            ("cancelada", "Cancelada"),
                        ],
                        db_index=True,
                        default="inativa",
                        max_length=30,
                        verbose_name="status",
                    ),
                ),
                (
                    "plano_slug",
                    models.CharField(
                        blank=True,
                        help_text="Ex.: basico, premium — alinhar depois com price id da Stripe.",
                        max_length=64,
                        verbose_name="identificador do plano",
                    ),
                ),
                ("stripe_customer_id", models.CharField(blank=True, max_length=255)),
                ("stripe_subscription_id", models.CharField(blank=True, max_length=255)),
                (
                    "current_period_end",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="fim do período atual (fatura)",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assinatura",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="usuário",
                    ),
                ),
            ],
            options={
                "verbose_name": "assinatura",
                "verbose_name_plural": "assinaturas",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="consultoria",
            constraint=models.UniqueConstraint(
                fields=("gerente", "cliente"),
                name="uniq_consultoria_gerente_cliente",
            ),
        ),
    ]
