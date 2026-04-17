<template>
  <Dialog
    v-model:visible="visible"
    modal
    :closable="false"
    :dismissableMask="true"
    :closeOnEscape="true"
    :style="{ width: 'min(40rem, 100vw - 2rem)' }"
  >
    <template #header>
      <div class="dialog-header">
        <h2 class="dialog-title">Editar utilizador</h2>
        <p v-if="usuario" class="dialog-subtitle">
          {{ usuario.username }}
        </p>
      </div>
    </template>

    <div v-if="usuario" class="dialog-body">
      <div class="field">
        <label class="field-label" for="usuario-dialog-username">Username</label>
        <div class="field-input">
          <InputText
            id="usuario-dialog-username"
            :model-value="usuario.username"
            class="w-full"
            disabled
            autocomplete="username"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label" for="usuario-dialog-email">E-mail</label>
        <div class="field-input">
          <InputText
            id="usuario-dialog-email"
            v-model="form.email"
            type="email"
            class="w-full"
            autocomplete="email"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label" for="usuario-dialog-first">Nome</label>
        <div class="field-input">
          <InputText
            id="usuario-dialog-first"
            v-model="form.first_name"
            class="w-full"
            autocomplete="given-name"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label" for="usuario-dialog-last">Sobrenome</label>
        <div class="field-input">
          <InputText
            id="usuario-dialog-last"
            v-model="form.last_name"
            class="w-full"
            autocomplete="family-name"
          />
        </div>
      </div>

      <div class="field field--switch">
        <label class="field-label" for="usuario-dialog-staff">Staff</label>
        <div class="field-input field-input--switch">
          <InputSwitch
            id="usuario-dialog-staff"
            v-model="form.is_staff"
          />
        </div>
      </div>

      <div class="field field--switch">
        <label class="field-label" for="usuario-dialog-super">Superuser</label>
        <div class="field-input field-input--switch">
          <InputSwitch
            id="usuario-dialog-super"
            v-model="form.is_superuser"
            :disabled="!podeAlterarSuperuser"
          />
        </div>
      </div>

      <div class="field field--checkbox-row">
        <span class="field-label" id="usuario-dialog-consultor-label">Consultor</span>
        <div class="field-input field-input--checkbox">
          <Checkbox
            v-model="form.is_gerente"
            input-id="usuario-dialog-consultor"
            :binary="true"
            aria-labelledby="usuario-dialog-consultor-label"
          />
          <span class="checkbox-hint">Gerente de contas (consultoria)</span>
        </div>
      </div>

      <div class="field field--multiselect">
        <label class="field-label" for="usuario-dialog-grupos">Grupos</label>
        <div class="field-input">
          <MultiSelect
            id="usuario-dialog-grupos"
            v-model="form.groupIds"
            :options="opcionesGrupos"
            option-label="name"
            option-value="id"
            display="chip"
            filter
            placeholder="Selecionar grupos…"
            class="w-full"
            :loading="loadingGrupos"
            :max-selected-labels="4"
            :show-toggle-all="false"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label" for="usuario-dialog-plano">Assinatura</label>
        <div class="field-input">
          <Select
            id="usuario-dialog-plano"
            v-model="form.plano"
            :options="opcoesAssinatura"
            optionLabel="label"
            optionValue="value"
            class="w-full"
            placeholder="Plano"
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
          @click="fechar"
        />
        <Button
          type="button"
          label="Guardar"
          icon="pi pi-check"
          :loading="loading"
          :disabled="!usuario"
          @click="guardar"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useStore } from 'vuex'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputSwitch from 'primevue/inputswitch'
import Select from 'primevue/select'
import MultiSelect from 'primevue/multiselect'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import { ASSINATURA_FILTRO_OPCOES } from '../componentes/usuariosAdminMock'
import { adminService } from '@/services/adminService'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  /** Linha da tabela (mesmo formato que `mapApiUser`). */
  usuario: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'save', 'cancel'])

const store = useStore()
const podeAlterarSuperuser = computed(() => Boolean(store.state.user?.is_superuser))

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const opcoesAssinatura = ASSINATURA_FILTRO_OPCOES

const opcionesGrupos = ref([])
const loadingGrupos = ref(false)

const form = ref({
  email: '',
  first_name: '',
  last_name: '',
  is_staff: false,
  is_superuser: false,
  is_gerente: false,
  groupIds: [],
  plano: 'comum'
})

function planoInicial (u) {
  const p = u?.assinatura
  return p === 'premium' ? 'premium' : 'comum'
}

function groupIdsInicial (u) {
  if (Array.isArray(u?.group_ids) && u.group_ids.length) {
    return [...u.group_ids].map((x) => Number(x)).filter((n) => !Number.isNaN(n))
  }
  return []
}

function sincronizarFormulario () {
  const u = props.usuario
  if (!u) {
    form.value = {
      email: '',
      first_name: '',
      last_name: '',
      is_staff: false,
      is_superuser: false,
      is_gerente: false,
      groupIds: [],
      plano: 'comum'
    }
    return
  }
  form.value = {
    email: u.email ?? '',
    first_name: u.first_name ?? '',
    last_name: u.last_name ?? '',
    is_staff: Boolean(u.is_staff),
    is_superuser: Boolean(u.is_superuser),
    is_gerente: Boolean(u.is_gerente),
    groupIds: groupIdsInicial(u),
    plano: planoInicial(u)
  }
}

async function carregarOpcoesGrupos () {
  if (!props.modelValue) return
  loadingGrupos.value = true
  try {
    const data = await adminService.getGroupOptions()
    opcionesGrupos.value = Array.isArray(data) ? data : []
  } catch {
    opcionesGrupos.value = []
  } finally {
    loadingGrupos.value = false
  }
}

watch(
  () => [props.modelValue, props.usuario],
  () => {
    if (props.modelValue && props.usuario) {
      sincronizarFormulario()
      carregarOpcoesGrupos()
    }
  },
  { deep: true }
)

function fechar () {
  emit('cancel')
  visible.value = false
}

function guardar () {
  if (!props.usuario) return
  emit('save', {
    id: props.usuario.id,
    email: (form.value.email || '').trim(),
    first_name: (form.value.first_name || '').trim(),
    last_name: (form.value.last_name || '').trim(),
    is_staff: form.value.is_staff,
    is_superuser: form.value.is_superuser,
    is_gerente: Boolean(form.value.is_gerente),
    group_ids: [...(form.value.groupIds || [])],
    plano: form.value.plano
  })
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
  font-size: 0.9rem;
  color: var(--texto-secundario);
}

.dialog-body {
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

.field--switch {
  align-items: center;
}

.field--multiselect {
  align-items: flex-start;
}

.field--checkbox-row {
  align-items: center;
}

.field-input--checkbox {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem 0.75rem;
}

.checkbox-hint {
  font-size: 0.8rem;
  color: var(--texto-secundario);
  line-height: 1.35;
}

.field-label {
  flex: 0 0 120px;
  font-weight: 600;
  color: var(--texto-primario);
  font-size: 0.9rem;
  padding-top: 0.4rem;
  min-width: 120px;
}

.field--switch .field-label {
  padding-top: 0;
}

.field-input {
  flex: 1;
  min-width: 0;
}

.field-input--switch {
  padding-top: 0.15rem;
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
