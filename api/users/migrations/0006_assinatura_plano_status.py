from datetime import timedelta

from django.db import migrations, models
from django.utils import timezone


def migrate_assinatura_plano_status(apps, schema_editor):
    Assinatura = apps.get_model("users", "Assinatura")
    User = apps.get_model("users", "User")

    status_map = {
        "ativa": "ativa",
        "trial": "ativa",
        "inativa": "expirada",
        "pagamento_pendente": "ativa",
        "cancelada": "cancelada",
    }

    for a in Assinatura.objects.all().iterator():
        slug = (getattr(a, "plano_slug", None) or "").lower()
        if slug in ("premium", "premium_annual", "premium_monthly"):
            plano = "premium"
        elif "premium" in slug:
            plano = "premium"
        else:
            plano = "comum"
        new_status = status_map.get(a.status, "expirada")
        Assinatura.objects.filter(pk=a.pk).update(plano=plano, status=new_status)

    now = timezone.now()
    for u in User.objects.all().iterator():
        if Assinatura.objects.filter(user_id=u.pk).exists():
            continue
        dj = getattr(u, "date_joined", None) or now
        end = dj + timedelta(days=30)
        st = "ativa" if end >= now else "expirada"
        Assinatura.objects.create(
            user_id=u.pk,
            plano="comum",
            status=st,
            current_period_end=end,
            plano_slug="",
            stripe_customer_id="",
            stripe_subscription_id="",
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_consultoria_assinatura_is_gerente"),
    ]

    operations = [
        migrations.AddField(
            model_name="assinatura",
            name="plano",
            field=models.CharField(
                choices=[("comum", "Comum"), ("premium", "Premium")],
                db_index=True,
                default="comum",
                max_length=16,
                verbose_name="plano",
            ),
        ),
        migrations.RunPython(migrate_assinatura_plano_status, noop_reverse),
        migrations.AlterField(
            model_name="assinatura",
            name="plano_slug",
            field=models.CharField(
                blank=True,
                help_text="Opcional: price id ou slug legado da Stripe.",
                max_length=64,
                verbose_name="identificador Stripe / legado",
            ),
        ),
        migrations.AlterField(
            model_name="assinatura",
            name="status",
            field=models.CharField(
                choices=[
                    ("ativa", "Ativa"),
                    ("expirada", "Expirada"),
                    ("cancelada", "Cancelada"),
                ],
                db_index=True,
                default="ativa",
                max_length=16,
                verbose_name="status",
            ),
        ),
    ]
