<template>
  <Dialog
    v-model:visible="visible"
    modal
    :closable="false"
    :dismissable-mask="true"
    :close-on-escape="true"
    :style="{ width: '28rem' }"
  >
    <template #header>
      <div class="filtro-header">
        <h2 class="filtro-title">Filtrar solicitações</h2>
        <p class="filtro-subtitle">          
        </p>
      </div>
    </template>

    <div class="filtro-body">
      <div class="field">
        <label class="field-label" for="filtro-sol-search">Utilizador</label>
        <div class="field-input">
          <InputText
            id="filtro-sol-search"
            v-model="texto"
            class="w-full"
            type="search"
            placeholder="Username ou e-mail"
            autocomplete="off"
            @keyup.enter="onAplicar"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label" for="filtro-sol-estado">Estado</label>
        <div class="field-input">
          <Select
            id="filtro-sol-estado"
            v-model="estado"
            :options="opcoesEstado"
            optionLabel="label"
            optionValue="value"
            placeholder="Todos"
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
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Button from 'primevue/button'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  /** Filtros ativos na lista (`{ search?: string, estado?: 'pendente'|'aceito' }`). */
  filtros: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'apply', 'clear'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const texto = ref('')
const estado = ref('')

const opcoesEstado = [
  { label: 'Pendente', value: 'pendente' },
  { label: 'Aceito', value: 'aceito' }
]

watch(
  () => props.modelValue,
  (aberto) => {
    if (aberto) {
      texto.value =
        props.filtros?.search != null ? String(props.filtros.search) : ''
      const e = props.filtros?.estado
      estado.value = e === 'pendente' || e === 'aceito' ? e : ''
    }
  }
)

function onAplicar () {
  const search = texto.value.trim()
  const out = {}
  if (search) {
    out.search = search
  }
  if (estado.value === 'pendente' || estado.value === 'aceito') {
    out.estado = estado.value
  }
  emit('apply', out)
  visible.value = false
}

function onLimpar () {
  texto.value = ''
  estado.value = ''
  emit('clear')
  visible.value = false
}

function onFechar () {
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

.btn-fechar :deep(.p-button) {
  background: var(--perigo);
  color: var(--texto-primario);
}

.btn-fechar :deep(.p-button:hover) {
  background: color-mix(in srgb, var(--perigo) 85%, black);
  color: var(--texto-primario);
}
</style>
