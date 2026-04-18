# Contexto da aplicação – Finanças

Este ficheiro descreve **só** o domínio da app **`financas`** (movimentações, categorias, dashboard, etc.). Para mensagens internas e avisos, ver **`contexto-avisos.md`**. Para autenticação e utilizadores, ver **`contexto-usuarios.md`**.

---

## Objetivo

Módulo de controle financeiro pessoal com:
- Movimentações (entrada e saída)
- Movimentações recorrentes
- Categorias
- Metas, reservas, investimentos, consolidados mensais
- Dashboard
- Controle por usuário autenticado

---

## Arquitetura

- Backend: Django + Django Rest Framework
- Autenticação: JWT (Simple JWT, access + refresh)
- Base da API: `/api/v1/financas/`
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

## Endpoints (base: `/api/v1/financas/`)

- `categorias/` – list/create e retrieve/update/destroy
- `movimentacoes/` – list/create e retrieve/update/destroy
- `movimentacoes-recorrentes/` – list/create e retrieve/update/destroy
- `metas/` – list/create e retrieve/update/destroy
- `consolidados-mensais/` – list/create e retrieve/update/destroy
- `reservas/` – list/create e retrieve/update/destroy
- `investimentos/` – list/create e retrieve/update/destroy
- `icone/` – list/create e retrieve/update/destroy (ícones para categorias etc.)
- `dashboard/` – dados agregados para o dashboard

Todos exigem autenticação JWT e filtram por `created_by`.

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

---

## Documentação relacionada

- **`contexto-avisos.md`** – mensagens internas e API `/api/v1/avisos/`.
- **`contexto-usuarios.md`** – JWT, modelo `User`, consultoria.