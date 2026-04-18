# Contexto da aplicação – Avisos (mensagens e consultoria)

Este documento descreve o app Django **`avisos`**: mensagens internas entre utilizadores e pedidos de **solicitação de consultoria**. Complementa `contexto-usuarios.md` (auth, `User`, vínculo **`Consultoria`** em `users.models`).

---

## Objetivo

- **Mensagens (`Mensagem`)**: inbox estilo conversa com **threads** (`thread_root_id` aponta para o id da primeira mensagem da conversa). Corpo em `mensagem` (texto curto); `lido`, `star` (favorito na perspetiva do destinatário em regras de listagem); `resposta` opcional (FK para mensagem anterior).
- **Solicitações (`SolicitacaoConsultoria`)**: fluxo de pedido entre `usuario` e `consultor` com `aceito` e `vinculo_encerrado` (detalhes nas views/serializers).

A API expõe tudo sob **`/api/v1/avisos/`** (ver `api/app/urls.py`).

---

## Quem pode falar com quem (`mensagens_permissoes.py`)

- **Helpdesk**: `is_staff` ou `is_superuser` pode trocar mensagens com **qualquer** outro utilizador (em qualquer direção).
- **Gerente e cliente**: só entre si se existir **`Consultoria`** com `status=ATIVA` (em qualquer direção: gerente→cliente ou cliente→gerente).
- **Não** é permitido enviar mensagem para si próprio.

A listagem **`mensagens/destinatarios/`** devolve apenas utilizadores permitidos para o **remetente efetivo** (ver abaixo sobre modo consultor).

---

## Contexto do utilizador nas mensagens (`get_financas_subject_user`)

As views usam o mesmo “sujeito” das finanças: em modo **visualização do cliente** (admin/consultor a monitorizar outra conta), as mensagens listadas e o destinatário nas contagens são os do **cliente** (`subject`), não do JWT.

Em modo **consultor só leitura** (`_financas_subject_readonly`), **`get_remetente_mensagem`** força o remetente da criação/edição a ser sempre o **`request.user`** (gerente), para não gravar mensagens como se fossem do cliente.

Regra geral: **`get_queryset`** filtra mensagens em que o sujeito é `remetente` **ou** `destino`.

---

## Endpoints (base: `/api/v1/avisos/`)

| Recurso | Métodos | Notas |
|---------|---------|--------|
| `mensagens/` | GET, POST | `MensagemFilter`: `nome`, `q`, `thread_root_id`, `lido`, `star`, `remetente`, `destino`, … |
| `mensagens/<pk>/` | GET, PATCH, DELETE | Apenas o **remetente** pode DELETE |
| `mensagens/conversas/` | GET | Query: `nome`, `q`, `favorita` (boolean); resposta `{ results: [...] }` com `thread_root_id`, `outro_utilizador`, preview, `nao_lidas` |
| `mensagens/threads/<thread_root_id>/marcar-lidas/` | POST | Marca não lidas onde o sujeito é destino |
| `mensagens/nao-lidas/` | GET | `{ count }` para o sujeito como destino |
| `mensagens/destinatarios/` | GET | Lista breve de utilizadores contactáveis |
| `solicitacoes-consultoria/` | GET, POST | Filtrado por participante (ver views) |
| `solicitacoes-consultoria/<pk>/` | GET, PATCH, DELETE | Conforme permissões do serializer/views |

Todos os endpoints acima exigem **JWT** (`IsAuthenticated`), salvo indicação em contrário no código.

---

## Filtros (`avisos/filters.py`)

- **`nome`**: texto em nomes, username ou email de remetente ou destino (icontains).
- **`q`**: texto no campo `mensagem` (icontains).

Na rota **`conversas/`**, os mesmos critérios são aplicados na agregação por `thread_root_id` (implementação em `mensagem_views`, não só no `FilterSet`).

---

## Padrões do projeto

- Nunca expor mensagens em que o utilizador do contexto não participe (`remetente` / `destino`).
- Validar **destino** na criação contra `pode_mensagem_entre(remetente, destino)`.
- **Threads**: ao responder (`resposta` preenchida), o backend calcula `thread_root_id`; na primeira mensagem de uma conversa nova, após gravar, pode atualizar `thread_root_id` para o próprio `pk` (ver `MensagemSerializer.create`).
- Usar **`django-filter`** (`MensagemFilter`) na listagem de mensagens.

---

## Frontend (resumo)

- Página de **Mensagens** (`front/src/pages/mensagens/`): inbox, painel de chat, dialog de nova mensagem, **filtros** num dialog alinhado ao padrão de movimentações (`DialogFiltroMensagens`).
- Serviço **`front/src/services/mensagens.js`** e estado em **Vuex** (contagem não lidas, etc.).

---

## Documentação relacionada

- **`contexto-financas.md`** – domínio financeiro e `get_financas_subject_user` no contexto de movimentações.
- **`contexto-usuarios.md`** – login JWT, modelo `User`, políticas de auth.
