"""
Usuário "dono" dos dados de finanças na request (tenant + filtros created_by).

Por padrão é o usuário autenticado (JWT). Com o header ``X-Financas-Subject-User``,
staff/superuser pode operar no tenant de qualquer utilizador com base configurada;
gerentes autenticados podem ver o contexto de um cliente com consultoria ativa
(nesse caso as rotas ``/financas/`` são só leitura; staff continua com alteração permitida).
O middleware aplica as regras e aponta o banco ``tenant``.
"""


def get_financas_subject_user(request):
    """
    Retorna o User cujos registros em ``financas`` devem ser listados/criados
    (mesmo ``id`` no tenant do cliente).
    """
    return getattr(request, "_financas_subject_user", request.user)
