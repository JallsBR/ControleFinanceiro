from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from users.models import Assinatura, User


class UserSerializer(serializers.ModelSerializer):
    """Perfil básico + capacidades Django para o painel admin (só staff)."""

    admin_capabilities = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_superuser',
            'is_gerente',
            'admin_capabilities',
        )

    def get_admin_capabilities(self, obj):
        if not getattr(obj, 'is_staff', False) and not getattr(obj, 'is_superuser', False):
            return None
        if getattr(obj, 'is_superuser', False):
            return {'superuser': True}
        u_app = User._meta.app_label
        g_app = Group._meta.app_label

        def u_perm(suffix):
            return obj.has_perm(f'{u_app}.{suffix}_user')

        def g_perm(suffix):
            return obj.has_perm(f'{g_app}.{suffix}_group')

        return {
            'users': {
                'view': u_perm('view') or u_perm('change'),
                'add': u_perm('add'),
                'change': u_perm('change'),
                'delete': u_perm('delete'),
            },
            'groups': {
                'view': g_perm('view') or g_perm('change'),
                'add': g_perm('add'),
                'change': g_perm('change'),
                'delete': g_perm('delete'),
            },
            # Editar permissões M2M do grupo (API PUT .../permissions)
            'group_permissions': g_perm('change'),
            # Abrir app como outro utilizador (tenant) — quem vê utilizadores no admin
            'view_financas_as_subject': u_perm('view') or u_perm('change'),
        }


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Atualização do próprio usuário (username não é alterável)."""

    current_password = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    new_password = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'current_password',
            'new_password',
        )
        extra_kwargs = {
            'email': {'required': False},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
        }

    def validate_email(self, value):
        if value is None:
            return value
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Informe um e-mail válido.')
        user = self.context['request'].user
        if (
            User.objects.exclude(pk=user.pk)
            .filter(email__iexact=value)
            .exists()
        ):
            raise serializers.ValidationError('Já existe um usuário com este e-mail.')
        return value

    def validate(self, attrs):
        new_pw = (attrs.get('new_password') or '').strip()
        cur_pw = (attrs.get('current_password') or '').strip()
        user = self.context['request'].user

        if new_pw and not cur_pw:
            raise serializers.ValidationError(
                {
                    'current_password': (
                        'Informe a senha atual para definir uma nova senha.'
                    )
                }
            )
        if cur_pw and not new_pw:
            raise serializers.ValidationError(
                {
                    'new_password': (
                        'Informe a nova senha ou deixe a senha atual em branco.'
                    )
                }
            )
        if new_pw:
            if not user.check_password(cur_pw):
                raise serializers.ValidationError(
                    {'current_password': 'Senha atual incorreta.'}
                )
            try:
                validate_password(new_pw, user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    {'new_password': list(exc.messages)}
                ) from exc
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop('current_password', None)
        new_password = (validated_data.pop('new_password', None) or '').strip()

        if new_password:
            instance.set_password(new_password)

        for attr, value in validated_data.items():
            if attr == 'email' and value is not None:
                value = (value or '').strip()
            if isinstance(value, str):
                value = value.strip()
            setattr(instance, attr, value)

        instance.save()
        return instance


class AdminUserListSerializer(serializers.ModelSerializer):
    """Usuário + plano de assinatura, grupos e flags staff/superuser para o painel admin."""

    nome_completo = serializers.SerializerMethodField()
    assinatura = serializers.SerializerMethodField()
    assinatura_status = serializers.SerializerMethodField()
    current_period_end = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    group_ids = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "is_gerente",
            "groups",
            "group_ids",
            "nome_completo",
            "assinatura",
            "assinatura_status",
            "current_period_end",
        )

    def get_nome_completo(self, obj):
        n = (obj.first_name or "").strip()
        s = (obj.last_name or "").strip()
        return " ".join(x for x in (n, s) if x) or "—"

    def _assinatura_obj(self, obj):
        try:
            return obj.assinatura
        except ObjectDoesNotExist:
            return None

    def get_assinatura(self, obj):
        a = self._assinatura_obj(obj)
        return a.plano if a else Assinatura.Plano.COMUM

    def get_assinatura_status(self, obj):
        a = self._assinatura_obj(obj)
        return a.status if a else Assinatura.Status.EXPIRADA

    def get_current_period_end(self, obj):
        a = self._assinatura_obj(obj)
        return a.current_period_end if a else None

    def get_groups(self, obj):
        return sorted(obj.groups.values_list("name", flat=True))

    def get_group_ids(self, obj):
        return list(obj.groups.order_by("name").values_list("pk", flat=True))


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """PATCH de utilizador no painel admin (inclui plano da assinatura)."""

    plano = serializers.ChoiceField(
        choices=Assinatura.Plano.choices,
        required=False,
    )
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "is_gerente",
            "plano",
            "group_ids",
        )
        extra_kwargs = {
            "email": {"required": False},
            "first_name": {"required": False, "allow_blank": True},
            "last_name": {"required": False, "allow_blank": True},
            "is_staff": {"required": False},
            "is_superuser": {"required": False},
            "is_gerente": {"required": False},
        }

    def validate_email(self, value):
        if value is None:
            return value
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Informe um e-mail válido.")
        if (
            User.objects.exclude(pk=self.instance.pk)
            .filter(email__iexact=value)
            .exists()
        ):
            raise serializers.ValidationError(
                "Já existe um utilizador com este e-mail."
            )
        return value

    def validate_group_ids(self, value):
        if value is None:
            return value
        uniq = list(dict.fromkeys(int(x) for x in value))
        if not uniq:
            return []
        if Group.objects.filter(pk__in=uniq).count() != len(uniq):
            raise serializers.ValidationError("Um ou mais grupos são inválidos.")
        return uniq

    def validate(self, attrs):
        request = self.context["request"]
        if not request.user.is_superuser:
            if "is_superuser" in attrs and attrs["is_superuser"] != self.instance.is_superuser:
                raise serializers.ValidationError(
                    {
                        "is_superuser": (
                            "Apenas um superuser pode alterar o estado de superuser."
                        )
                    }
                )
        return attrs

    def update(self, instance, validated_data):
        plano = validated_data.pop("plano", None)
        group_ids = validated_data.pop("group_ids", None)
        for attr, value in validated_data.items():
            if isinstance(value, str):
                value = value.strip()
            setattr(instance, attr, value)
        instance.save()

        if group_ids is not None:
            instance.groups.set(Group.objects.filter(pk__in=group_ids))

        if plano is not None:
            assinatura, created = Assinatura.objects.get_or_create(
                user=instance,
                defaults={
                    "plano": plano,
                    "status": Assinatura.Status.ATIVA,
                },
            )
            if not created:
                assinatura.plano = plano
                assinatura.save(update_fields=["plano", "updated_at"])

        return instance


_GROUP_USERS_PREVIEW_LIMIT = 30


class AdminGroupListSerializer(serializers.ModelSerializer):
    """Grupo Django auth para listagem admin."""

    permissions_count = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ("id", "name", "permissions_count", "users", "user_count")

    def get_permissions_count(self, obj):
        if hasattr(obj, "permissions_count"):
            return int(obj.permissions_count)
        return obj.permissions.count()

    def get_users(self, obj):
        cache = getattr(obj, "_prefetched_objects_cache", {})
        prefetched = cache.get("user_set")
        if prefetched is not None:
            user_iter = list(prefetched)[:_GROUP_USERS_PREVIEW_LIMIT]
        else:
            user_iter = list(
                obj.user_set.order_by("first_name", "last_name", "username").only(
                    "username", "first_name", "last_name"
                )[:_GROUP_USERS_PREVIEW_LIMIT]
            )
        out = []
        for u in user_iter:
            name = (u.get_full_name() or "").strip()
            out.append(name if name else (u.username or ""))
        return out

    def get_user_count(self, obj):
        if hasattr(obj, "user_count"):
            return int(obj.user_count)
        return obj.user_set.count()


class AdminGroupWriteSerializer(serializers.ModelSerializer):
    """Criar / renomear grupo."""

    class Meta:
        model = Group
        fields = ("name",)

    def validate_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Indique o nome do grupo.")
        qs = Group.objects.filter(name=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Já existe um grupo com este nome.")
        return value
