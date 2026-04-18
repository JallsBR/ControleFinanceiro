<template>
  <div class="solicitacoes-page">
    <CardStatus
      tituloPrincipal="Solicitações de consultoria"
      subtitulo="Pedidos de utilizadores que o identificaram como consultor. Aceite o pedido para ativar o vínculo; elimine para recusar um pendente ou encerrar a consultoria já aceita."
      icone="pi pi-inbox"
      style="margin-bottom: 1rem;"
    />

    <BaseDataTable
      :items="lista"
      :loading="loading"
      :totalRecords="totalRecords"
      :first="first"
      :lazy="true"
      :reorderableColumns="true"
      @page="onPage"
    >
      <template #toolbar>
        <div class="table-toolbar">
          <div class="right">
            <Button icon="pi pi-refresh" text label="Atualizar" :loading="loading" @click="atualizarLista" />
            <Button icon="pi pi-search" text label="Filtrar" @click="abrirFiltro" />
          </div>
        </div>
      </template>

      <template #columns>
        <Column field="usuario" columnKey="usuario" header="Utilizador" :sortable="false">
          <template #body="{ data }">
            <div class="sol-user">
              <span class="sol-user-nome">{{ nomeUtilizador(data.usuario) }}</span>
              <span class="sol-user-meta">{{ data.usuario?.email || '—' }}</span>
              <span class="sol-user-meta">@{{ data.usuario?.username || '—' }}</span>
            </div>
          </template>
        </Column>

        <Column field="mensagem" columnKey="mensagem" header="Mensagem" :sortable="false">
          <template #body="{ data }">
            <span class="sol-mensagem">{{ data.mensagem }}</span>
          </template>
        </Column>

        <Column
          field="aceito"
          columnKey="aceito"
          header="Estado"
          style="width: 6.25rem; min-width: 6.25rem; max-width: 6.75rem"
          :sortable="false"
        >
          <template #body="{ data }">
            <div class="sol-estado">
              <Tag v-if="data.aceito" severity="success" value="Aceito" />
              <Tag v-else severity="warn" value="Pendente" />
            </div>
          </template>
        </Column>

        <Column
          header="Ações"
          columnKey="acoesSolicitacoes"
          style="width: 7rem; min-width: 7rem; max-width: 7rem"
          :reorderableColumn="false"
          :sortable="false"
        >
          <template #body="slotProps">
            <div class="sol-acoes">
              <Button
                v-if="!slotProps.data.aceito"
                type="button"
                icon="pi pi-check"
                text
                severity="success"
                :aria-label="'Aceitar pedido de ' + nomeUtilizador(slotProps.data.usuario)"
                :loading="acaoId === slotProps.data.id && acaoTipo === 'aceitar'"
                :disabled="acaoId != null"
                @click="aceitar(slotProps.data)"
              />
              <Button
                type="button"
                icon="pi pi-trash"
                text
                severity="danger"
                :aria-label="slotProps.data.aceito
                  ? ('Encerrar vínculo e remover pedido de ' + nomeUtilizador(slotProps.data.usuario))
                  : ('Recusar e eliminar pedido de ' + nomeUtilizador(slotProps.data.usuario))"
                :loading="acaoId === slotProps.data.id && acaoTipo === 'excluir'"
                :disabled="acaoId != null"
                @click="excluirPedido(slotProps.data)"
              />
            </div>
          </template>
        </Column>
      </template>
    </BaseDataTable>

    <DialogFiltroSolicitacoesConsultoria
      v-model="visibleFiltro"
      :filtros="filtros"
      @apply="onFiltroApply"
      @clear="onFiltroClear"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import CardStatus from '@/components/CardStatus.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import DialogFiltroSolicitacoesConsultoria from '@/components/DialogFiltroSolicitacoesConsultoria.vue'
import Button from 'primevue/button'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import { getSolicitacoesRecebidasPage, aceitarSolicitacao, recusarSolicitacao } from '@/services/consultoria'
import { useToast } from '@/utils/useToast'

const store = useStore()
const toast = useToast()

