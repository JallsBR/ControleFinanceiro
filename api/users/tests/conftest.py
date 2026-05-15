import pytest

from users.models import TermoUso
from users.services import publicar_termo_inicial


@pytest.fixture
def termo_uso_vigente(db):
    publicar_termo_inicial()
    return TermoUso.objects.get(version="1.0.0", ativo=True)
