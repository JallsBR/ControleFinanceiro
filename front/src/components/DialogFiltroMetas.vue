<template>
  <Dialog
    v-model:visible="modelValue"
    modal
    :closable="false"
    :dismissableMask="true"
    :closeOnEscape="true"
    :style="{ width: '30rem' }"
  >
    <template #header>
      <div class="filtro-header">
        <h2 class="filtro-title">Filtrar metas</h2>
        <p class="filtro-subtitle">
          Defina período, prioridade e conclusão.
        </p>
      </div>
    </template>

    <div class="filtro-body">
      <div class="field">
        <label class="field-label">Período</label>
        <div class="field-input period">
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
        <label class="field-label">Prioridade</label>
        <div class="field-input">
          <Select
            v-model="prioridade"
            :options="optionsPrioridade"
            optionLabel="label"
            optionValue="value"
            placeholder="Todas"
            class="w-full"
            :showClear="true"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label">Concluída</label>
        <div class="field-input">
          <Select
            v-model="concluida"
            :options="optionsConcluida"
            optionLabel="label"
            optionValue="value"
            placeholder="Todas"
            class="w-full"
            :showClear="true"
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

const dataInicial = ref(null)
const dataFinal = ref(null)
const prioridade = ref(null)
const concluida = ref(null)

const optionsPrioridade = [
  { label: 'Rápida', value: 'R' },
  { label: 'Média', value: 'M' },
  { label: 'Longa', value: 'L' }
]

const optionsConcluida = [
  { label: 'Sim', value: 'True' },
  { label: 'Não', value: 'False' }
]

function toIsoDate(date) {
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
  const ini = toIsoDate(dataInicial.value)
  const fim = toIsoDate(dataFinal.value)

  if (ini) filtros['data_meta__gte'] = ini
  if (fim) filtros['data_meta__lte'] = fim
  if (prioridade.value) filtros.prioridade = prioridade.value
  if (concluida.value === 'True' || concluida.value === 'False') {
    filtros.concluida = concluida.value
  }

  emit('apply', filtros)
  visible.value = false
}

function onLimpar() {
  dataInicial.value = null
  dataFinal.value = null
  prioridade.value = null
  concluida.value = null
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
  font-size: 1.3rem;
  font-weight: 600;
}

.filtro-subtitle {
  margin: 0;
  font-size: 0.9rem;
  color: var(--texto-secundario);
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
  color: var(--texto-primario);
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

.field-input.period {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.period-separator {
  color: var(--texto-secundario);
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
  background: var(--perigo);
  color: var(--texto-primario);
}

.btn-fechar :deep(.p-button:hover) {
  background: color-mix(in srgb, var(--perigo) 85%, black);
  color: var(--texto-primario);
}
</style>

