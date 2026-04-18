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
        <h2 class="filtro-title">Filtrar conversas</h2>
        <p class="filtro-subtitle">
          Refine a lista por contacto, texto nas mensagens ou apenas favoritas.
        </p>
      </div>
    </template>

    <div class="filtro-body">
      <div class="field">
        <label class="field-label" for="filtro-msg-nome">Contacto</label>
        <div class="field-input">
          <InputText
            id="filtro-msg-nome"
            v-model="draftNome"
            class="w-full"
            placeholder="Nome do contacto"
            autocomplete="off"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label" for="filtro-msg-q">Texto</label>
        <div class="field-input">
          <InputText
            id="filtro-msg-q"
            v-model="draftQ"
            class="w-full"
            placeholder="Procurar no texto…"
            autocomplete="off"
          />
        </div>
      </div>

      <div class="field field--fav">
        <span class="field-label">Opções</span>
        <label class="field-input filtro-msg-fav" for="filtro-msg-fav">
          <Checkbox
            v-model="draftFavorita"
            input-id="filtro-msg-fav"
            :binary="true"
            aria-labelledby="filtro-msg-fav-legenda"
          />
          <span id="filtro-msg-fav-legenda" class="filtro-msg-fav__text">Só favoritas</span>
        </label>
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
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Checkbox from 'primevue/checkbox'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  nome: {
    type: String,
    default: ''
  },
  q: {
    type: String,
    default: ''
  },
  favorita: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'apply', 'clear'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const draftNome = ref('')
const draftQ = ref('')
const draftFavorita = ref(false)

function sincronizarDraft () {
  draftNome.value = props.nome || ''
  draftQ.value = props.q || ''
  draftFavorita.value = props.favorita === true
}

watch(visible, (aberto) => {
  if (aberto) sincronizarDraft()
})

function onAplicar () {
  emit('apply', {
    nome: (draftNome.value || '').trim(),
    q: (draftQ.value || '').trim(),
    favorita: draftFavorita.value === true
  })
  visible.value = false
}

function onLimpar () {
  draftNome.value = ''
  draftQ.value = ''
  draftFavorita.value = false
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
  margin-bottom: 0.75rem;
}

.field:last-child {
  margin-bottom: 0;
}

.field--fav {
  align-items: center;
}

.field-label {
  flex: 0 0 90px;
  font-weight: 600;
  color: var(--texto-primario);
  font-size: 0.9rem;
  padding-top: 0.4rem;
  min-width: 90px;
}

.field--fav .field-label {
  padding-top: 0;
}

.field-input {
  flex: 1;
  min-width: 0;
}

.field-input .w-full {
  width: 100%;
}

.filtro-msg-fav {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin: 0;
  padding-top: 0.35rem;
  cursor: pointer;
  user-select: none;
}

.field--fav .filtro-msg-fav {
  padding-top: 0;
}

.filtro-msg-fav__text {
  font-size: 0.9rem;
  color: var(--texto-primario);
}

.filtro-msg-fav :deep(.p-checkbox) {
  position: relative;
  width: 1.125rem;
  height: 1.125rem;
  flex-shrink: 0;
}

.filtro-msg-fav :deep(.p-checkbox-input) {
  appearance: none;
  -webkit-appearance: none;
  opacity: 0;
  position: absolute;
  inset: 0;
  margin: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
  z-index: 1;
}

.filtro-msg-fav :deep(.p-checkbox-box) {
  width: 1.125rem;
  height: 1.125rem;
  border-radius: 4px;
  border: 1px solid color-mix(in srgb, var(--texto-secundario) 48%, transparent);
  background: var(--bg-secundario);
  box-shadow: none;
}

.filtro-msg-fav :deep(.p-checkbox:not(.p-disabled):hover .p-checkbox-box) {
  border-color: color-mix(in srgb, var(--texto-secundario) 68%, transparent);
}

.filtro-msg-fav :deep(.p-checkbox.p-checkbox-checked .p-checkbox-box) {
  background: var(--sucesso);
  border-color: var(--sucesso);
}

.filtro-msg-fav :deep(.p-checkbox.p-checkbox-checked .p-checkbox-icon) {
  color: #fff;
}

.filtro-msg-fav :deep(.p-checkbox:not(.p-disabled).p-focus .p-checkbox-box) {
  outline: 2px solid color-mix(in srgb, var(--sucesso) 42%, transparent);
  outline-offset: 1px;
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
