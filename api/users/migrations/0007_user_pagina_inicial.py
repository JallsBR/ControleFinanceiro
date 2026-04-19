from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_assinatura_plano_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="pagina_inicial",
            field=models.CharField(
                choices=[
                    ("dashboard", "Painel (dashboard)"),
                    ("relatorio", "Relatório"),
                    ("administrar", "Administrar"),
                    ("consultoria", "Consultoria"),
                ],
                db_index=True,
                default="dashboard",
                max_length=20,
                verbose_name="página inicial após login",
            ),
        ),
    ]
