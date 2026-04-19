<template>
    <CardStatus
        tituloPrincipal="Investimentos"
        subtitulo="Gerencie os seus investimentos"
        icone="pi pi-chart-line"
        :mostrarAcao="!readOnly"
        iconeAcao="pi pi-plus"
        @acao="abrirModalInvestimento"
        style="margin-bottom: 1rem;"
    />

    <BaseDataTable
      :items="lista"
      :loading="loading"
      :totalRecords="totalRecords"
      :first="first"
      :reorderableColumns="true"
      @page="onPage"
      @sort="onSort"
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
            <Column field="tipo" columnKey="tipo" header="Tipo" style="min-width: 7rem; max-width: 8rem" sortable>
                <template #body="{ data }">
                    {{ labelTipo(data.tipo) }}
                </template>
            </Column>
            <Column field="valor_inicial" columnKey="valor_inicial" header="Valor inicial" style="min-width: 7rem; max-width: 7rem" sortable>
                <template #body="{ data }">
                    {{ Money.format(data.valor_inicial) }}
                </template>
            </Column>
            <Column field="taxa_rendimento" columnKey="taxa_rendimento" header="Taxa %" style="min-width: 6rem; max-width: 6rem" sortable>
                <template #body="{ data }">
                    {{ formatarTaxa(data.taxa_rendimento) }}
                </template>
            </Column>
            <Column field="data_aplicacao" columnKey="data_aplicacao" header="Aplicação" style="min-width: 7rem; max-width: 7rem" sortable>
                <template #body="{ data }">
                    {{ formatarData(data.data_aplicacao) }}
                </template>
            </Column>
            <Column field="data_vencimento" columnKey="data_vencimento" header="Vencimento" style="min-width: 7rem; max-width: 7rem" sortable>
                <template #body="{ data }">
                    {{ formatarData(data.data_vencimento) }}
                </template>
            </Column>
            <Column field="ativo" columnKey="ativo" header="Ativo" style="min-width: 6rem; max-width: 6rem" sortable>
                <template #body="{ data }">
                    <span :class="['invest-status', data.ativo ? 'invest-status--ativo' : 'invest-status--inativo']">
                        {{ data.ativo ? 'Ativo' : 'Inativo' }}
                    </span>
                </template>
            </Column>
            <Column
              v-if="!readOnly"
              header="Ações"
              columnKey="acoesInvestimentos"
              style="width: 8rem"
              :reorderableColumn="false"
            >
                <template #body="slotProps">
                    <Button icon="pi pi-pencil" text @click="editarInvestimento(slotProps.data)" />
                    <Button icon="pi pi-trash" text severity="danger" @click="deletarInvestimento(slotProps.data)" />
                </template>
            </Column>
        </template>
    </BaseDataTable>

    <DialogInvestimento
      v-model:visible="visibleInvestimento"
      :investimento="investimentoEmEdicao"
      @saved="onInvestimentoSalva"
    />

    <DialogConfirma
      v-model="visibleExcluir"
      titulo="Excluir investimento?"
      mensagem="Esta ação não pode ser desfeita. Deseja realmente excluir este investimento?"
      icone="pi pi-trash"
      tipo="danger"
      labelConfirmar="Excluir"
      labelCancelar="Cancelar"
      iconeConfirmar="pi pi-trash"
      severityConfirmar="danger"
      :loading="excluindo"
      @confirm="executarExclusao"
    />

    <DialogFiltroInvestimentos
      v-model="visibleFiltro"
      @apply="onFiltroApply"
      @clear="onFiltroClear"
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
import { useFinancasSubjectReadOnly } from '@/utils/useFinancasSubjectReadOnly'
import { drfOrderingFromPrimeSort } from '@/utils/primeLazySort'
import DialogConfirma from '@/components/DialogConfirma.vue'
import DialogInvestimento from '@/pages/investimentos/DialogInvestimento.vue'
import DialogFiltroInvestimentos from '@/components/DialogFiltroInvestimentos.vue'

const toast = useToast()
const { readOnly } = useFinancasSubjectReadOnly()

const visibleInvestimento = ref(false)
const visibleExcluir = ref(false)
const visibleFiltro = ref(false)
const investimentoEmEdicao = ref(null)
const itemParaExcluir = ref(null)
const excluindo = ref(false)

const lista = ref([])
const loading = ref(false)
const totalRecords = ref(0)
const currentPage = ref(1)
const first = ref(0)
const filtros = ref({})
const ordering = ref(undefined)

const carregarLista = async () => {
  loading.value = true
  try {
    const params = { ...filtros.value }
    if (ordering.value) params.ordering = ordering.value
    const { data, total } = await financasService.investimentos.getPage(currentPage.value, params)
    lista.value = data
    totalRecords.value = total
  } catch (error) {
    console.error('Erro ao carregar investimentos:', error)
    lista.value = []
    totalRecords.value = 0
    toast.error('Erro', 'Não foi possível carregar os investimentos.')
  } finally {
    loading.value = false
  }
}

function onPage(event) {
  first.value = event.first
  currentPage.value = event.page + 1
  carregarLista()
}

function onSort(event) {
  ordering.value = drfOrderingFromPrimeSort(event.sortField, event.sortOrder)
  first.value = 0
  currentPage.value = 1
  carregarLista()
}

function abrirModalInvestimento() {
  if (readOnly.value) return
  investimentoEmEdicao.value = null
  visibleInvestimento.value = true
}

function editarInvestimento(item) {
  if (readOnly.value) return
  investimentoEmEdicao.value = item
  visibleInvestimento.value = true
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
  first.value = 0
  ordering.value = undefined
  carregarLista()
}

function onFiltroClear() {
  filtros.value = {}
  currentPage.value = 1
  first.value = 0
  ordering.value = undefined
  carregarLista()
}

function onInvestimentoSalva() {
  carregarLista()
  toast.success('Investimento salvo', '')
}

function deletarInvestimento(item) {
  if (readOnly.value || !item?.id) return
  itemParaExcluir.value = item
  visibleExcluir.value = true
}

async function executarExclusao() {
  if (readOnly.value || !itemParaExcluir.value?.id) return
  excluindo.value = true
  try {
    await financasService.investimentos.delete(itemParaExcluir.value.id)
    visibleExcluir.value = false
    itemParaExcluir.value = null
    await carregarLista()
    toast.success('Investimento excluído', '')
  } catch (error) {
    console.error('Erro ao excluir investimento:', error)
    toast.error('Erro', 'Não foi possível excluir o investimento.')
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

function formatarTaxa(val) {
  if (val === null || val === undefined || val === '') return '—'
  const num = Number(val)
  if (Number.isNaN(num)) return '—'
  return `${num.toFixed(2)}%`
}

function labelTipo(tipo) {
  if (!tipo) return '—'
  const map = {
    CDB: 'CDB',
    ACAO: 'Ação',
    FII: 'Fundo Imobiliário',
    CRIPTO: 'Criptomoeda',
    TESOURO: 'Tesouro Direto',
    OUTRO: 'Outro'
  }
  return map[tipo] || tipo
}

watch(visibleInvestimento, (v) => {
  if (!v) investimentoEmEdicao.value = null
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

.invest-status {
  display: inline-flex;
  align-items: center;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
}

.invest-status--ativo {
  background: color-mix(in srgb, var(--sucesso) 20%, transparent);
  color: var(--sucesso);
}

.invest-status--inativo {
  background: color-mix(in srgb, var(--perigo) 20%, transparent);
  color: var(--perigo);
}
</style>