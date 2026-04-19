<template>
  <div class="relatorio-page">
    <CardStatus
      tituloPrincipal="Relatório"
      subtitulo="Analise entradas, saídas e saldo por período"
      icone="pi pi-chart-line"
      style="margin-bottom: 1rem;"
    />

    <div class="top-grid">
      <div class="filtros-wrapper">
        <h2 class="card-title">Período</h2>
        <p class="card-subtitle">Defina o intervalo de datas para analisar o relatório.</p>

        <div class="field">
          <label class="field-label">Datas</label>
          <div class="field-input period-input">
            <DatePicker
              v-model="dataInicial"
              dateFormat="dd/mm/yy"
              placeholder="Data inicial"
              showIcon
            />
            <span class="period-separator">até</span>
            <DatePicker
              v-model="dataFinal"
              dateFormat="dd/mm/yy"
              placeholder="Data final"
              showIcon
            />
          </div>
        </div>

        <hr class="relatorio-periodo-divider" />

        <div class="relatorio-atalhos-linha-full">
          <div class="atalho-input atalho-input--full">
            <Button
              type="button"
              label="Hoje"
              text
              size="small"
              icon="pi pi-calendar"
              @click="setHoje"
            />
            <Button
              type="button"
              label="Este mês"
              text
              size="small"
              icon="pi pi-calendar-times"
              @click="setMesAtual"
            />
            <Button
              type="button"
              label="Última Semana"
              text
              size="small"
              icon="pi pi-history"
              @click="setUltimos7Dias"
            />
            <Button
              type="button"
              label="Aplicar"
              icon="pi pi-check"
              size="small"
              @click="carregarRelatorio"
            />
          </div>
        </div>
      </div>

      <div class="consolidados-card">
        <div class="consolidados-card-header">
          <h2 class="card-title consolidados-card-title">Consolidados mensais</h2>
          <Button
            type="button"
            icon="pi pi-search"
            text
            rounded
            severity="secondary"
            title="Ver todos os consolidados na base de dados"
            aria-label="Análise de todos os consolidados mensais"
            @click="abrirDialogConsolidadosAnalise"
          />
        </div>
        <div v-if="loadingConsolidados" class="consolidados-state">
          Carregando consolidados...
        </div>

        <div v-else-if="consolidadosOrdenados.length === 0" class="consolidados-state">
          Nenhum consolidado disponível.
        </div>

        <div v-else class="consolidados-scroll-wrapper">
          <div class="consolidados-lista" style="padding-right: 15px;">
            <div
              v-for="item in consolidadosOrdenados"
              :key="`${item.ano}-${item.mes}`"
              class="consolidado-linha"
            >
              <div class="consolidado-info">
                <span class="consolidado-mes">
                  {{ formatMesAno(item.ano, item.mes) }}
                </span>
              </div>
              <div class="consolidado-valores">
                <span class="cons-entradas">
                  Entradas: + {{ Money.format(item.total_entradas, { currency: true }) }}
                </span>
                <span class="cons-saidas">
                  Saídas: - {{ Money.format(item.total_saidas, { currency: true }) }}
                </span>
                <span
                  class="cons-saldo"
                  :class="item.total_entradas - item.total_saidas >= 0 ? 'positivo' : 'negativo'"
                >
                  Saldo: {{ Money.format(item.total_entradas - item.total_saidas, { currency: true }) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="resumo-grid">
      <CardStatus
        titulo="Entradas no período"
        :valor="Money.format(resumo.totalEntradas, { currency: true })"
        icone="pi pi-arrow-down-left"
        variante="entrada"
      />
      <CardStatus
        titulo="Saídas no período"
        :valor="Money.format(resumo.totalSaidas, { currency: true })"
        icone="pi pi-arrow-up-right"
        variante="saida"
      />
      <CardStatus
        titulo="Saldo do período"
        :valor="Money.format(resumo.saldoPeriodo, { currency: true })"
        icone="pi pi-chart-line"
        :variante="getVarianteByValor(resumo.saldoPeriodo)"
      />
    </div>

    <div class="relatorio-detalhe">
      <h2 class="section-title">Movimentações no período</h2>

      <BaseDataTable
        :items="movimentosFiltrados"
        :loading="loading"
        :totalRecords="movimentosFiltrados.length"
        :first="0"
        :lazy="false"
        :reorderableColumns="true"
      >
        <template #toolbar>
          <div class="table-toolbar">
            <div class="right">
              <Button icon="pi pi-refresh" text label="Atualizar" @click="atualizarMovimentacoes" />
              <Button icon="pi pi-search" text label="Filtrar" @click="abrirFiltro" />
              <Button
                icon="pi pi-file-pdf"          
                label="Exportar Relatório emPDF"
                :loading="exportingPdf"
                :disabled="exportingPdf"
                @click="exportarPdfRelatorio"
              />
            </div>
          </div>
        </template>
        <template #columns>
          <Column
            field="data"
            columnKey="data"
            header="Data"
            style="min-width: 7rem; max-width: 9rem"
            sortable
          >
            <template #body="{ data }">
              {{ formatarData(data.data) }} ({{ data.diaSemana }})
            </template>
          </Column>
          <Column
            field="tipo"
            columnKey="tipo"
            header="Tipo"
            style="min-width: 3rem; max-width: 4rem"
            sortable
          >
            <template #body="{ data }">
              <span
                class="mov-tipo-tag"
                :class="data.tipo === 'E' ? 'entrada' : 'saida'"
              >
                {{ data.tipo === 'E' ? 'Entrada' : 'Saída' }}
              </span>
            </template>
          </Column>
          <Column
            field="categoria"
            columnKey="categoria"
            header="Categoria"
            style="min-width: 4rem; max-width: 6rem"
            sortable
          >
            <template #body="{ data }">
              <span class="categoria-cell">
                <i
                  v-if="classeIconeCategoria(data.categoria)"
                  :class="classeIconeCategoria(data.categoria)"
                  class="categoria-cell__icon"
                />
                <span>{{ nomeCategoria(data.categoria) }}</span>
              </span>
            </template>
          </Column>
          <Column
            field="descricao"
            columnKey="descricao"
            header="Descrição"
            sortable
          />
          <Column
            field="valor"
            columnKey="valor"
            header="Valor"
            style="min-width: 7rem; max-width: 8rem"
            sortable
          >
            <template #body="{ data }">
              <span
                class="mov-valor"
                :class="data.tipo === 'E' ? 'mov-entrada' : 'mov-saida'"
              >
                {{ data.tipo === 'E' ? '+' : '-' }}
                {{ Money.format(data.valor, { currency: true }) }}
              </span>
            </template>
          </Column>
          <Column
            v-if="!readOnly"
            header="Ações"
            columnKey="acoesRelatorio"
            style="width: 8rem"
            :reorderableColumn="false"
          >
            <template #body="slotProps">
              <Button icon="pi pi-pencil" text @click="editarMovimentacao(slotProps.data)" />
              <Button icon="pi pi-trash" text severity="danger" @click="deletarMovimentacao(slotProps.data)" />
            </template>
          </Column>
        </template>
      </BaseDataTable>

      <div class="relatorio-tabela-totais" aria-live="polite">
        <span class="relatorio-tabela-totais__label">Total da Seleção: </span>
        <span
          class="relatorio-tabela-totais__valor"
          :class="totalLinhasVisiveis >= 0 ? 'positivo' : 'negativo'"
        >
          {{ Money.format(totalLinhasVisiveis, { currency: true }) }}
        </span>
      </div>
    </div>

    <DialogEntradas
      v-model:visible="visibleEntrada"
      :movimentacao="entradaEmEdicao"
      @saved="onMovimentacaoSalva"
    />
    <DialogSaida
      v-model:visible="visibleSaida"
      :movimentacao="saidaEmEdicao"
      @saved="onMovimentacaoSalva"
    />

    <DialogConfirma
      v-model="visibleExcluir"
      :titulo="tituloExcluir"
      :mensagem="mensagemExcluir"
      icone="pi pi-trash"
      tipo="danger"
      labelConfirmar="Excluir"
      labelCancelar="Cancelar"
      iconeConfirmar="pi pi-trash"
      severityConfirmar="danger"
      :loading="excluindo"
      @confirm="executarExclusao"
    />

    <DialogFiltroRelatorioMovimentacoes
      v-model="visibleFiltro"
      @apply="onFiltroApply"
      @clear="onFiltroClear"
    />

    <Dialog
      v-model:visible="visibleConsolidadosAnalise"
      header="Consolidados mensais — análise completa"
      :modal="true"
      :dismissableMask="true"
      :style="{ width: 'min(960px, 96vw)' }"
      class="dialog-consolidados-analise"
      @show="carregarConsolidadosAnaliseTodos"
    >
      <p class="dialog-consolidados-analise__hint">
        Todos os meses registados na base de dados para este utilizador (fora do período do relatório).
      </p>
      <BaseDataTable
        :items="consolidadosAnaliseTodos"
        :loading="loadingConsolidadosAnalise"
        :totalRecords="consolidadosAnaliseTodos.length"
        :first="0"
        :lazy="false"
        :reorderableColumns="true"
        :rows="12"
      >
        <template #columns>
          <Column header="Período" style="min-width: 11rem">
            <template #body="{ data }">
              {{ formatMesAno(data.ano, data.mes) }}
            </template>
          </Column>
          <Column field="ano" header="Ano" sortable style="width: 5rem" />
          <Column field="mes" header="Mês" sortable style="width: 4rem" />
          <Column field="total_entradas" header="Entradas" sortable style="min-width: 8rem">
            <template #body="{ data }">
              <span class="tipo-entrada-tab">{{ Money.format(data.total_entradas, { currency: true }) }}</span>
            </template>
          </Column>
          <Column field="total_saidas" header="Saídas" sortable style="min-width: 8rem">
            <template #body="{ data }">
              <span class="tipo-saida-tab">{{ Money.format(data.total_saidas, { currency: true }) }}</span>
            </template>
          </Column>
          <Column header="Saldo" style="min-width: 8rem">
            <template #body="{ data }">
              <span
                :class="saldoConsolidadoNum(data) >= 0 ? 'tipo-entrada-tab' : 'tipo-saida-tab'"
              >
                {{ Money.format(saldoConsolidadoNum(data), { currency: true }) }}
              </span>
            </template>
          </Column>
        </template>
      </BaseDataTable>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/pt-br'
import CardStatus from '@/components/CardStatus.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import Column from 'primevue/column'
import DatePicker from 'primevue/datepicker'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Money from '@/utils/Money.js'
import financasService from '@/services/financasService'
import { useToast } from '@/utils/useToast'
import { useFinancasSubjectReadOnly } from '@/utils/useFinancasSubjectReadOnly'
import { PAGE_SIZE } from '@/constants/pagination'
import DialogEntradas from '@/pages/home/DialogEntradas.vue'
import DialogSaida from '@/pages/home/DialogSaida.vue'
import DialogConfirma from '@/components/DialogConfirma.vue'
import DialogFiltroRelatorioMovimentacoes from '@/components/DialogFiltroRelatorioMovimentacoes.vue'

const toast = useToast()
const { readOnly } = useFinancasSubjectReadOnly()

dayjs.locale('pt-br')

const hoje = dayjs()

const dataInicial = ref(hoje.startOf('month').toDate())
const dataFinal = ref(hoje.endOf('month').toDate())

const loading = ref(false)
const exportingPdf = ref(false)
/** Lista completa do período (API); filtros aplicam-se no computed. */
const movimentosBrutos = ref([])
const filtrosTabela = ref({
  tipo: null,
  categorias: [],
  descricao: ''
})

const visibleEntrada = ref(false)
const visibleSaida = ref(false)
const visibleExcluir = ref(false)
const visibleFiltro = ref(false)
const entradaEmEdicao = ref(null)
const saidaEmEdicao = ref(null)
const itemParaExcluir = ref(null)
const excluindo = ref(false)

const categoriasMap = ref({})
const iconesMap = ref({})


const consolidados = ref([])
const loadingConsolidados = ref(false)

const visibleConsolidadosAnalise = ref(false)
const consolidadosAnaliseTodos = ref([])
const loadingConsolidadosAnalise = ref(false)

/** Ordem cronológica dentro do período escolhido (mais antigo primeiro). */
const consolidadosOrdenados = computed(() => {
  return [...consolidados.value].sort((a, b) => {
    if (a.ano !== b.ano) return a.ano - b.ano
    return a.mes - b.mes
  })
})

const movimentosFiltrados = computed(() => {
  let list = movimentosBrutos.value
  const f = filtrosTabela.value
  if (f.tipo) {
    list = list.filter(m => m.tipo === f.tipo)
  }
  if (f.categorias?.length) {
    const set = new Set(f.categorias.map(Number))
    list = list.filter(m => set.has(Number(m.categoria)))
  }
  if (f.descricao && String(f.descricao).trim()) {
    const q = String(f.descricao).trim().toLowerCase()
    list = list.filter(m => (m.descricao || '').toLowerCase().includes(q))
  }
  return list
})

/** Resumo alinhado com as linhas visíveis na tabela (e com o PDF quando exportado com os mesmos filtros). */
const resumo = computed(() => {
  let totalEntradas = 0
  let totalSaidas = 0
  for (const mov of movimentosFiltrados.value) {
    const valor = Number(mov.valor) || 0
    if (mov.tipo === 'E') {
      totalEntradas += valor
    } else if (mov.tipo === 'S') {
      totalSaidas += valor
    }
  }
  return {
    totalEntradas,
    totalSaidas,
    saldoPeriodo: totalEntradas - totalSaidas
  }
})

/** Soma algebrica dos valores das linhas atualmente na tabela (entradas +, saídas −). */
const totalLinhasVisiveis = computed(() => {
  let t = 0
  for (const m of movimentosFiltrados.value) {
    const v = Number(m.valor) || 0
    if (m.tipo === 'E') t += v
    else if (m.tipo === 'S') t -= v
  }
  return t
})

const tituloExcluir = computed(() =>
  itemParaExcluir.value?.tipo === 'E' ? 'Excluir entrada?' : 'Excluir saída?'
)

const mensagemExcluir = computed(() =>
  itemParaExcluir.value?.tipo === 'E'
    ? 'Esta ação não pode ser desfeita. Deseja realmente excluir esta entrada?'
    : 'Esta ação não pode ser desfeita. Deseja realmente excluir esta saída?'
)

function toIsoDate (date) {
  if (date == null || date === '') return null
  const d = dayjs(date)
  if (!d.isValid()) return null
  return d.format('YYYY-MM-DD')
}

function formatarData (val) {
  if (!val) return '—'
  const d = typeof val === 'string' ? val : (val?.split?.('T')?.[0] ?? '')
  if (!d) return '—'
  const [y, m, day] = d.split('-')
  return [day, m, y].filter(Boolean).join('/')
}

function getDiaSemana (isoDate) {
  return dayjs(isoDate).format('dddd')
}

function getVarianteByValor (valor) {
  const num = Number(valor || 0)
  if (num > 0) return 'entrada'
  if (num < 0) return 'saida'
  return 'neutro'
}

function formatMesAno (ano, mes) {
  const m = String(mes).padStart(2, '0')
  return dayjs(`${ano}-${m}-01`).format('MMMM [de] YYYY')
}

function saldoConsolidadoNum (row) {
  const e = Number(row?.total_entradas) || 0
  const s = Number(row?.total_saidas) || 0
  return e - s
}

function abrirDialogConsolidadosAnalise () {
  visibleConsolidadosAnalise.value = true
}

async function carregarConsolidadosAnaliseTodos () {
  loadingConsolidadosAnalise.value = true
  try {
    const raw = await financasService.consolidadosMensais.getTodos()
    const arr = Array.isArray(raw) ? raw : (raw?.results || raw?.data || [])
    consolidadosAnaliseTodos.value = arr || []
  } catch (error) {
    console.error('Erro ao carregar consolidados para análise:', error)
    consolidadosAnaliseTodos.value = []
    toast.error('Erro', 'Não foi possível carregar todos os consolidados.')
  } finally {
    loadingConsolidadosAnalise.value = false
  }
}

function nomeCategoria (id) {
  const cat = categoriasMap.value[id]
  return cat?.nome ?? id ?? '—'
}

function classeIconeCategoria (id) {
  const cat = categoriasMap.value[id]
  if (!cat || !cat.icone) return ''
  return iconesMap.value[cat.icone] || ''
}

async function carregarCategoriasEIcones () {
  try {
    const arr = await financasService.categorias.getAllFlat()
    categoriasMap.value = Object.fromEntries((arr || []).map(c => [c.id, c]))
  } catch (_) {
    categoriasMap.value = {}
  }
  try {
    const arr = await financasService.icone.getAllFlat()
    iconesMap.value = Object.fromEntries((arr || []).map(i => [i.id, i.classe_css]))
  } catch (error) {
    console.error('Erro ao carregar ícones:', error)
    iconesMap.value = {}
  }
}

function atualizarMovimentacoes () {
  carregarRelatorio()
}

function abrirFiltro () {
  visibleFiltro.value = true
}

function onFiltroApply (payload) {
  const cats = payload?.categorias
  const categoriasArr = Array.isArray(cats)
    ? cats.map(Number).filter(id => !Number.isNaN(id))
    : []
  filtrosTabela.value = {
    tipo: payload?.tipo ?? null,
    categorias: categoriasArr,
    descricao: payload?.descricao != null ? String(payload.descricao) : ''
  }
}

function onFiltroClear () {
  filtrosTabela.value = { tipo: null, categorias: [], descricao: '' }
}

function editarMovimentacao (item) {
  if (readOnly.value || !item) return
  if (item.tipo === 'E') {
    entradaEmEdicao.value = item
    visibleEntrada.value = true
  } else {
    saidaEmEdicao.value = item
    visibleSaida.value = true
  }
}

function deletarMovimentacao (item) {
  if (readOnly.value || !item?.id) return
  itemParaExcluir.value = item
  visibleExcluir.value = true
}

async function executarExclusao () {
  if (readOnly.value || !itemParaExcluir.value?.id) return
  excluindo.value = true
  try {
    await financasService.movimentacoes.delete(itemParaExcluir.value.id)
    visibleExcluir.value = false
    itemParaExcluir.value = null
    await carregarRelatorio()
    toast.success('Movimentação excluída', '')
  } catch (error) {
    console.error('Erro ao excluir:', error)
    toast.error('Erro', 'Não foi possível excluir a movimentação.')
  } finally {
    excluindo.value = false
  }
}

async function onMovimentacaoSalva () {
  await carregarRelatorio()
}

watch(visibleEntrada, (v) => {
  if (!v) entradaEmEdicao.value = null
})

watch(visibleSaida, (v) => {
  if (!v) saidaEmEdicao.value = null
})

watch(visibleExcluir, (v) => {
  if (!v) itemParaExcluir.value = null
})

/** Agrega todas as páginas da listagem (PAGE_SIZE no backend). */
async function listarMovimentacoesDoPeriodo (ini, fim) {
  const filtros = { data__gte: ini, data__lte: fim }
  const acumulado = []
  let page = 1

  for (;;) {
    const { data, total } = await financasService.movimentacoes.getPage(page, filtros)
    const batch = Array.isArray(data) ? data : []
    if (!batch.length) break
    acumulado.push(...batch)

    const totalRegistros = typeof total === 'number' && !Number.isNaN(total) ? total : null
    if (totalRegistros != null && totalRegistros > 0) {
      if (acumulado.length >= totalRegistros) break
    } else if (batch.length < PAGE_SIZE) {
      break
    }
    page += 1
    if (page > 5000) break
  }

  return acumulado
}

async function carregarRelatorio () {
  const ini = toIsoDate(dataInicial.value)
  const fim = toIsoDate(dataFinal.value)

  if (!ini || !fim) {
    toast.error('Período', 'Defina a data inicial e a data final.')
    consolidados.value = []
    return
  }

  loading.value = true
  try {
    const arr = await listarMovimentacoesDoPeriodo(ini, fim)
    const lista = (arr || []).map(m => ({
      ...m,
      diaSemana: getDiaSemana(m.data)
    }))

    movimentosBrutos.value = lista
  } catch (error) {
    console.error('Erro ao carregar relatório:', error)
    movimentosBrutos.value = []
    toast.error('Erro', 'Não foi possível carregar o relatório do período.')
  } finally {
    loading.value = false
  }
  await carregarConsolidados()
}

async function exportarPdfRelatorio () {
  const ini = toIsoDate(dataInicial.value)
  const fim = toIsoDate(dataFinal.value)
  if (!ini || !fim) {
    toast.error('PDF', 'Defina a data inicial e a data final.')
    return
  }
  exportingPdf.value = true
  try {
    const f = filtrosTabela.value
    const cats = f.categorias?.length
      ? f.categorias.map(Number).filter(id => !Number.isNaN(id)).join(',')
      : undefined
    const desc = f.descricao != null && String(f.descricao).trim()
      ? String(f.descricao).trim()
      : undefined
    const blob = await financasService.relatorios.downloadSaldoPdf({
      dataInicio: ini,
      dataFim: fim,
      tipo: f.tipo || undefined,
      categorias: cats,
      descricao: desc,
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `relatorio-${ini}_${fim}.pdf`
    a.rel = 'noopener'
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
    toast.success('PDF', 'Relatório descarregado.')
  } catch (error) {
    console.error('Erro ao gerar PDF:', error)
    let msg = 'Não foi possível gerar o relatório.'
    const data = error?.response?.data
    if (data instanceof Blob) {
      try {
        const text = await data.text()
        const parsed = JSON.parse(text)
        if (parsed?.detail) msg = typeof parsed.detail === 'string' ? parsed.detail : JSON.stringify(parsed.detail)
      } catch (_) {
        /* ignore */
      }
    } else if (data?.detail) {
      msg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
    }
    toast.error('PDF', msg)
  } finally {
    exportingPdf.value = false
  }
}

async function carregarConsolidados () {
  const ini = toIsoDate(dataInicial.value)
  const fim = toIsoDate(dataFinal.value)
  if (!ini || !fim) {
    consolidados.value = []
    return
  }
  loadingConsolidados.value = true
  try {
    const raw = await financasService.consolidadosMensais.getByPeriod({
      dataInicio: ini,
      dataFim: fim
    })
    const arr = Array.isArray(raw) ? raw : (raw?.results || raw?.data || [])
    consolidados.value = arr || []
  } catch (error) {
    console.error('Erro ao carregar consolidados mensais:', error)
    consolidados.value = []
    toast.error('Erro', 'Não foi possível carregar os consolidados mensais.')
  } finally {
    loadingConsolidados.value = false
  }
}

async function setHoje () {
  dataInicial.value = hoje.toDate()
  dataFinal.value = hoje.toDate()
  await carregarRelatorio()
}

async function setMesAtual () {
  dataInicial.value = hoje.startOf('month').toDate()
  dataFinal.value = hoje.endOf('month').toDate()
  await carregarRelatorio()
}

async function setUltimos7Dias () {
  dataInicial.value = hoje.subtract(6, 'day').toDate()
  dataFinal.value = hoje.toDate()
  await carregarRelatorio()
}

onMounted(async () => {
  await carregarCategoriasEIcones()
  await carregarRelatorio()
})
</script>

<style scoped>
.relatorio-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.top-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(0, 2fr);
  gap: 1.25rem;
  align-items: stretch;
}

.filtros-wrapper,
.consolidados-card {
  background: var(--bg-secundario);
  border-radius: 18px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.consolidados-card {
  min-height: 0;
}

.consolidados-card-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  min-width: 0;
}

.consolidados-card-title {
  margin: 0;
  flex: 1;
  min-width: 0;
}

.card-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--texto-primario);
}

.card-subtitle {
  margin: 0;
  font-size: 0.85rem;
  color: var(--texto-secundario);
}

.field {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  width: 100%;
}

.field-label {
  flex: 0 0 90px;
  font-weight: 600;
  color: var(--texto-primario);
  font-size: 0.9rem;
  padding-top: 0.4rem;
  min-width: 90px;
}

.field-input {
  flex: 1;
  min-width: 0;
}

.period-input {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.period-separator {
  color: var(--texto-secundario);
  font-size: 0.85rem;
}

.relatorio-periodo-divider {
  width: 100%;
  margin: 0;
  border: none;
  border-top: 1px solid color-mix(in srgb, var(--texto-secundario) 22%, transparent);
}

.relatorio-atalhos-linha-full {
  width: 100%;
  box-sizing: border-box;
  padding-top: 0.65rem;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
}

/* Três atalhos de texto partilham o espaço flex; Aplicar só o necessário (mais folga para "Última Semana") */
.atalho-input--full {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(min-content, 1.35fr) max-content;
  gap: 0.35rem 0.4rem;
  width: 100%;
  align-items: center;
}

.atalho-input--full :deep(.p-button) {
  width: 100%;
  min-width: 0;
  min-height: 0;
  box-sizing: border-box;
  justify-content: center;
  font-size: 0.8125rem;
  padding-block: 0.35rem;
  padding-inline: 0.35rem;
}

.atalho-input--full :deep(.p-button:nth-child(-n + 3)) {
  white-space: nowrap;
}

.atalho-input--full :deep(.p-button:last-child) {
  width: auto;
  justify-self: center;
  padding-inline: 0.45rem;
}

.atalho-input--full :deep(.p-button .p-button-icon) {
  font-size: 0.875rem;
}

.consolidados-state {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: var(--texto-secundario);
}

/* Wrapper com scroll: ocupa o espaço restante do card e rola quando necessário */
.consolidados-scroll-wrapper {
  margin-top: 0.25rem;
  padding-right: 5px;
  flex: 1 1 0;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-gutter: stable;
}

.consolidados-scroll-wrapper::-webkit-scrollbar {
  width: 5px;
}

.consolidados-scroll-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.consolidados-scroll-wrapper::-webkit-scrollbar-thumb {
  background: color-mix(in srgb, var(--texto-secundario) 30%, transparent);
  border-radius: 3px;
}

.consolidados-scroll-wrapper::-webkit-scrollbar-thumb:hover {
  background: color-mix(in srgb, var(--texto-secundario) 45%, transparent);
}

.consolidados-lista {
  padding-bottom: 10px;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.consolidado-linha {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  padding: 0.35rem 0;
  border-bottom: 1px solid color-mix(in srgb, var(--texto-secundario) 25%, transparent);
}

.consolidado-linha:last-child {
  border-bottom: none;
}

.consolidado-mes {
  font-weight: 500;
  color: var(--texto-primario);
  text-transform: capitalize;
}

.consolidado-valores {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
}

.cons-entradas {
  color: var(--sucesso);
}

.cons-saidas {
  color: var(--perigo);
}

.cons-saldo {
  font-weight: 600;
}

.cons-saldo.positivo {
  color: var(--sucesso);
}

.cons-saldo.negativo {
  color: var(--perigo);
}

.resumo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1.25rem;
}

.relatorio-detalhe {
  background: var(--bg-secundario);
  border-radius: 18px;
  padding: 1.25rem 1.5rem;
}

.section-title {
  margin: 0 0 0.75rem 0;
  font-size: 1.1rem;
  color: var(--texto-primario);
}

.table-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}

.table-toolbar .right {
  display: flex;
  gap: 0.5rem;
}

.categoria-cell {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.categoria-cell__icon {
  font-size: 1rem;
}

.relatorio-tabela-totais {
  display: flex;
  justify-content: flex-end;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.5rem 0.75rem;
  margin-top: 0.75rem;
  padding-top: 0.65rem;
  border-top: 1px solid color-mix(in srgb, var(--texto-secundario) 18%, transparent);
}

.relatorio-tabela-totais__label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--texto-secundario);
}

