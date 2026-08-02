"""Provisiona banco tenant MySQL para usuários sem tenant_db_name."""

from django.core.management.base import BaseCommand, CommandError

from app.db_router import set_skip_categorias_signal
from users.auth import _create_tenant_db_for_user
from users.models import User


class Command(BaseCommand):
    help = (
        "Cria e migra o banco `{DB_NAME}_user_{id}` para cada User com "
        "tenant_db_name nulo (ou para --user-id específico)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id",
            type=int,
            default=None,
            help="Provisiona apenas o usuário com este id.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Só lista quem seria provisionado.",
        )

    def handle(self, *args, **options):
        qs = User.objects.filter(tenant_db_name__isnull=True).order_by("id")
        user_id = options["user_id"]
        if user_id is not None:
            qs = User.objects.filter(id=user_id)
            if not qs.exists():
                raise CommandError(f"Usuário id={user_id} não encontrado.")
            if qs.first().tenant_db_name:
                self.stdout.write(
                    self.style.WARNING(
                        f"Usuário id={user_id} já tem tenant_db_name="
                        f"{qs.first().tenant_db_name}; nada a fazer."
                    )
                )
                return

        users = list(qs)
        if not users:
            self.stdout.write(self.style.SUCCESS("Nenhum usuário pendente de tenant."))
            return

        if options["dry_run"]:
            for u in users:
                self.stdout.write(f"  dry-run: id={u.id} username={u.username}")
            return

        ok, falhas = 0, 0
        for user in users:
            self.stdout.write(f"Provisionando id={user.id} username={user.username}…")
            set_skip_categorias_signal(True)
            try:
                _create_tenant_db_for_user(user)
                user.refresh_from_db()
                self.stdout.write(
                    self.style.SUCCESS(f"  → {user.tenant_db_name}")
                )
                ok += 1
            except Exception as exc:
                falhas += 1
                self.stderr.write(
                    self.style.ERROR(f"  falhou: {exc}")
                )
            finally:
                set_skip_categorias_signal(False)

        self.stdout.write(
            self.style.SUCCESS(f"Concluído: {ok} ok, {falhas} falha(s).")
        )
