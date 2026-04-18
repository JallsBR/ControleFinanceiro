from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("avisos", "0003_mensagem_thread_root"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mensagem",
            name="assunto",
        ),
    ]
