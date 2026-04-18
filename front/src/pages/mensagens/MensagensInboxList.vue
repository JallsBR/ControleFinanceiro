<template>
  <aside class="inbox" aria-label="Lista de conversas">
    <div v-if="loading" class="inbox__estado">
      <i class="pi pi-spin pi-spinner" aria-hidden="true" />
      <span>A carregar…</span>
    </div>
    <p v-else-if="!items.length" class="inbox__vazio">
      Nenhuma conversa.
    </p>
    <ul v-else class="inbox__lista" role="listbox">
      <li
        v-for="c in items"
        :id="'conv-' + c.thread_root_id"
        :key="c.thread_root_id"
        role="option"
        :aria-selected="selectedThreadId === c.thread_root_id"
        class="inbox__item"
        :class="{ 'inbox__item--ativo': selectedThreadId === c.thread_root_id }"
      >
        <button
          type="button"
          class="inbox__btn"
          @click="$emit('select', c.thread_root_id)"
        >
          <span class="inbox__nome">{{ nomeContato(c) }}</span>
          <span class="inbox__meta">
            <time :datetime="c.ultima_mensagem_em">{{ formatarCurto(c.ultima_mensagem_em) }}</time>
            <Badge
              v-if="c.nao_lidas > 0"
              :value="c.nao_lidas > 99 ? '99+' : String(c.nao_lidas)"
              severity="danger"
              class="inbox__badge"
            />
          </span>
          <span class="inbox__preview">{{ c.preview }}</span>
        </button>
      </li>
    </ul>
  </aside>
</template>

<script setup>
import Badge from 'primevue/badge'

defineProps({
  items: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  selectedThreadId: { type: Number, default: null }
})

defineEmits(['select'])

function nomeContato (c) {
  const u = c?.outro_utilizador
  if (!u) return '—'
  const fn = (u.first_name || '').trim()
  const ln = (u.last_name || '').trim()
  const nome = [fn, ln].filter(Boolean).join(' ')
  if (nome) return nome
  return u.username || u.email || `ID ${u.id}`
}

function formatarCurto (iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    const now = new Date()
    const sameDay =
      d.getDate() === now.getDate() &&
      d.getMonth() === now.getMonth() &&
      d.getFullYear() === now.getFullYear()
    if (sameDay) {
      return d.toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' })
    }
    return d.toLocaleDateString('pt-PT', { day: '2-digit', month: 'short' })
  } catch (_) {
    return ''
  }
}
</script>

<style scoped>
.inbox {
  --msg-borda: color-mix(in srgb, var(--texto-secundario) 34%, transparent);
  border: 1px solid var(--msg-borda);
  border-radius: 12px;
  background: var(--bg-secundario);
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.inbox__estado,
.inbox__vazio {
  padding: 1rem;
  color: var(--texto-secundario);
  font-size: 0.9rem;
}

.inbox__estado {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.inbox__lista {
  list-style: none;
  margin: 0;
  padding: 0.35rem 0;
  overflow-y: auto;
  flex: 1;
  max-height: min(70vh, 36rem);
}

.inbox__item {
  margin: 0;
  padding: 0;
}

.inbox__btn {
  width: 100%;
  margin: 0;
  padding: 0.65rem 0.85rem;
  border: none;
  border-bottom: 1px solid var(--msg-borda);
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  transition: background-color 0.15s ease, box-shadow 0.15s ease;
}

.inbox__item:last-child .inbox__btn {
  border-bottom: none;
}

.inbox__btn:hover {
  background: color-mix(in srgb, var(--texto-secundario) 10%, var(--bg-primario));
}

.inbox__item--ativo .inbox__btn {
  background: color-mix(in srgb, var(--sucesso) 14%, var(--bg-secundario));
  box-shadow: inset 3px 0 0 var(--sucesso);
}

.inbox__item--ativo .inbox__btn:hover {
  background: color-mix(in srgb, var(--sucesso) 18%, var(--bg-secundario));
}

.inbox__nome {
  font-weight: 600;
  font-size: 0.92rem;
  color: var(--texto-primario);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.inbox__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.72rem;
  color: var(--texto-secundario);
}

.inbox__badge :deep(.p-badge) {
  border-radius: 9999px !important;
  min-width: 1.1rem;
  height: 1.1rem;
  font-size: 0.62rem;
  padding: 0 0.3rem;
}

.inbox__preview {
  font-size: 0.78rem;
  color: var(--texto-secundario);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}
</style>
