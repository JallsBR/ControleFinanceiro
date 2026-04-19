<template>
    <CardStatus
        tituloPrincipal="Metas"
        subtitulo="Gerencie as suas metas"
        icone="pi pi-bullseye"
        :mostrarAcao="!readOnly"
        iconeAcao="pi pi-plus"
        @acao="abrirModalMeta"
        style="margin-bottom: 1rem;"
    />

    <div class="metas-insights-grid">
      <div
        class="meta-reserva-insight"
        role="region"
        :aria-busy="loading"
        aria-labelledby="meta-insight-titulo"
      >
        <div class="meta-reserva-insight__head">
          <i class="pi pi-wallet meta-reserva-insight__icon" aria-hidden="true" />
          <div class="meta-reserva-insight__textwrap">
            <h3 id="meta-insight-titulo" class="meta-reserva-insight__title">
              Reserva vs. Metas
            </h3>
            <p class="meta-reserva-insight__copy">
              Com a reserva atual (<strong>{{ Money.format(reservaAtual, { currency: true }) }}</strong>),
              você atinge
              <strong>{{ percentualReservaNasMetas }}%</strong>
              do valor combinado das metas <strong>desta página</strong>
              (<strong>{{ Money.format(somaValorMetasNaTabela, { currency: true }) }}</strong>).
            </p>
          </div>
        </div>
        <ProgressBar
          :value="percentualReservaNasMetas"
          :showValue="true"
          class="meta-reserva-insight__bar"
        />
      </div>

      <div
        class="meta-reserva-insight meta-reserva-insight--investimento"
        role="region"
        :aria-busy="loading"
        aria-labelledby="meta-investimento-titulo"
      >
        <div class="meta-reserva-insight__head">
          <i class="pi pi-chart-line meta-reserva-insight__icon" aria-hidden="true" />
          <div class="meta-reserva-insight__textwrap">
            <h3 id="meta-investimento-titulo" class="meta-reserva-insight__title">
              Investimento vs. Metas
            </h3>
            <p class="meta-reserva-insight__copy">
              Com o total em investimentos ativos (<strong>{{ Money.format(investimentoAtivoTotal, { currency: true }) }}</strong>),
              você atinge
              <strong>{{ percentualInvestimentoNasMetas }}%</strong>
              do valor combinado das metas <strong>desta página</strong>
              (<strong>{{ Money.format(somaValorMetasNaTabela, { currency: true }) }}</strong>).
            </p>
          </div>
        </div>
        <ProgressBar
          :value="percentualInvestimentoNasMetas"
          :showValue="true"
          class="meta-reserva-insight__bar"
        />
      </div>
    </div>

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
            <Column
              v-if="!readOnly"
              header="Ações"
              columnKey="acoesMetas"
              style="width: 8rem"
              :reorderableColumn="false"
            >
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
import { ref, computed, onMounted, watch } from 'vue'
import CardStatus from '@/components/CardStatus.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import Column from 'primevue/column'
import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'
import Money from '@/utils/Money.js'
import financasService from '@/services/financasService'
import { useToast } from '@/utils/useToast'
import { useFinancasSubjectReadOnly } from '@/utils/useFinancasSubjectReadOnly'
import { drfOrderingFromPrimeSort } from '@/utils/primeLazySort'
import DialogConfirma from '@/components/DialogConfirma.vue'
import DialogMeta from '@/pages/metas/DialogMeta.vue'
import DialogFiltroMetas from '@/components/DialogFiltroMetas.vue'

const toast = useToast()
const { readOnly } = useFinancasSubjectReadOnly()

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
const ordering = ref(undefined)

const reservaAtual = ref(0)
const investimentoAtivoTotal = ref(0)

/** Soma dos `valor_meta` das linhas atualmente na tabela (página atual). */
const somaValorMetasNaTabela = computed(() =>
  lista.value.reduce((acc, m) => acc + (Number(m.valor_meta) || 0), 0)
)

const percentualReservaNasMetas = computed(() => {
  const r = Number(reservaAtual.value) || 0
  const s = Number(somaValorMetasNaTabela.value) || 0
  if (s <= 0) return 0
  return Math.min(100, Math.round((r / s) * 100))
})

const percentualInvestimentoNasMetas = computed(() => {
  const inv = Number(investimentoAtivoTotal.value) || 0
  const s = Number(somaValorMetasNaTabela.value) || 0
  if (s <= 0) return 0
  return Math.min(100, Math.round((inv / s) * 100))
})

