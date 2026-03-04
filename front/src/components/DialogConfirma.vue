<template>
  <Dialog
    v-model:visible="modelValue"
    modal
    :closable="false"
    :dismissableMask="false"
    :closeOnEscape="true"
    :style="{ width }"
    @hide="emit('cancel')"
  >
    <!-- HEADER -->
    <template #header>
      <div class="app-dialog__header">
        <div class="app-dialog__icon" :class="iconSeverityClass">
          <i :class="icone"></i>
        </div>
        <div class="app-dialog__titles">
          <h2 class="app-dialog__title">
            {{ titulo }}
          </h2>
          <p v-if="mensagem" class="app-dialog__subtitle">
            {{ mensagem }}
          </p>
        </div>
      </div>
    </template>

    <!-- BODY (conteúdo adicional opcional) -->
    <div v-if="$slots.default" class="app-dialog__body">
      <slot />
    </div>

    <!-- FOOTER -->
    <template #footer>
      <div class="app-dialog__footer">
        <div class="app-dialog__actions">
          <Button
            type="button"
            :label="labelCancelar"
            icon="pi pi-times"
            severity="secondary"
            @click="cancelar"
          />
          <Button
            type="button"
            :label="labelConfirmar"
            :icon="iconeConfirmar"
            :severity="severityConfirmar"
            :loading="loading"
            @click="confirmar"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { computed } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  titulo: {
    type: String,
    default: 'Confirmar'
  },
  mensagem: {
    type: String,
    default: ''
  },
  icone: {
    type: String,
    default: 'pi pi-exclamation-triangle'
  },
  /** 'danger' | 'warn' | 'info' - afeta a cor do ícone no header */
  tipo: {
    type: String,
    default: 'warn'
  },
  labelConfirmar: {
    type: String,
    default: 'Confirmar'
  },
  labelCancelar: {
    type: String,
    default: 'Cancelar'
  },
  iconeConfirmar: {
    type: String,
    default: 'pi pi-check'
  },
  severityConfirmar: {
    type: String,
    default: 'danger'
  },
  width: {
    type: String,
    default: '28rem'
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const modelValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const iconSeverityClass = computed(() => {
  const m = { danger: 'app-dialog__icon--danger', warn: 'app-dialog__icon--warn', info: 'app-dialog__icon--info' }
  return m[props.tipo] || m.warn
})

function confirmar() {
  emit('confirm')
}

function cancelar() {
  modelValue.value = false
  emit('cancel')
}
</script>

<style scoped>
.app-dialog__header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.app-dialog__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e5e7eb;
  border-radius: 8px;
  padding: 0.5rem;
}

.app-dialog__icon i {
  color: #111827;
  font-size: 1.25rem;
}

.app-dialog__icon--warn {
  background: #fef3c7;
}
.app-dialog__icon--warn i {
  color: #b45309;
}

.app-dialog__icon--danger {
  background: #fee2e2;
}
.app-dialog__icon--danger i {
  color: #b91c1c;
}

.app-dialog__icon--info {
  background: #dbeafe;
}
.app-dialog__icon--info i {
  color: #1d4ed8;
}

.app-dialog__titles {
  display: flex;
  flex-direction: column;
}

.app-dialog__title {
  margin: 0;
  font-size: 2.3rem;
  font-weight: 600;
}

.app-dialog__subtitle {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
}

.app-dialog__body {
  padding: 0;
}

.app-dialog__footer {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.75rem;
  width: 100%;
}

.app-dialog__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  width: 100%;
}

/* Container geral do Dialog */
:deep(.p-dialog) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.p-dialog-header) {
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
  padding: 1.25rem 1.5rem;
}

:deep(.p-dialog-content) {
  padding: 1.5rem;
  background: #ffffff;
}

:deep(.p-dialog-footer) {
  border-top: 1px solid #e5e7eb;
  padding: 1rem 1.5rem;
  background: #fafafa;
}

:deep(.p-dialog-mask) {
  backdrop-filter: blur(2px);
  background-color: rgba(0, 0, 0, 0.4);
}
</style>
