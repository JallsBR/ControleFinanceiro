<template>
  <Dialog
    v-model:visible="visible"
    modal
    :closable="false"
    :dismissableMask="true"
    :closeOnEscape="true"
    :style="{ width: '32rem' }"
  >
    <template #header>
      <div class="filtro-header">
        <h2 class="filtro-title">Filtrar movimentações</h2>
              </div>
    </template>

    <div class="filtro-body">
      <div class="field">
        <label class="field-label">Tipo</label>
        <div class="field-input">
          <Select
            v-model="tipo"
            :options="tipoOpcoes"
            optionLabel="label"
            optionValue="value"
            placeholder="Todas"
            class="w-full"
            :showClear="true"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label">Categorias</label>
        <div class="field-input">
          <MultiSelect
            v-model="categoriasSelecionadas"
            :options="categoriasFiltradas"
            optionLabel="nome"
            optionValue="id"
            display="chip"
            filter
            placeholder="Todas"
            class="w-full"
            :maxSelectedLabels="3"
            :showToggleAll="false"
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
          </MultiSelect>
        </div>
      </div>

      <div class="field">
        <label class="field-label">Descrição</label>
        <div class="field-input">
          <InputText
            v-model="descricao"
            class="w-full"
            placeholder="Contém o texto…"
            autocomplete="off"
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
import { ref, computed, watch, onMounted } from 'vue'
import Dialog from 'primevue/dialog'
import Select from 'primevue/select'
import MultiSelect from 'primevue/multiselect'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import financasService from '@/services/financasService'

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

const tipoOpcoes = [
  { label: 'Todas', value: '' },
  { label: 'Entrada', value: 'E' },
  { label: 'Saída', value: 'S' }
]

const tipo = ref('')
const categoriasSelecionadas = ref([])
const descricao = ref('')
const categorias = ref([])
const iconesMap = ref({})

const categoriasFiltradas = computed(() => {
  const t = tipo.value
  const arr = categorias.value || []
  if (!t) return arr
  return arr.filter(c => c.tipo === t)
})

watch(tipo, () => {
  categoriasSelecionadas.value = []
})

function resetar () {
  tipo.value = ''
  categoriasSelecionadas.value = []
  descricao.value = ''
}

function onAplicar () {
  const d = (descricao.value || '').trim()
  const ids = (categoriasSelecionadas.value || [])
    .map(id => Number(id))
    .filter(id => !Number.isNaN(id))
  emit('apply', {
    tipo: tipo.value || null,
    categorias: ids,
    descricao: d || null
  })
  visible.value = false
}

function onLimpar () {
  resetar()
  emit('clear')
  visible.value = false
}

function onFechar () {
  visible.value = false
}

async function carregarCategoriasEIcones () {
  try {
    const arr = await financasService.categorias.getAllFlat()
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

function classeIcone (id) {
  return iconesMap.value[id] || ''
}

watch(visible, (v) => {
  if (v) return
})

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
