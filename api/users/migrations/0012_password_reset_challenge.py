# Generated manually — recuperação de senha por e-mail

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0011_twofactorchallenge_link_token_hash"),
    ]

    operations = [
        migrations.CreateModel(
            name="PasswordResetChallenge",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("token_hash", models.CharField(max_length=128, verbose_name="hash do token")),
                ("expires_at", models.DateTimeField(db_index=True, verbose_name="expira em")),
                (
                    "consumed_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="consumido em"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="criado em"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="password_reset_challenges",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="usuário",
                    ),
                ),
            ],
            options={
                "verbose_name": "desafio de redefinição de senha",
                "verbose_name_plural": "desafios de redefinição de senha",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["user", "expires_at"],
                        name="users_pwdreset_user_exp_idx",
                    ),
                ],
            },
        ),
    ]
