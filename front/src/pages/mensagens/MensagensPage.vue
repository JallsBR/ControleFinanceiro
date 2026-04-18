<template>
  <div class="mensagens-page">
    <CardStatus
      tituloPrincipal="Mensagens"
      subtitulo="Inbox e conversas no estilo chat: contacte a equipa, o consultor ou clientes em consultoria. Use Filtrar para refinar por contacto, texto ou favoritas; as mensagens lidas permanecem no histórico."
      icone="pi pi-envelope"
      class="mensagens-page__card"
    />

    <div class="mensagens-toolbar">
      <Button
        type="button"
        icon="pi pi-refresh"
        text
        label="Atualizar"
        :loading="loadingConversas || loadingThread"
        @click="atualizarTudo"
      />
      <Button
        type="button"
        icon="pi pi-filter"
        text
        label="Filtrar"
        @click="visibleFiltro = true"
      />
      <Button
        type="button"
        label="Nova mensagem"
        icon="pi pi-plus"
        text
        @click="abrirNovaMensagemDialog"
      />
    </div>

    <div class="mensagens-layout">
      <MensagensInboxList
        :items="conversas"
        :loading="loadingConversas"
        :selected-thread-id="threadSelecionado"
        @select="onSelecionarThread"
      />
      <MensagensChatPanel
        :messages="mensagensOrdenadas"
        :loading="loadingThread"
        :other-user="contactoThread"
        :linha-preview="linhaPreviewThread"
        :context-user-id="contextoContaId"
        :star-id="starLoadingId"
        :delete-id="deleteLoadingId"
        @eliminar="onEliminarMensagem"
        @alternar-star="onAlternarStar"
        @continuar-conversa="abrirDialogContinuarConversa"
      />
    </div>

    <DialogNovaMensagem
      v-model="dialogNova"
      :resposta-id="respostaParaDialog"
      @enviada="onNovaEnviada"
    />

    <DialogFiltroMensagens
      v-model="visibleFiltro"
      :nome="filtroNome"
      :q="filtroQ"
      :favorita="filtroFavorita"
      @apply="onFiltroApply"
      @clear="onFiltroClear"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useStore } from 'vuex'
import CardStatus from '@/components/CardStatus.vue'
import Button from 'primevue/button'
import DialogFiltroMensagens from '@/components/DialogFiltroMensagens.vue'
import DialogNovaMensagem from './DialogNovaMensagem.vue'
import MensagensInboxList from './MensagensInboxList.vue'
import MensagensChatPanel from './MensagensChatPanel.vue'
import {
  listConversas,
  listMensagens,
  patchMensagem,
  eliminarMensagem,
  marcarThreadLidas
} from '@/services/mensagens'
import { useToast } from '@/utils/useToast'

const store = useStore()
const toast = useToast()

const dialogNova = ref(false)
const visibleFiltro = ref(false)
/** null = nova conversa (escolher destinatário); senão id da mensagem a que se responde. */
const respostaParaDialog = ref(null)
const filtroNome = ref('')
const filtroQ = ref('')
const filtroFavorita = ref(false)

const conversas = ref([])
const loadingConversas = ref(false)
const threadSelecionado = ref(null)
const mensagensThread = ref([])
const loadingThread = ref(false)
const starLoadingId = ref(null)
const deleteLoadingId = ref(null)

const contextoContaId = computed(() => {
  if (store.getters.subjectViewAdminActive && store.state.subjectViewMode?.userId) {
    const n = Number(store.state.subjectViewMode.userId)
    return Number.isFinite(n) ? n : null
  }
  if (store.getters.subjectViewConsultorActive && store.state.subjectViewMode?.userId) {
    const n = Number(store.state.subjectViewMode.userId)
    return Number.isFinite(n) ? n : null
  }
  const id = store.getters.getUser?.id
  return id != null ? Number(id) : null
})

const conversaAtiva = computed(() =>
  conversas.value.find((c) => c.thread_root_id === threadSelecionado.value) || null
)