/** Soma só reservas ativas (`ativa=true`); inativas não entram no indicador. */
async function carregarReserva () {
  try {
    const ativas = await financasService.reservas.getAllFlat({ ativa: true })
    reservaAtual.value = (ativas || []).reduce(
      (acc, r) => acc + (Number(r.valor) || 0),
      0
    )
  } catch (error) {
    console.error('Erro ao carregar reservas ativas:', error)
    reservaAtual.value = 0
  }
}

/** Soma `valor_inicial` só de investimentos ativos (`ativo=true`). */
async function carregarInvestimentosAtivos () {
  try {
    const ativos = await financasService.investimentos.getAllFlat({ ativo: true })
    investimentoAtivoTotal.value = (ativos || []).reduce(
      (acc, i) => acc + (Number(i.valor_inicial) || 0),
      0
    )
  } catch (error) {
    console.error('Erro ao carregar investimentos ativos:', error)
    investimentoAtivoTotal.value = 0
  }
}

async function carregarIndicadoresPatrimonio () {
  await Promise.all([carregarReserva(), carregarInvestimentosAtivos()])
}

const carregarLista = async () => {
  loading.value = true
  try {
    const params = { ...filtros.value }
    if (ordering.value) params.ordering = ordering.value
    const { data, total } = await financasService.metas.getPage(currentPage.value, params)
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

function onSort(event) {
  ordering.value = drfOrderingFromPrimeSort(event.sortField, event.sortOrder)
  first.value = 0
  currentPage.value = 1
  carregarLista()
}

function abrirModalMeta() {
  if (readOnly.value) return
  metaEmEdicao.value = null
  visibleMeta.value = true
}

function editarMeta(item) {
  if (readOnly.value) return
  metaEmEdicao.value = item
  visibleMeta.value = true
}

function atualizarLista () {
  void Promise.all([carregarLista(), carregarIndicadoresPatrimonio()])
}

function abrirFiltro() {
  visibleFiltro.value = true
}

function onFiltroApply (novosFiltros) {
  filtros.value = novosFiltros || {}
  currentPage.value = 1
  first.value = 0
  ordering.value = undefined
  void carregarLista()
}

function onFiltroClear () {
  filtros.value = {}
  currentPage.value = 1
  first.value = 0
  ordering.value = undefined
  void carregarLista()
}

function deletarMeta(item) {
  if (readOnly.value || !item?.id) return
  itemParaExcluir.value = item
  visibleExcluir.value = true
}

async function executarExclusao() {
  if (readOnly.value || !itemParaExcluir.value?.id) return
  excluindo.value = true
  try {
    await financasService.metas.delete(itemParaExcluir.value.id)
    visibleExcluir.value = false
    itemParaExcluir.value = null
    await Promise.all([carregarLista(), carregarIndicadoresPatrimonio()])
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

function onMetaSalva () {
  void Promise.all([carregarLista(), carregarIndicadoresPatrimonio()])
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
  void Promise.all([carregarLista(), carregarIndicadoresPatrimonio()])
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

.metas-insights-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 1rem;
  align-items: stretch;
  margin-bottom: 1rem;
}

.metas-insights-grid .meta-reserva-insight {
  margin-bottom: 0;
  min-height: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.metas-insights-grid .meta-reserva-insight__bar {
  margin-top: auto;
}

@media (max-width: 768px) {
  .metas-insights-grid {
    grid-template-columns: 1fr;
  }
}

.meta-reserva-insight {
  background: var(--bg-secundario);
  border-radius: 18px;
  padding: 1rem 1.25rem 1.15rem;
  margin-bottom: 1rem;
}

.meta-reserva-insight__head {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.meta-reserva-insight__icon {
  font-size: 1.35rem;
  color: var(--sucesso);
  margin-top: 0.15rem;
  flex-shrink: 0;
}

.meta-reserva-insight__title {
  margin: 0 0 0.35rem 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--texto-primario);
}

.meta-reserva-insight__copy {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.45;
  color: var(--texto-secundario);
}

.meta-reserva-insight__copy strong {
  color: var(--texto-primario);
  font-weight: 600;
}

.meta-reserva-insight__bar {
  width: 100%;
}

.meta-reserva-insight__bar :deep(.p-progressbar) {
  height: 0.65rem;
  border-radius: 999px;
}

.meta-reserva-insight__bar :deep(.p-progressbar-value) {
  border-radius: 999px;
}
</style>
