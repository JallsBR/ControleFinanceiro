<template>
  <section class="chat" aria-label="Mensagens da conversa">
    <header v-if="otherUser" class="chat__header">
      <h2 class="chat__titulo">{{ nomeContato(otherUser) }}</h2>   
    </header>
    <div v-else class="chat__placeholder">
      <i class="pi pi-comments" aria-hidden="true" />
      <p>Selecione uma conversa à esquerda.</p>
    </div>

    <template v-if="otherUser">
      <div ref="scrollRef" class="chat__scroll" role="log">
        <div v-if="loading" class="chat__estado">
          <i class="pi pi-spin pi-spinner" aria-hidden="true" />
        </div>
        <template v-else>
          <article
            v-for="m in messages"
            :key="m.id"
            class="chat__linha"
            :class="mensagemDoUtilizadorAtivo(m) ? 'chat__linha--eu' : 'chat__linha--outro'"
          >
            <div
              class="chat__bubble"
              :class="{ 'chat__bubble--nao-lida': !m.lido && m.destino?.id === contextUserId }"
            >
              <div class="chat__bubble-inner">
                <p class="chat__texto">
                  <template v-for="(seg, si) in segmentosMensagem(m.mensagem)" :key="`${m.id}-${si}`">
                    <a
                      v-if="seg.type === 'url'"
                      :href="seg.href"
                      class="chat__texto-link"
                      target="_blank"
                      rel="noopener noreferrer"
                    >{{ seg.value }}</a>
                    <span v-else>{{ seg.value }}</span>
                  </template>
                </p>
                <footer class="chat__footer">
                  <time class="chat__hora" :datetime="m.created_at">{{ formatarData(m.created_at) }}</time>
                  <span v-if="!m.lido && m.destino?.id === contextUserId" class="chat__nao-lida">Não lida</span>
                </footer>
              </div>
              <div class="chat__accoes">
                <template v-if="m.remetente?.id === contextUserId">
                  <Button
                    type="button"
                    icon="pi pi-trash"
                    text
                    rounded
                    severity="danger"
                    class="chat__acao"
                    title="Eliminar"
                    aria-label="Eliminar mensagem"
                    :loading="deleteId === m.id"
                    @click="$emit('eliminar', m.id)"
                  />
                </template>
                <template v-else>
                  <Button
                    type="button"
                    :icon="m.star ? 'pi pi-star-fill' : 'pi pi-star'"
                    text
                    rounded
                    class="chat__acao"
                    :title="m.star ? 'Retirar favorito' : 'Marcar favorito'"
                    :aria-label="m.star ? 'Retirar favorito' : 'Marcar favorito'"
                    :loading="starId === m.id"
                    @click="$emit('alternar-star', m)"
                  />
                </template>
              </div>
            </div>
          </article>
        </template>
      </div>
      <footer class="chat__barra-responder">
        <Button
          type="button"
          label="Responder"
          icon="pi pi-reply"
          outlined
          size="small"
          :disabled="!podeResponder"
          @click="$emit('continuar-conversa')"
        />
      </footer>
    </template>
  </section>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import Button from 'primevue/button'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  otherUser: { type: Object, default: null },
  /** Pré-visualização da última mensagem (inbox) ou contexto curto. */
  linhaPreview: { type: String, default: '' },
  contextUserId: { type: Number, default: null },
  starId: { type: Number, default: null },
  deleteId: { type: Number, default: null }
})

defineEmits(['eliminar', 'alternar-star', 'continuar-conversa'])

const scrollRef = ref(null)

const podeResponder = computed(() => props.messages.length > 0)

watch(
  () => props.messages.length,
  () => scrollAoFim()
)

