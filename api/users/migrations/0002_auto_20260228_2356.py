from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_admin_user(apps, schema_editor):
    User = apps.get_model('users', 'User')

    if not User.objects.filter(username='admin').exists():
        User.objects.create(
            username='admin',
            email='admin@email.com',
            password=make_password('12345'),
            is_superuser=True,
            is_staff=True,
            is_active=True,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),  # ou a última migration do users
    ]

    operations = [
        migrations.RunPython(create_admin_user),
    ]