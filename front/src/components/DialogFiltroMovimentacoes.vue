<template>
  <Dialog
    v-model:visible="modelValue"
    modal
    :closable="false"
    :dismissableMask="true"
    :closeOnEscape="true"
    :style="{ width: '32rem' }"
  >
    <template #header>
      <div class="filtro-header">
        <h2 class="filtro-title">Filtrar movimentações</h2>
        <p class="filtro-subtitle">
          Defina período e categoria para refinar a lista.
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
        <label class="field-label">Categoria</label>
        <div class="field-input">
          <Select
            v-model="categoria"
            :options="categorias"
            optionLabel="nome"
            optionValue="id"
            placeholder="Todas"
            class="w-full"
            :showClear="true"
          >
            <template #option="slotProps">
              <div class="categoria-option">
                <i
                  v-if="slotProps.option.icone && classeIcone(slotProps.option.icone)"
                  :class="classeIcone(slotProps.option.icone)"
                  class="categoria-option__icon"
                />
                <span>{{ slotProps.option.nome }}</span>
              </div>
            </template>
          </Select>
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
import { ref, computed, watch, onMounted } from 'vue'
import Dialog from 'primevue/dialog'
import DatePicker from 'primevue/datepicker'
import Select from 'primevue/select'
import Button from 'primevue/button'
import financasService from '@/services/financasService'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  /** 'E' ou 'S' */
  tipo: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'apply', 'clear'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const dataInicial = ref(null)
const dataFinal = ref(null)
const categoria = ref(null)
const categorias = ref([])
const iconesMap = ref({})

const modelValue = visible

function resetar() {
  dataInicial.value = null
  dataFinal.value = null
  categoria.value = null
}

watch(visible, (v) => {
  if (!v) return
})

function formatarDataIso(date) {
  if (!date) return null
  const d = new Date(date)
  if (Number.isNaN(d.getTime())) return null
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function onAplicar() {
  const filtros = {}

  const ini = formatarDataIso(dataInicial.value)
  const fim = formatarDataIso(dataFinal.value)

  if (ini) filtros['data__gte'] = ini
  if (fim) filtros['data__lte'] = fim
  if (categoria.value) filtros['categoria'] = categoria.value

  emit('apply', filtros)
  visible.value = false
}

function onLimpar() {
  resetar()
  emit('clear')
  visible.value = false
}

function onFechar() {
  visible.value = false
}

async function carregarCategoriasEIcones() {
  try {
    const data = await financasService.categorias.getAll({ tipo: props.tipo })
    const arr = Array.isArray(data) ? data : (data?.results || data?.data || [])
    categorias.value = arr || []
  } catch (error) {
    console.error('Erro ao carregar categorias para filtro:', error)
    categorias.value = []
  }

  try {
    const arr = await financasService.icone.getAllFlat()
    iconesMap.value = Object.fromEntries((arr || []).map(i => [i.id, i.classe_css]))
  } catch (error) {
    console.error('Erro ao carregar ícones para filtro:', error)
    iconesMap.value = {}
  }
}

function classeIcone(id) {
  return iconesMap.value[id] || ''
}

onMounted(() => {
  carregarCategoriasEIcones()
})
</script>

<style scoped>
.filtro-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.filtro-title {
  margin: 0;
  font-size: 1.4rem;
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

.categoria-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.categoria-option__icon {
  font-size: 1.1rem;
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

