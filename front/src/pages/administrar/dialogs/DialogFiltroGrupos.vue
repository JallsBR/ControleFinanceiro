<template>
  <Dialog
    v-model:visible="visible"
    modal
    :closable="false"
    :dismissableMask="true"
    :closeOnEscape="true"
    :style="{ width: '28rem' }"
  >
    <template #header>
      <div class="filtro-header">
        <h2 class="filtro-title">Filtrar grupos</h2>
        <p class="filtro-subtitle">Pesquisa pelo nome do grupo.</p>
      </div>
    </template>

    <div class="filtro-body">
      <div class="field">
        <label class="field-label" for="filtro-grupo-nome">Nome</label>
        <div class="field-input">
          <InputText
            id="filtro-grupo-nome"
            v-model="nome"
            class="w-full"
            placeholder="Contém…"
            autocomplete="off"
          />
        </div>
      </div>
    </div>

    <template #footer>
      <div class="filtro-footer">
        <div class="filtro-actions">
          <Button type="button" label="Limpar" icon="pi pi-filter-slash" text @click="onLimpar" />
          <Button type="button" label="Aplicar" icon="pi pi-check" @click="onAplicar" />
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
import Button from 'primevue/button'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  filtrosAtivos: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['update:modelValue', 'apply', 'clear'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const nome = ref('')

function sincronizar () {
  nome.value = props.filtrosAtivos?.nomeGrupo ?? ''
}

watch(
  () => props.modelValue,
  (aberto) => {
    if (aberto) sincronizar()
  }
)

function onAplicar () {
  const filtros = {}
  const n = nome.value.trim()
  if (n) filtros.nomeGrupo = n
  emit('apply', filtros)
  visible.value = false
}

function onLimpar () {
  nome.value = ''
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
  color: var(--texto-primario);
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
}

.field-label {
  flex: 0 0 100px;
  font-weight: 600;
  color: var(--texto-primario);
  font-size: 0.9rem;
  padding-top: 0.4rem;
  min-width: 100px;
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
  flex-wrap: wrap;
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