const mensagensOrdenadas = computed(() =>
  [...mensagensThread.value].sort(
    (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  )
)

const contactoThread = computed(() => {
  const u = conversaAtiva.value?.outro_utilizador
  if (u) return u
  const sorted = mensagensOrdenadas.value
  const eu = contextoContaId.value
  if (!sorted.length || eu == null) return null
  const m = sorted[0]
  return m.remetente?.id === eu ? m.destino : m.remetente
})

const linhaPreviewThread = computed(() => {
  const p = conversaAtiva.value?.preview
  if (p) return p
  const sorted = mensagensOrdenadas.value
  if (!sorted.length) return ''
  const last = sorted[sorted.length - 1]
  return (last?.mensagem || '').slice(0, 160)
})

function abrirNovaMensagemDialog () {
  respostaParaDialog.value = null
  dialogNova.value = true
}

function abrirDialogContinuarConversa () {
  const arr = mensagensOrdenadas.value
  if (!arr.length) return
  respostaParaDialog.value = arr[arr.length - 1].id
  dialogNova.value = true
}

watch(dialogNova, (aberto) => {
  if (!aberto) respostaParaDialog.value = null
})

const paramsFiltrosConversas = computed(() => ({
  nome: (filtroNome.value || '').trim(),
  q: (filtroQ.value || '').trim(),
  favorita: filtroFavorita.value === true
}))

async function carregarConversas () {
  loadingConversas.value = true
  try {
    conversas.value = await listConversas(paramsFiltrosConversas.value)
    if (
      threadSelecionado.value != null &&
      !conversas.value.some((c) => c.thread_root_id === threadSelecionado.value)
    ) {
      threadSelecionado.value = null
      mensagensThread.value = []
    }
  } catch (e) {
    console.error(e)
    conversas.value = []
    toast.error('Mensagens', 'Não foi possível carregar as conversas.')
  } finally {
    loadingConversas.value = false
  }
}

async function recarregarAposFiltros () {
  await carregarConversas()
  if (threadSelecionado.value != null) {
    await carregarThreadMensagens()
  }
}

function onFiltroApply ({ nome, q, favorita }) {
  filtroNome.value = nome ?? ''
  filtroQ.value = q ?? ''
  filtroFavorita.value = favorita === true
  void recarregarAposFiltros()
}

function onFiltroClear () {
  filtroNome.value = ''
  filtroQ.value = ''
  filtroFavorita.value = false
  void recarregarAposFiltros()
}

async function carregarThreadMensagens () {
  const tid = threadSelecionado.value
  if (tid == null) {
    mensagensThread.value = []
    return
  }
  loadingThread.value = true
  try {
    const params = { thread_root_id: tid }
    const n = (filtroNome.value || '').trim()
    const q = (filtroQ.value || '').trim()
    if (n) params.nome = n
    if (q) params.q = q
    if (filtroFavorita.value) params.star = true
    mensagensThread.value = await listMensagens(params)
  } catch (e) {
    console.error(e)
    mensagensThread.value = []
    toast.error('Mensagens', 'Não foi possível carregar a conversa.')
  } finally {
    loadingThread.value = false
  }
}

async function onSelecionarThread (threadRootId) {
  threadSelecionado.value = threadRootId
  await carregarThreadMensagens()
  try {
    await marcarThreadLidas(threadRootId)
    await store.dispatch('fetchMensagensNaoLidas')
    await carregarConversas()
  } catch (e) {
    console.error(e)
  }
}

async function atualizarTudo () {
  await carregarConversas()
  if (threadSelecionado.value != null) {
    await carregarThreadMensagens()
  }
  await store.dispatch('fetchMensagensNaoLidas')
}

async function onNovaEnviada (payload) {
  toast.success('Mensagens', 'Mensagem enviada.')
  const root = payload?.thread_root_id ?? payload?.id
  if (root != null) {
    threadSelecionado.value = Number(root)
  }
  await carregarConversas()
  if (threadSelecionado.value != null) {
    await carregarThreadMensagens()
  }
  await store.dispatch('fetchMensagensNaoLidas')
}

async function onAlternarStar (m) {
  starLoadingId.value = m.id
  try {
    await patchMensagem(m.id, { star: !m.star })
    m.star = !m.star
    await carregarConversas()
  } catch (e) {
    toast.error('Mensagens', 'Não foi possível atualizar o favorito.')
  } finally {
    starLoadingId.value = null
  }
}

async function onEliminarMensagem (id) {
  deleteLoadingId.value = id
  try {
    await eliminarMensagem(id)
    toast.success('Mensagens', 'Mensagem eliminada.')
    await carregarThreadMensagens()
    await carregarConversas()
    await store.dispatch('fetchMensagensNaoLidas')
  } catch (e) {
    const d = e?.response?.data
    toast.error(
      'Mensagens',
      typeof d?.detail === 'string' ? d.detail : 'Não foi possível eliminar.'
    )
  } finally {
    deleteLoadingId.value = null
  }
}

onMounted(async () => {
  if (store.getters.subjectViewAdminActive && store.state.subjectViewMode?.userId) {
    await store.dispatch('fetchSubjectMonitoredProfile')
  }
  await carregarConversas()
})
</script>

<style scoped>
.mensagens-page__card {
  margin-bottom: 1rem;
}

.mensagens-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem 0.65rem;
  margin-bottom: 1rem;
}

.mensagens-layout {
  display: grid;
  grid-template-columns: minmax(260px, 320px) 1fr;
  gap: 1rem;
  align-items: stretch;
  min-height: min(72vh, 580px);
}

@media (max-width: 900px) {
  .mensagens-layout {
    grid-template-columns: 1fr;
  }
}
</style>
