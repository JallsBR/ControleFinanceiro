from django.db.models import Q
from rest_framework import serializers

from app.financas_subject import get_financas_subject_user
from app.consultoria_subject import request_user_pode_atuar_como_consultor_da_solicitacao
from users.models import User

from .models import Mensagem, SolicitacaoConsultoria


def resolve_gerente_por_identificador(identifier: str) -> User:
    """Resolve utilizador consultor (is_gerente) por e-mail ou username, sem listar utilizadores."""
    s = (identifier or "").strip()
    if not s:
        raise serializers.ValidationError(
            {"consultor_identifier": "Identificador vazio."}
        )
    if "@" in s:
        u = User.objects.filter(email__iexact=s).first()
        msg = "Não foi encontrado consultor com este e-mail."
    else:
        u = User.objects.filter(username__iexact=s).first()
        msg = "Não foi encontrado consultor com este nome de utilizador."
    if not u:
        raise serializers.ValidationError({"consultor_identifier": msg})
    if not getattr(u, "is_gerente", False):
        raise serializers.ValidationError(
            {
                "consultor_identifier": (
                    "Este utilizador não está registado como consultor."
                )
            }
        )
    return u


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class MensagemSerializer(serializers.ModelSerializer):
    remetente = UserBriefSerializer(read_only=True)
    destino = UserBriefSerializer(read_only=True)
    destino_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="destino", write_only=True
    )

    class Meta:
        model = Mensagem
        fields = (
            "id",
            "remetente",
            "destino",
            "destino_id",
            "assunto",
            "lido",
            "resposta",
            "mensagem",
            "link",
            "star",
            "created_at",
        )
        read_only_fields = ("remetente", "destino", "created_at")

    def validate_resposta(self, value):
        if value is None:
            return value
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return value
        user = request.user
        if not Mensagem.objects.filter(
            Q(remetente=user) | Q(destino=user), pk=value.pk
        ).exists():
            raise serializers.ValidationError(
                "A mensagem referenciada em resposta não existe ou não lhe pertence."
            )
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return attrs
        user = request.user
        if self.instance is None:
            return attrs
        # destinatário controla leitura / estrela
        if self.instance.destino_id != user.id:
            incoming = attrs.keys()
            if "lido" in incoming and attrs.get("lido") != self.instance.lido:
                raise serializers.ValidationError(
                    {"lido": "Só o destinatário pode alterar o estado lido."}
                )
            if "star" in incoming and attrs.get("star") != self.instance.star:
                raise serializers.ValidationError(
                    {"star": "Só o destinatário pode alterar o destaque."}
                )
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop("destino", None)
        return super().update(instance, validated_data)


class SolicitacaoConsultoriaSerializer(serializers.ModelSerializer):
    usuario = UserBriefSerializer(read_only=True)
    consultor = UserBriefSerializer(read_only=True)
    consultor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_gerente=True),
        source="consultor",
        write_only=True,
        required=False,
    )
    consultor_identifier = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )

    class Meta:
        model = SolicitacaoConsultoria
        fields = (
            "id",
            "usuario",
            "consultor",
            "consultor_id",
            "consultor_identifier",
            "mensagem",
            "aceito",
            "vinculo_encerrado",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "usuario",
            "consultor",
            "vinculo_encerrado",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        if self.instance is not None and getattr(
            self.instance, "vinculo_encerrado", False
        ):
            if attrs:
                raise serializers.ValidationError(
                    "Esta solicitação está encerrada e não pode ser alterada."
                )
        request = self.context.get("request")
        if self.instance is not None:
            attrs.pop("consultor_identifier", None)
        if self.instance is None:
            ident_raw = attrs.pop("consultor_identifier", None)
            ident = (ident_raw or "").strip() if ident_raw is not None else ""
            consultor = attrs.get("consultor")
            if consultor is not None and ident:
                raise serializers.ValidationError(
                    {
                        "consultor_identifier": (
                            "Envie apenas o identificador (e-mail ou utilizador) "
                            "ou o ID interno, não ambos."
                        )
                    }
                )
            if consultor is None:
                if not ident:
                    raise serializers.ValidationError(
                        {
                            "consultor_identifier": (
                                "Informe o e-mail ou nome de utilizador do consultor."
                            )
                        }
                    )
                consultor = resolve_gerente_por_identificador(ident)
                attrs["consultor"] = consultor
            user = getattr(request, "user", None)
            subject = (
                get_financas_subject_user(request)
                if user and user.is_authenticated
                else None
            )
            if subject and consultor.id == subject.id:
                raise serializers.ValidationError(
                    {
                        "consultor_identifier": (
                            "Não pode solicitar consultoria a si mesmo."
                        )
                    }
                )
            if subject:
                if SolicitacaoConsultoria.objects.filter(
                    usuario_id=subject.id,
                    consultor_id=consultor.id,
                    aceito=False,
                ).exists():
                    raise serializers.ValidationError(
                        {
                            "consultor_identifier": (
                                "Já existe um pedido pendente para este consultor. "
                                "Aguarde o aceite ou a resposta do consultor. "
                                "Após a consultoria ser encerrada, poderá voltar a solicitar."
                            )
                        }
                    )
        if self.instance is None and attrs.get("aceito"):
            raise serializers.ValidationError(
                {
                    "aceito": "O aceite só pode ser definido pelo consultor após criada a solicitação."
                }
            )
        if self.instance is not None and "aceito" in attrs:
            if attrs.get("aceito") is False:
                raise serializers.ValidationError(
                    {
                        "aceito": (
                            "Para recusar, utilize a ação de eliminar o pedido "
                            "(remove o registo da base de dados)."
                        )
                    }
                )
            if attrs.get("aceito") != self.instance.aceito:
                user = getattr(request, "user", None)
                pode = user and user.is_authenticated
                if pode:
                    pode = request_user_pode_atuar_como_consultor_da_solicitacao(
                        request, self.instance.consultor_id
                    )
                if not pode:
                    raise serializers.ValidationError(
                        {
                            "aceito": "Só o consultor indicado pode aceitar a solicitação."
                        }
                    )
        return attrs

    def update(self, instance, validated_data):
        from users.models import Consultoria

        validated_data.pop("usuario", None)
        validated_data.pop("consultor", None)
        validated_data.pop("consultor_identifier", None)
        aceito_antes = instance.aceito
        instance = super().update(instance, validated_data)
        if not aceito_antes and instance.aceito:
            Consultoria.objects.update_or_create(
                gerente_id=instance.consultor_id,
                cliente_id=instance.usuario_id,
                defaults={"status": Consultoria.Status.ATIVA},
            )
        return instance
