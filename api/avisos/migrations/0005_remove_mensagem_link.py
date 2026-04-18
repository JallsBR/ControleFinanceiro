from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("avisos", "0004_remove_mensagem_assunto"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mensagem",
            name="link",
        ),
    ]
