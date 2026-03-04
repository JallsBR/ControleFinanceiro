<template>
  <Dialog
    v-model:visible="modelValue"
    modal
    :closable="false"
    :dismissableMask="true"
    :closeOnEscape="true"
    :style="{ width: '22rem' }"
  >
    <template #header>
      <div class="filtro-header">
        <h2 class="filtro-title">Filtrar investimentos</h2>
        <p class="filtro-subtitle">
          Selecione o status para refinar a lista.
        </p>
      </div>
    </template>

    <div class="filtro-body">
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

const optionsStatus = [
  { label: 'Todos', value: null },
  { label: 'Apenas ativos', value: 'True' },
  { label: 'Apenas inativos', value: 'False' }
]

const status = ref(null)

function onAplicar() {
  const filtros = {}
  if (status.value === 'True' || status.value === 'False') {
    filtros.ativo = status.value
  }
  emit('apply', filtros)
  visible.value = false
}

function onLimpar() {
  status.value = null
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
  flex-direction: column;
  gap: 0.4rem;
}

.field-label {
  font-weight: 600;
  color: #e5e7eb;
  font-size: 0.9rem;
}

.field-input {
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
  background: #ff6b6b;
  color: #fff;
}

.btn-fechar :deep(.p-button:hover) {
  background: #ff5252;
  color: #fff;
}
</style>