.relatorio-tabela-totais__valor {
  font-size: 1.05rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.relatorio-tabela-totais__valor.positivo {
  color: var(--sucesso);
}

.relatorio-tabela-totais__valor.negativo {
  color: var(--perigo);
}

.mov-tipo-tag {
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
}

.mov-tipo-tag.entrada {
  background: color-mix(in srgb, var(--sucesso) 20%, transparent);
  color: var(--sucesso);
}

.mov-tipo-tag.saida {
  background: color-mix(in srgb, var(--perigo) 20%, transparent);
  color: var(--perigo);
}

.mov-valor {
  font-weight: 600;
}

.mov-entrada {
  color: var(--sucesso);
}

.mov-saida {
  color: var(--perigo);
}

@media (max-width: 900px) {
  .top-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>

<style>
/* Dialog pode renderizar fora do scoped (teleport). */
.dialog-consolidados-analise .dialog-consolidados-analise__hint {
  font-size: 0.875rem;
  color: var(--texto-secundario, #6c757d);
  margin: 0 0 1rem 0;
  line-height: 1.4;
}

.dialog-consolidados-analise .tipo-entrada-tab {
  color: var(--sucesso, #198754);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.dialog-consolidados-analise .tipo-saida-tab {
  color: var(--perigo, #dc3545);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
</style>