const lista = ref([])
const loading = ref(false)
const totalRecords = ref(0)
const currentPage = ref(1)
const first = ref(0)
const filtros = ref({})
const visibleFiltro = ref(false)
const acaoId = ref(null)
const acaoTipo = ref('')

const user = computed(() => store.getters.getUser)

function nomeUtilizador (u) {
  if (!u) return '—'
  const fn = (u.first_name || '').trim()
  const ln = (u.last_name || '').trim()
  const c = [fn, ln].filter(Boolean).join(' ')
  if (c) return c
  return u.username || `ID ${u.id}`
}

function extrairErro (error) {
  const d = error?.response?.data
  if (typeof d?.detail === 'string') return d.detail
  if (Array.isArray(d?.detail)) return d.detail.join(' ')
  return 'Operação falhou. Tente novamente.'
}

const carregarLista = async () => {
  const uid = user.value?.id
  if (!uid) return
  loading.value = true
  try {
    const { data, total } = await getSolicitacoesRecebidasPage(
      uid,
      currentPage.value,
      filtros.value
    )
    lista.value = data
    totalRecords.value = total
  } catch (error) {
    console.error('Erro ao carregar solicitações:', error)
    lista.value = []
    totalRecords.value = 0
    toast.error('Erro', 'Não foi possível carregar as solicitações.')
  } finally {
    loading.value = false
  }
}

function onPage (event) {
  first.value = event.first
  currentPage.value = event.page + 1
  carregarLista()
}

function atualizarLista () {
  carregarLista()
}

function abrirFiltro () {
  visibleFiltro.value = true
}

function onFiltroApply (novosFiltros) {
  filtros.value = novosFiltros || {}
  currentPage.value = 1
  first.value = 0
  carregarLista()
}

function onFiltroClear () {
  filtros.value = {}
  currentPage.value = 1
  first.value = 0
  carregarLista()
}

async function aceitar (row) {
  acaoId.value = row.id
  acaoTipo.value = 'aceitar'
  try {
    await aceitarSolicitacao(row.id)
    toast.success('Consultoria', 'Pedido aceito. A consultoria foi ativada.')
    await store.dispatch('fetchConsultoriaResumo')
    currentPage.value = 1
    first.value = 0
    await carregarLista()
  } catch (e) {
    console.log('[SolicitacoesConsultoriaPage] aceitar', e)
    toast.error('Consultoria', extrairErro(e))
  } finally {
    acaoId.value = null
    acaoTipo.value = ''
  }
}

async function excluirPedido (row) {
  acaoId.value = row.id
  acaoTipo.value = 'excluir'
  try {
    await recusarSolicitacao(row.id)
    toast.success(
      'Consultoria',
      row.aceito
        ? 'Vínculo encerrado e pedido removido.'
        : 'Pedido recusado e removido.'
    )
    await store.dispatch('fetchConsultoriaResumo')
    currentPage.value = 1
    first.value = 0
    await carregarLista()
  } catch (e) {
    console.log('[SolicitacoesConsultoriaPage] excluirPedido', e)
    toast.error('Consultoria', extrairErro(e))
  } finally {
    acaoId.value = null
    acaoTipo.value = ''
  }
}

onMounted(() => {
  carregarLista()
})
</script>

<style scoped>
.table-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}

.table-toolbar .right {
  display: flex;
  gap: 0.5rem;
}

.sol-user {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
}

.sol-user-nome {
  font-weight: 600;
  color: var(--texto-primario);
}

.sol-user-meta {
  font-size: 0.8rem;
  color: var(--texto-secundario);
}

.sol-mensagem {
  white-space: pre-wrap;
  line-height: 1.45;
  color: var(--texto-primario);
}

.sol-estado {
  white-space: nowrap;
}

.sol-estado :deep(.p-tag) {
  font-size: 0.7rem;
  padding: 0.2rem 0.4rem;
}

.sol-acoes {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: flex-start;
  gap: 0.1rem;
  white-space: nowrap;
}

.sol-acoes :deep(.p-button) {
  flex-shrink: 0;
  width: 2.25rem;
  min-width: 2.25rem;
  height: 2.25rem;
  padding: 0;
}

</style>