function scrollAoFim () {
  nextTick(() => {
    const el = scrollRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

function nomeContato (u) {
  if (!u) return '—'
  const fn = (u.first_name || '').trim()
  const ln = (u.last_name || '').trim()
  const nome = [fn, ln].filter(Boolean).join(' ')
  if (nome) return nome
  return u.username || u.email || `ID ${u.id}`
}

function formatarData (iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('pt-PT', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (_) {
    return iso
  }
}

/** O utilizador do contexto é o remetente (mensagem “minha” à esquerda). */
function mensagemDoUtilizadorAtivo (m) {
  const eu = props.contextUserId
  if (eu == null || !m?.remetente) return false
  return Number(m.remetente.id) === Number(eu)
}

/**
 * Parte o texto em segmentos texto / URL (http/https) para links clicáveis.
 */
function segmentosMensagem (raw) {
  const text = raw == null ? '' : String(raw)
  if (!text) return [{ type: 'text', value: '' }]
  const re = /https?:\/\/[^\s<]+/gi
  const out = []
  let last = 0
  let m
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) {
      out.push({ type: 'text', value: text.slice(last, m.index) })
    }
    let url = m[0]
    url = url.replace(/[),.;:!?]+$/, '')
    out.push({ type: 'url', value: url, href: url })
    last = m.index + m[0].length
  }
  if (last < text.length) {
    out.push({ type: 'text', value: text.slice(last) })
  }
  return out.length ? out : [{ type: 'text', value: text }]
}
</script>

<style scoped>
.chat {
  --msg-borda: color-mix(in srgb, var(--texto-secundario) 34%, transparent);
  border: 1px solid var(--msg-borda);
  border-radius: 12px;
  background: var(--bg-primario);
  min-height: min(70vh, 36rem);
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat__header {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--msg-borda);
  background: var(--bg-secundario);
  border-radius: 12px 12px 0 0;
}

.chat__titulo {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--texto-primario);
}

.chat__sub {
  margin: 0.25rem 0 0;
  font-size: 0.8rem;
  color: var(--texto-secundario);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.chat__placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: var(--texto-secundario);
  padding: 2rem;
}

.chat__placeholder .pi {
  font-size: 2rem;
  opacity: 0.5;
}

.chat__scroll {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem 0.65rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  min-height: 12rem;
}

.chat__estado {
  display: flex;
  justify-content: center;
  padding: 2rem;
  color: var(--texto-secundario);
}

.chat__linha {
  display: flex;
  width: 100%;
}

/* Utilizador ativo: as suas mensagens à esquerda; do outro à direita. */
.chat__linha--eu {
  justify-content: flex-start;
}

.chat__linha--outro {
  justify-content: flex-end;
}

.chat__linha--outro .chat__bubble {
  flex-direction: row-reverse;
}

.chat__bubble {
  max-width: min(100%, 28rem);
  display: flex;
  align-items: flex-end;
  gap: 0.15rem;
  position: relative;
}

.chat__bubble:hover .chat__accoes {
  opacity: 1;
}

.chat__bubble-inner {
  padding: 0.55rem 0.75rem;
  border-radius: 12px;
  background: var(--bg-secundario);
  border: 1px solid var(--msg-borda);
  flex: 1;
  min-width: 0;
}

.chat__linha--eu .chat__bubble-inner {
  background: color-mix(in srgb, var(--texto-secundario) 12%, var(--bg-secundario));
  border-color: color-mix(in srgb, var(--texto-secundario) 42%, transparent);
}

.chat__bubble--nao-lida .chat__bubble-inner {
  border-color: rgba(245, 158, 11, 0.35);
}

.chat__texto {
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.45;
  font-size: 0.88rem;
  word-break: break-word;
}

.chat__texto-link {
  color: var(--sucesso);
  text-decoration: none;
  word-break: break-all;
}

.chat__texto-link:hover {
  filter: brightness(1.12);
}

.chat__footer {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.35rem;
  font-size: 0.7rem;
  color: var(--texto-secundario);
}

.chat__nao-lida {
  font-weight: 600;
  color: rgba(245, 158, 11, 0.95);
}

.chat__accoes {
  display: flex;
  flex-direction: column;
  opacity: 0;
  transition: opacity 0.15s ease;
  flex-shrink: 0;
}

.chat__acao :deep(.p-button) {
  width: 2rem;
  height: 2rem;
  padding: 0;
}

.chat__barra-responder {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 0.65rem 0.75rem;
  border-top: 1px solid var(--msg-borda);
  flex-shrink: 0;
}
</style>
