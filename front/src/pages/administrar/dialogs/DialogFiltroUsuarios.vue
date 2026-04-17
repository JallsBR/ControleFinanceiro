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
        <h2 class="filtro-title">Filtrar utilizadores</h2>
        <p class="filtro-subtitle">
          Critérios de pesquisa e tipo de conta (staff / superuser / comum).
        </p>
      </div>
    </template>

    <div class="filtro-body">
      <div class="field">
        <label class="field-label" for="filtro-usuario-tipo">Tipo de utilizador</label>
        <div class="field-input">
          <Select
            id="filtro-usuario-tipo"
            v-model="tipoUsuario"
            :options="opcoesTipoUsuario"
            optionLabel="label"
            optionValue="value"
            placeholder="Todos"
            class="w-full"
            :showClear="true"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label" for="filtro-usuario-username">Username</label>
        <div class="field-input">
          <InputText
            id="filtro-usuario-username"
            v-model="username"
            class="w-full"
            placeholder="Contém…"
            autocomplete="off"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label" for="filtro-usuario-email">E-mail</label>
        <div class="field-input">
          <InputText
            id="filtro-usuario-email"
            v-model="email"
            type="email"
            class="w-full"
            placeholder="Contém…"
            autocomplete="off"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label" for="filtro-usuario-nome">Nome e sobrenome</label>
        <div class="field-input">
          <InputText
            id="filtro-usuario-nome"
            v-model="nome"
            class="w-full"
            placeholder="Contém no nome completo…"
            autocomplete="off"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label" for="filtro-usuario-assinatura">Assinatura</label>
        <div class="field-input">
          <Select
            id="filtro-usuario-assinatura"
            v-model="assinatura"
            :options="opcoesAssinatura"
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
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Button from 'primevue/button'
import { ASSINATURA_FILTRO_OPCOES } from '../componentes/usuariosAdminMock'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  /** Filtros já aplicados (para reabrir o diálogo com os mesmos valores). */
  filtrosAtivos: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'apply', 'clear'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const username = ref('')
const email = ref('')
const nome = ref('')
const assinatura = ref(null)

const opcoesAssinatura = ASSINATURA_FILTRO_OPCOES

/** Valores enviados à API como `tipo_usuario`. */
const opcoesTipoUsuario = [
  { label: 'Superuser', value: 'superuser' },
  { label: 'Staff', value: 'staff' },
  { label: 'Utilizador comum', value: 'comum' }
]

const tipoUsuario = ref(null)

function sincronizarDoPai () {
  const f = props.filtrosAtivos || {}
  username.value = f.username ?? ''
  email.value = f.email ?? ''
  nome.value = f.nome ?? ''
  assinatura.value = f.assinatura ?? null
  tipoUsuario.value = f.tipoUsuario ?? null
}

watch(
  () => props.modelValue,
  (aberto) => {
    if (aberto) sincronizarDoPai()
  }
)

function onAplicar () {
  const filtros = {}
  const u = username.value.trim()
  const e = email.value.trim()
  const n = nome.value.trim()
  if (u) filtros.username = u
  if (e) filtros.email = e
  if (n) filtros.nome = n
  if (assinatura.value) filtros.assinatura = assinatura.value
  if (tipoUsuario.value) filtros.tipoUsuario = tipoUsuario.value
  emit('apply', filtros)
  visible.value = false
}

function onLimpar () {
  username.value = ''
  email.value = ''
  nome.value = ''
  assinatura.value = null
  tipoUsuario.value = null
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
  margin-bottom: 0.75rem;
}

.field:last-child {
  margin-bottom: 0;
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
