# Generated manually for 2FA por e-mail (OTP)

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0009_alter_aceitetermouso_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="two_factor_enabled",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text=(
                    "Se verdadeiro, o login exige um código OTP enviado ao e-mail cadastrado."
                ),
                verbose_name="autenticação em dois fatores",
            ),
        ),
        migrations.CreateModel(
            name="TwoFactorChallenge",
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
                ("code_hash", models.CharField(max_length=128, verbose_name="hash do código")),
                ("expires_at", models.DateTimeField(db_index=True, verbose_name="expira em")),
                (
                    "consumed_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="consumido em"
                    ),
                ),
                (
                    "attempts",
                    models.PositiveSmallIntegerField(default=0, verbose_name="tentativas"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="criado em"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="two_factor_challenges",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="usuário",
                    ),
                ),
            ],
            options={
                "verbose_name": "desafio 2FA",
                "verbose_name_plural": "desafios 2FA",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["user", "expires_at"],
                        name="users_twofa_user_id_expires_idx",
                    ),
                ],
            },
        ),
    ]
