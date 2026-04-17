<template>
  <div class="saldo-page">
    <CardStatus
      tituloPrincipal="Saldo"
      subtitulo="Analise entradas, saídas e saldo por período"
      icone="pi pi-chart-line"
      style="margin-bottom: 1rem;"
    />

    <div class="top-grid">
      <div class="filtros-wrapper">
        <h2 class="card-title">Período</h2>
        <p class="card-subtitle">Defina o intervalo de datas para analisar o saldo.</p>

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

        <div class="field">
          <label class="field-label">&nbsp;</label>
          <div class="field-input atalho-input">
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
              label="Últimos 7 dias"
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
              @click="carregarSaldo"
            />
          </div>
        </div>
      </div>

      <div class="consolidados-card">
        <h2 class="card-title">Consolidados mensais</h2>
        <div v-if="loadingConsolidados" class="consolidados-state">
          Carregando consolidados...
        </div>

        <div v-else-if="consolidadosOrdenados.length === 0" class="consolidados-state">
          Nenhum consolidado disponível.
        </div>

        <div v-else class="consolidados-scroll-wrapper" >
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

    <div class="saldo-detalhe">
      <h2 class="section-title">Movimentações no período</h2>

      <BaseDataTable
        :items="movimentos"
        :loading="loading"
        :totalRecords="movimentos.length"
        :first="0"
        :lazy="false"
        :reorderableColumns="false"
      >
        <template #columns>
          <Column
            field="data"
            columnKey="data"
            header="Data"
            style="min-width: 7rem; max-width: 8rem"
          >
            <template #body="{ data }">
              {{ formatarData(data.data) }} ({{ data.diaSemana }})
            </template>
          </Column>
          <Column
            field="tipo"
            columnKey="tipo"
            header="Tipo"
            style="min-width: 6rem; max-width: 7rem"
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
            field="descricao"
            columnKey="descricao"
            header="Descrição"
          />
          <Column
            field="valor"
            columnKey="valor"
            header="Valor"
            style="min-width: 7rem; max-width: 8rem"
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
        </template>
      </BaseDataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/pt-br'
import CardStatus from '@/components/CardStatus.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import Column from 'primevue/column'
import DatePicker from 'primevue/datepicker'
import Button from 'primevue/button'
import Money from '@/utils/Money.js'
import financasService from '@/services/financasService'
import { useToast } from '@/utils/useToast'

const toast = useToast()

dayjs.locale('pt-br')

const hoje = dayjs()

const dataInicial = ref(hoje.startOf('month').toDate())
const dataFinal = ref(hoje.endOf('month').toDate())

const loading = ref(false)
const movimentos = ref([])

const resumo = ref({
  totalEntradas: 0,
  totalSaidas: 0,
  saldoPeriodo: 0
})

const consolidados = ref([])
const loadingConsolidados = ref(false)

const consolidadosOrdenados = computed(() => {
  return [...consolidados.value].sort((a, b) => {
    if (a.ano === b.ano) {
      return b.mes - a.mes
    }
    return b.ano - a.ano
  })
})

function toIsoDate (date) {
  if (!date) return null
  const d = new Date(date)
  if (Number.isNaN(d.getTime())) return null
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
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

/** Agrega todas as páginas da listagem (PAGE_SIZE no backend). */
async function listarMovimentacoesDoPeriodo (ini, fim) {
  const filtros = { data__gte: ini, data__lte: fim }
  const acumulado = []
  let page = 1
  let totalEsperado = Infinity

  while (acumulado.length < totalEsperado) {
    const { data, total } = await financasService.movimentacoes.getPage(page, filtros)
    totalEsperado = total ?? 0
    if (!data?.length) break
    acumulado.push(...data)
    page += 1
  }

  return acumulado
}

async function carregarSaldo () {
  const ini = toIsoDate(dataInicial.value)
  const fim = toIsoDate(dataFinal.value)

  if (!ini || !fim) return

  loading.value = true
  try {
    const arr = await listarMovimentacoesDoPeriodo(ini, fim)
    const lista = (arr || []).map(m => ({
      ...m,
      diaSemana: getDiaSemana(m.data)
    }))

    movimentos.value = lista

    let totalEntradas = 0
    let totalSaidas = 0

    for (const mov of lista) {
      const valor = Number(mov.valor) || 0
      if (mov.tipo === 'E') {
        totalEntradas += valor
      } else if (mov.tipo === 'S') {
        totalSaidas += valor
      }
    }

    resumo.value = {
      totalEntradas,
      totalSaidas,
      saldoPeriodo: totalEntradas - totalSaidas
    }
  } catch (error) {
    console.error('Erro ao carregar saldo:', error)
    movimentos.value = []
    resumo.value = {
      totalEntradas: 0,
      totalSaidas: 0,
      saldoPeriodo: 0
    }
    toast.error('Erro', 'Não foi possível carregar o saldo do período.')
  } finally {
    loading.value = false
  }
}

async function carregarConsolidados () {
  loadingConsolidados.value = true
  try {
    const raw = await financasService.consolidadosMensais.getAll()
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

function setHoje () {
  dataInicial.value = hoje.toDate()
  dataFinal.value = hoje.toDate()
  carregarSaldo()
}

function setMesAtual () {
  dataInicial.value = hoje.startOf('month').toDate()
  dataFinal.value = hoje.endOf('month').toDate()
  carregarSaldo()
}

function setUltimos7Dias () {
  dataInicial.value = hoje.subtract(6, 'day').toDate()
  dataFinal.value = hoje.toDate()
  carregarSaldo()
}

onMounted(() => {
  carregarSaldo()
  carregarConsolidados()
})
</script>

<style scoped>
.saldo-page {
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

.atalho-input {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
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

.saldo-detalhe {
  background: var(--bg-secundario);
  border-radius: 18px;
  padding: 1.25rem 1.5rem;
}

.section-title {
  margin: 0 0 0.75rem 0;
  font-size: 1.1rem;
  color: var(--texto-primario);
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