<template>
    <CardStatus
        tituloPrincipal="Metas"
        subtitulo="Gerencie as suas metas"
        icone="pi pi-bullseye"
        :mostrarAcao="true"
        iconeAcao="pi pi-plus"
        @acao="abrirModalMeta"
        style="margin-bottom: 1rem;"
    />

    <BaseDataTable
      :items="lista"
      :loading="loading"
      :totalRecords="totalRecords"
      :first="first"
      :reorderableColumns="true"
      @page="onPage"
    >
        <template #toolbar>
            <div class="table-toolbar">
                <div class="right">
                    <Button icon="pi pi-refresh" text @click="atualizarLista" label="Atualizar" />
                    <Button icon="pi pi-filter" text @click="abrirFiltro" label="Filtrar" />
                </div>
            </div>
        </template>
        <template #columns>
            <Column field="id" columnKey="id" header="ID" style="min-width: 3rem; max-width: 3rem" sortable />
            <Column field="nome" columnKey="nome" header="Nome" sortable />
            <Column field="valor_meta" columnKey="valor_meta" header="Valor Meta" style="min-width: 7rem; max-width: 7rem" sortable>
                <template #body="{ data }">
                    {{ Money.format(data.valor_meta) }}
                </template>
            </Column>
            <Column field="data_meta" columnKey="data_meta" header="Data Meta" style="min-width: 7rem; max-width: 7rem" sortable>
                <template #body="{ data }">
                    {{ formatarData(data.data_meta) }}
                </template>
            </Column>
            <Column field="prioridade" columnKey="prioridade" header="Prioridade" style="min-width: 7rem; max-width: 7rem" sortable>
                <template #body="{ data }">
                    {{ labelPrioridade(data.prioridade) }}
                </template>
            </Column>
            <Column field="concluida" columnKey="concluida" header="Concluída" style="min-width: 7rem; max-width: 7rem" sortable>
                <template #body="{ data }">
                    <span :class="['meta-status', data.concluida ? 'meta-status--ok' : 'meta-status--pendente']">
                        {{ data.concluida ? 'Sim' : 'Não' }}
                    </span>
                </template>
            </Column>
            <Column header="Ações" columnKey="acoesMetas" style="width: 8rem" :reorderableColumn="false">
                <template #body="slotProps">
                    <Button icon="pi pi-pencil" text @click="editarMeta(slotProps.data)" />
                    <Button icon="pi pi-trash" text severity="danger" @click="deletarMeta(slotProps.data)" />
                </template>
            </Column>
        </template>
    </BaseDataTable>

    <DialogMeta
      v-model:visible="visibleMeta"
      :meta="metaEmEdicao"
      @saved="onMetaSalva"
    />

    <DialogFiltroMetas
      v-model="visibleFiltro"
      @apply="onFiltroApply"
      @clear="onFiltroClear"
    />

    <DialogConfirma
      v-model="visibleExcluir"
      titulo="Excluir meta?"
      mensagem="Esta ação não pode ser desfeita. Deseja realmente excluir esta meta?"
      icone="pi pi-trash"
      tipo="danger"
      labelConfirmar="Excluir"
      labelCancelar="Cancelar"
      iconeConfirmar="pi pi-trash"
      severityConfirmar="danger"
      :loading="excluindo"
      @confirm="executarExclusao"
    />
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import CardStatus from '@/components/CardStatus.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Money from '@/utils/Money.js'
import financasService from '@/services/financasService'
import { useToast } from '@/utils/useToast'
import DialogConfirma from '@/components/DialogConfirma.vue'
import DialogMeta from '@/pages/metas/DialogMeta.vue'
import DialogFiltroMetas from '@/components/DialogFiltroMetas.vue'

const toast = useToast()

const visibleMeta = ref(false)
const visibleExcluir = ref(false)
const visibleFiltro = ref(false)
const metaEmEdicao = ref(null)
const itemParaExcluir = ref(null)
const excluindo = ref(false)

const lista = ref([])
const loading = ref(false)
const totalRecords = ref(0)
const currentPage = ref(1)
const first = ref(0)
const filtros = ref({})

const carregarLista = async () => {
  loading.value = true
  try {
    const { data, total } = await financasService.metas.getPage(currentPage.value, filtros.value)
    lista.value = data
    totalRecords.value = total
  } catch (error) {
    console.error('Erro ao carregar metas:', error)
    lista.value = []
    totalRecords.value = 0
    toast.error('Erro', 'Não foi possível carregar as metas.')
  } finally {
    loading.value = false
  }
}

function onPage(event) {
  first.value = event.first
  currentPage.value = event.page + 1
  carregarLista()
}

function abrirModalMeta() {
  metaEmEdicao.value = null
  visibleMeta.value = true
}

function editarMeta(item) {
  metaEmEdicao.value = item
  visibleMeta.value = true
}

function atualizarLista() {
  carregarLista()
}

function abrirFiltro() {
  visibleFiltro.value = true
}

function onFiltroApply(novosFiltros) {
  filtros.value = novosFiltros || {}
  currentPage.value = 1
  carregarLista()
}

function onFiltroClear() {
  filtros.value = {}
  currentPage.value = 1
  carregarLista()
}

function deletarMeta(item) {
  if (!item?.id) return
  itemParaExcluir.value = item
  visibleExcluir.value = true
}

async function executarExclusao() {
  if (!itemParaExcluir.value?.id) return
  excluindo.value = true
  try {
    await financasService.metas.delete(itemParaExcluir.value.id)
    visibleExcluir.value = false
    itemParaExcluir.value = null
    await carregarLista()
    toast.success('Meta excluída', '')
  } catch (error) {
    console.error('Erro ao excluir meta:', error)
    toast.error('Erro', 'Não foi possível excluir a meta.')
  } finally {
    excluindo.value = false
  }
}

function formatarData(val) {
  if (!val) return '—'
  const d = typeof val === 'string' ? val : (val?.split?.('T')?.[0] ?? '')
  if (!d) return '—'
  const [y, m, day] = d.split('-')
  return [day, m, y].filter(Boolean).join('/')
}

function onMetaSalva() {
  carregarLista()
  toast.success('Meta salva', '')
}

function labelPrioridade(p) {
  if (p === 'R') return 'Rápida'
  if (p === 'M') return 'Média'
  if (p === 'L') return 'Longa'
  return p || '—'
}

watch(visibleMeta, (v) => {
  if (!v) metaEmEdicao.value = null
})

watch(visibleExcluir, (v) => {
  if (!v) itemParaExcluir.value = null
})

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

.meta-status {
  display: inline-flex;
  align-items: center;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
}

.meta-status--ok {
  background: color-mix(in srgb, var(--sucesso) 20%, transparent);
  color: var(--sucesso);
}

.meta-status--pendente {
  background: color-mix(in srgb, var(--perigo) 20%, transparent);
  color: var(--neutro);
}
</style>
