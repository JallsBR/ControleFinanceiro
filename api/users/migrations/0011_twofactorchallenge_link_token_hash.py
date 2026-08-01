# Generated manually — link mágico 2FA

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0010_two_factor_enabled_challenge"),
    ]

    operations = [
        migrations.AddField(
            model_name="twofactorchallenge",
            name="link_token_hash",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Token do link de login no e-mail; nunca em claro.",
                max_length=128,
                verbose_name="hash do link mágico",
            ),
        ),
    ]
