<template>
  <Dialog
    v-model:visible="modelValue"
    modal
    :closable="false"
    :dismissableMask="true"
    :closeOnEscape="true"
    :style="{ width: '40rem' }"
  >
    <template #header>
      <div class="filtro-header">
        <h2 class="filtro-title">Filtrar investimentos</h2>
        <p class="filtro-subtitle">
          Refine por status, tipo, período e valores.
        </p>
      </div>
    </template>

    <div class="filtro-body">
      <div class="field">
        <label class="field-label">Tipo</label>
        <div class="field-input">
          <Select
            v-model="tipo"
            :options="optionsTipo"
            optionLabel="label"
            optionValue="value"
            placeholder="Todos"
            class="w-full"
            :showClear="true"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label">Status</label>
        <div class="field-input">
          <Select
            v-model="status"
            :options="optionsStatus"
            optionLabel="label"
            optionValue="value"
            placeholder="Todos"
            class="w-full"
            :showClear="true"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label">Aplicação</label>
        <div class="field-input range">
          <DatePicker
            v-model="dataAplicacaoInicial"
            dateFormat="dd/mm/yy"
            placeholder="Data inicial"
            showIcon
          />
          <span class="range-separator">até</span>
          <DatePicker
            v-model="dataAplicacaoFinal"
            dateFormat="dd/mm/yy"
            placeholder="Data final"
            showIcon
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label">Vencimento</label>
        <div class="field-input range">
          <DatePicker
            v-model="dataVencimentoInicial"
            dateFormat="dd/mm/yy"
            placeholder="Data inicial"
            showIcon
          />
          <span class="range-separator">até</span>
          <DatePicker
            v-model="dataVencimentoFinal"
            dateFormat="dd/mm/yy"
            placeholder="Data final"
            showIcon
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label">Valor inicial</label>
        <div class="field-input range">
          <InputNumber
            v-model="valorMin"
            mode="decimal"
            locale="pt-BR"
            :minFractionDigits="2"
            :maxFractionDigits="2"
            placeholder="Mínimo"
            class="w-full"
          />
          <span class="range-separator">até</span>
          <InputNumber
            v-model="valorMax"
            mode="decimal"
            locale="pt-BR"
            :minFractionDigits="2"
            :maxFractionDigits="2"
            placeholder="Máximo"
            class="w-full"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label">Taxa %</label>
        <div class="field-input range">
          <InputNumber
            v-model="taxaMin"
            mode="decimal"
            locale="pt-BR"
            :minFractionDigits="2"
            :maxFractionDigits="2"
            placeholder="Mínima"
            class="w-full"
          />
          <span class="range-separator">até</span>
          <InputNumber
            v-model="taxaMax"
            mode="decimal"
            locale="pt-BR"
            :minFractionDigits="2"
            :maxFractionDigits="2"
            placeholder="Máxima"
            class="w-full"
          />
        </div>
      </div>
    </div>

    <template #footer>
      <div class="filtro-footer">
        <div class="filtro-actions">
          <Button
            type="button"
            label="Limpar"
            icon="pi pi-filter-slash"
            text
            @click="onLimpar"
          />
          <Button
            type="button"
            label="Aplicar"
            icon="pi pi-check"
            @click="onAplicar"
          />
          <Button
            type="button"
            label="Fechar"
            icon="pi pi-times"
            class="btn-fechar"
            severity="danger"
            @click="onFechar"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import Dialog from 'primevue/dialog'
import DatePicker from 'primevue/datepicker'
import Select from 'primevue/select'
import InputNumber from 'primevue/inputnumber'
import Button from 'primevue/button'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'apply', 'clear'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const modelValue = visible

const optionsStatus = [
  { label: 'Todos', value: null },
  { label: 'Apenas ativos', value: 'True' },
  { label: 'Apenas inativos', value: 'False' }
]

const optionsTipo = [
  { label: 'Todos', value: null },
  { label: 'CDB', value: 'CDB' },
  { label: 'Ação', value: 'ACAO' },
  { label: 'Fundo Imobiliário', value: 'FII' },
  { label: 'Criptomoeda', value: 'CRIPTO' },
  { label: 'Tesouro Direto', value: 'TESOURO' },
  { label: 'Outro', value: 'OUTRO' }
]

const status = ref(null)
const tipo = ref(null)
const dataAplicacaoInicial = ref(null)
const dataAplicacaoFinal = ref(null)
const dataVencimentoInicial = ref(null)
const dataVencimentoFinal = ref(null)
const valorMin = ref(null)
const valorMax = ref(null)
const taxaMin = ref(null)
const taxaMax = ref(null)

function toIsoDate (date) {
  if (!date) return null
  const d = new Date(date)
  if (Number.isNaN(d.getTime())) return null
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function onAplicar() {
  const filtros = {}
  if (status.value === 'True' || status.value === 'False') {
    filtros.ativo = status.value
  }
  if (tipo.value) {
    filtros.tipo = tipo.value
  }

  const aplIni = toIsoDate(dataAplicacaoInicial.value)
  const aplFim = toIsoDate(dataAplicacaoFinal.value)
  const venIni = toIsoDate(dataVencimentoInicial.value)
  const venFim = toIsoDate(dataVencimentoFinal.value)

  if (aplIni) filtros['data_aplicacao__gte'] = aplIni
  if (aplFim) filtros['data_aplicacao__lte'] = aplFim
  if (venIni) filtros['data_vencimento__gte'] = venIni
  if (venFim) filtros['data_vencimento__lte'] = venFim

  const vMin = Number(valorMin.value)
  const vMax = Number(valorMax.value)
  const tMin = Number(taxaMin.value)
  const tMax = Number(taxaMax.value)

  if (!Number.isNaN(vMin) && vMin > 0) filtros['valor_inicial__gte'] = vMin
  if (!Number.isNaN(vMax) && vMax > 0) filtros['valor_inicial__lte'] = vMax
  if (!Number.isNaN(tMin) && tMin >= 0) filtros['taxa_rendimento__gte'] = tMin
  if (!Number.isNaN(tMax) && tMax >= 0) filtros['taxa_rendimento__lte'] = tMax
  emit('apply', filtros)
  visible.value = false
}

function onLimpar() {
  status.value = null
  tipo.value = null
  dataAplicacaoInicial.value = null
  dataAplicacaoFinal.value = null
  dataVencimentoInicial.value = null
  dataVencimentoFinal.value = null
  valorMin.value = null
  valorMax.value = null
  taxaMin.value = null
  taxaMax.value = null
  emit('clear')
  visible.value = false
}

function onFechar() {
  visible.value = false
}
</script>

<style scoped>
.filtro-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.filtro-title {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.filtro-subtitle {
  margin: 0;
  font-size: 0.9rem;
  color: #9ca3af;
}

.filtro-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  width: 100%;
  margin-bottom: 0.75rem;
}

.field:last-child {
  margin-bottom: 0;
}

.field-label {
  flex: 0 0 90px;
  font-weight: 600;
  color: #e5e7eb;
  font-size: 0.9rem;
  padding-top: 0.4rem;
  min-width: 90px;
}

.field-input {
  flex: 1;
  min-width: 0;
}

.field-input .w-full {
  width: 100%;
}

.field-input.range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.range-separator {
  color: #9ca3af;
  font-size: 0.85rem;
}

.filtro-footer {
  display: flex;
  justify-content: flex-end;
}

.filtro-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-fechar :deep(.p-button) {
  background: #ff6b6b;
  color: #fff;
}

.btn-fechar :deep(.p-button:hover) {
  background: #ff5252;
  color: #fff;
}
</style>

