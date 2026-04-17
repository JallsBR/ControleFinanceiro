<template>
  <Dialog
    v-model:visible="visible"
    modal
    :closable="false"
    :dismissableMask="true"
    :closeOnEscape="true"
    :style="{ width: 'min(28rem, 100vw - 2rem)' }"
  >
    <template #header>
      <div class="dialog-header">
        <h2 class="dialog-title">{{ titulo }}</h2>
        <p v-if="grupo" class="dialog-subtitle">ID {{ grupo.id }}</p>
      </div>
    </template>

    <div class="dialog-body">
      <div class="field">
        <label class="field-label" for="grupo-dialog-nome">Nome do grupo</label>
        <div class="field-input">
          <InputText
            id="grupo-dialog-nome"
            v-model="nome"
            class="w-full"
            autocomplete="off"
            :disabled="loading"
          />
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <Button
          type="button"
          label="Cancelar"
          icon="pi pi-times"
          class="btn-cancelar-vermelho"
          severity="danger"
          :disabled="loading"
          @click="fechar"
        />
        <Button
          type="button"
          label="Guardar"
          icon="pi pi-check"
          :loading="loading"
          :disabled="!nome.trim()"
          @click="guardar"
        />
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
  /** null = criar; objeto com id e name = editar */
  grupo: { type: Object, default: null },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'save', 'cancel'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const titulo = computed(() => (props.grupo ? 'Editar grupo' : 'Novo grupo'))

const nome = ref('')

function sincronizar () {
  nome.value = props.grupo?.name ? String(props.grupo.name) : ''
}

watch(
  () => [props.modelValue, props.grupo],
  () => {
    if (props.modelValue) sincronizar()
  },
  { deep: true }
)

function fechar () {
  emit('cancel')
  visible.value = false
}

function guardar () {
  const n = (nome.value || '').trim()
  if (!n) return
  if (props.grupo) {
    emit('save', { id: props.grupo.id, name: n })
  } else {
    emit('save', { name: n })
  }
}
</script>

<style scoped>
.dialog-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.dialog-title {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 600;
  color: var(--texto-primario);
}

.dialog-subtitle {
  margin: 0;
  font-size: 0.85rem;
  color: var(--texto-secundario);
}

.dialog-body {
  padding-top: 0.25rem;
}

.field {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  width: 100%;
}

.field-label {
  flex: 0 0 120px;
  font-weight: 600;
  color: var(--texto-primario);
  font-size: 0.9rem;
  padding-top: 0.4rem;
  min-width: 120px;
}

.field-input {
  flex: 1;
  min-width: 0;
}

.field-input .w-full {
  width: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-cancelar-vermelho :deep(.p-button) {
  background: var(--perigo);
  color: var(--texto-primario);
}

.btn-cancelar-vermelho :deep(.p-button:hover) {
  background: color-mix(in srgb, var(--perigo) 85%, black);
  color: var(--texto-primario);
}
</style>
