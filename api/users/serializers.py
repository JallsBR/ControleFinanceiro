from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
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
        )


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
