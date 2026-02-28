# Contexto da Aplicação - Finanças

## Objetivo
Aplicação de controle financeiro pessoal com:
- Movimentações (entrada e saída)
- Movimentações recorrentes
- Categorias
- Controle por usuário autenticado

---

## Arquitetura

- Backend: Django + Django Rest Framework
- Autenticação: Token / JWT
- Cada registro pertence a um usuário (created_by)
- Todas as queries devem filtrar por created_by

---

## Regras de Negócio

### Movimentação Recorrente

- tipo:
  - E = Entrada
  - S = Saída

- categoria.tipo deve ser igual ao tipo da movimentação
- data_fim não pode ser menor que data_inicio
- valor não pode ser negativo
- ordering padrão: -data_inicio

---

## Padrões do Projeto

- Sempre usar:
    get_queryset() filtrando por request.user
- Sempre usar:
    perform_create() setando created_by
- Não permitir acesso a dados de outros usuários
- Validações complexas devem ir no model.clean()

---

## Filtros utilizados

- tipo
- ativa
- data_inicio
- data_fim
- ordering dinâmico via query param

---

## Boas práticas adotadas

- Services ainda não implementados
- Futuramente separar lógica recorrente em camada de domínio
- Usar django-filter para filtros