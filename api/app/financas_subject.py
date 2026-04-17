"""
Usuário "dono" dos dados de finanças na request (tenant + filtros created_by).

Por padrão é o usuário autenticado (JWT). Com o header ``X-Financas-Subject-User``,
um gerente autenticado pode operar no contexto de um cliente vinculado (consultoria ativa);
o middleware valida o vínculo e aponta o banco tenant do cliente.
"""


def get_financas_subject_user(request):
    """
    Retorna o User cujos registros em ``financas`` devem ser listados/criados
    (mesmo ``id`` no tenant do cliente).
    """
    return getattr(request, "_financas_subject_user", request.user)
