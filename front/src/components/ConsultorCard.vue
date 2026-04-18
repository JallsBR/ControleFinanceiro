<template>
  <article class="consultor-card" :aria-label="ariaLabel">
    <div class="consultor-card__main">
      <div class="consultor-card__icone-wrap">
        <div class="icone-container">
          <i class="pi pi-user" aria-hidden="true" />
        </div>
      </div>
      <h3 class="consultor-card__nome">{{ titulo }}</h3>
      <p v-if="subtitulo" class="consultor-card__meta">{{ subtitulo }}</p>
      <slot />
    </div>

    <div
      class="consultor-card__actions"
      role="group"
      :aria-label="'Ações para ' + titulo"
    >
      <Button
        v-if="mostrarVisualizar && podeAbrirVisualizacao"
        type="button"
        class="consultor-card__btn"
        icon="pi pi-eye"
        rounded
        text
        severity="success"
        :aria-label="'Ver finanças de ' + titulo + ' (novo separador, só leitura)'"
        title="Ver finanças do cliente (só leitura)"
        @click="abrirVisualizacaoCliente"
      />
      <Button
        v-if="mostrarEncerrar"
        type="button"
        class="consultor-card__btn"
        icon="pi pi-trash"
        rounded
        text
        severity="danger"
        :loading="encerrando"
        :disabled="encerrando"
        :aria-label="'Encerrar consultoria com ' + titulo"
        title="Encerrar consultoria"
        @click="onEncerrar"
      />
      <Button
        type="button"
        class="consultor-card__btn"
        icon="pi pi-send"
        rounded
        text
        severity="success"
        :aria-label="'Mensagem a ' + titulo + ' (em breve)'"
        title="Mensagem (em breve)"
      />
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import Button from 'primevue/button'
import {
  FINANCAS_VIEW_AS_DISPLAY_QUERY,
  FINANCAS_VIEW_AS_KIND_QUERY,
  FINANCAS_VIEW_AS_USER_QUERY,
  SUBJECT_VIEW_KIND
} from '@/constants/financasViewAs'

const props = defineProps({
  /** Nome preferencial (ex.: nome_exibicao da API) */
  nome: {
    type: String,
    default: ''
  },
  /** Texto secundário (ex.: e-mail) */
  subtitulo: {
    type: String,
    default: ''
  },
  /** Ex.: ocultar no card «O seu consultor» (cliente); consultores mantêm nos clientes. */
  mostrarVisualizar: {
    type: Boolean,
    default: true
  },
  /** PK do registo ``Consultoria`` (API) para encerrar o vínculo. */
  consultoriaId: {
    type: [Number, String],
    default: null
  },
  /** Pedido DELETE em curso para este card. */
  encerrando: {
    type: Boolean,
    default: false
  },
  /** PK do utilizador cliente (default DB) para modo visualização finanças. */
  clienteUserId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['encerrar'])

const titulo = computed(() => (props.nome || '').trim() || 'Consultor')

const ariaLabel = computed(() => {
  const s = (props.subtitulo || '').trim()
  return s ? `${titulo.value}, ${s}` : titulo.value
})

const mostrarEncerrar = computed(() => {
  const id = props.consultoriaId
  return id != null && id !== ''
})

const podeAbrirVisualizacao = computed(() => {
  const id = props.clienteUserId
  return id != null && id !== ''
})

function onEncerrar () {
  if (!mostrarEncerrar.value || props.encerrando) return
  emit('encerrar')
}

function abrirVisualizacaoCliente () {
  if (!podeAbrirVisualizacao.value) return
  const basePath = import.meta.env.BASE_URL || '/'
  const path = basePath.endsWith('/') ? basePath : `${basePath}/`
  const url = new URL(path, window.location.origin)
  url.searchParams.set(FINANCAS_VIEW_AS_USER_QUERY, String(props.clienteUserId))
  url.searchParams.set(FINANCAS_VIEW_AS_KIND_QUERY, SUBJECT_VIEW_KIND.CONSULTOR)
  const label = (props.nome || '').trim() || (props.subtitulo || '').trim()
  if (label) {
    url.searchParams.set(
      FINANCAS_VIEW_AS_DISPLAY_QUERY,
      encodeURIComponent(label.slice(0, 120))
    )
  }
  window.open(url.toString(), '_blank', 'noopener,noreferrer')
}
</script>

<style scoped>
.consultor-card {
  display: flex;
  align-items: stretch;
  gap: 0.25rem;
  min-width: 0;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  background: var(--bg-secundario);
  border-radius: 10px;
  padding: 1.05rem 0.75rem 1rem 1.15rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.consultor-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.28);
}

.consultor-card__main {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  padding-right: 0.35rem;
}

.consultor-card__icone-wrap {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 0.55rem;
}

.icone-container {
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  background-color: var(--bg-primario);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icone-container i {
  color: var(--texto-secundario);
  font-size: 1.2rem;
}

.consultor-card__nome {
  margin: 0;
  font-size: clamp(0.88rem, 3.2vw, 1.22rem);
  font-weight: 700;
  color: var(--texto-primario);
  line-height: 1.2;
  min-width: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.consultor-card__meta {
  margin: 0.22rem 0 0;
  font-size: calc(0.62rem * 1.3);
  color: var(--texto-secundario);
  line-height: 1.25;
  word-break: break-all;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.consultor-card__actions {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.2rem;
  padding: 0.15rem 0.25rem 0.15rem 0.35rem;
  margin-left: 0.05rem;
  border-left: 1px solid color-mix(in srgb, var(--texto-secundario) 14%, transparent);
}

.consultor-card__btn {
  flex-shrink: 0;
}

.consultor-card__btn :deep(.p-button) {
  width: 1.55rem;
  min-width: 1.55rem;
  height: 1.55rem;
  padding: 0;
}

.consultor-card__btn :deep(.p-button .p-button-icon) {
  font-size: 0.68rem;
}
</style>
