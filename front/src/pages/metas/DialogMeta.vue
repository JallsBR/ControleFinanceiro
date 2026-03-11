<template>
  <DialogFinancas
    v-model="dialogVisible"
    :titulo="tituloDialog"
    :subtitulo="subtituloDialog"
    :icone="isEdit ? 'pi pi-pencil' : 'pi pi-bullseye'"
    width="30rem"
  >
    <div class="dialog-form flex flex-column gap-4">
      <div class="field">
        <label for="nome" class="field-label">Nome</label>
        <div class="field-input">
          <InputText
            id="nome"
            v-model="form.nome"
            class="w-full"
            autocomplete="off"
          />
        </div>
      </div>

      <div class="field valor-field">
        <label for="valor" class="field-label">Valor</label>
        <div class="field-input">
          <InputGroup class="w-full">
            <InputGroupAddon>R$</InputGroupAddon>
            <InputNumber
              id="valor"
              v-model="form.valor_meta"
              mode="decimal"
              locale="pt-BR"
              :min="0.01"
              :minFractionDigits="2"
              :maxFractionDigits="2"
              placeholder="0,00"
              class="valor-input"
            />
          </InputGroup>
        </div>
      </div>

      <div class="field">
        <label for="data_meta" class="field-label">Data meta</label>
        <div class="field-input">
          <DatePicker
            id="data_meta"
            v-model="form.data_meta"
            dateFormat="dd/mm/yy"
            showIcon
            class="w-full"
          />
        </div>
      </div>

      <div class="field">
        <label for="prioridade" class="field-label">Prioridade</label>
        <div class="field-input">
          <Select
            id="prioridade"
            v-model="form.prioridade"
            :options="optionsPrioridade"
            optionLabel="label"
            optionValue="value"
            placeholder="Selecione"
            class="w-full"
          />
        </div>
      </div>

      <div class="field">
        <label class="field-label">Concluída</label>
        <div class="field-input">
          <InputSwitch v-model="form.concluida" />
        </div>
      </div>
    </div>

    <template #actions>
      <Button
        type="button"
        label="Salvar"
        icon="pi pi-check"
        @click="salvar"
      />
      <Button
        type="button"
        label="Fechar"
        icon="pi pi-times"
        class="btn-fechar"
        severity="danger"
        @click="dialogVisible = false"
      />
    </template>
  </DialogFinancas>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import DialogFinancas from '@/components/DialogFinancas.vue'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import InputGroup from 'primevue/inputgroup'
import InputGroupAddon from 'primevue/inputgroupaddon'
import DatePicker from 'primevue/datepicker'
import Select from 'primevue/select'
import InputSwitch from 'primevue/inputswitch'
import Button from 'primevue/button'
import financasService from '@/services/financasService'
import { useToast } from '@/utils/useToast'

const toast = useToast()

const props = defineProps({
  visible: { type: Boolean, default: false },
  meta: { type: Object, default: null }
})

const emit = defineEmits(['update:visible', 'saved'])

const dialogVisible = computed({
  get: () => props.visible,
  set: (v) => emit('update:visible', v)
})

const isEdit = computed(() => !!props.meta?.id)

const tituloDialog = computed(() =>
  isEdit.value ? 'Editar meta' : 'Nova meta'
)
const subtituloDialog = computed(() =>
  isEdit.value
    ? 'Altere os dados da meta.'
    : 'Cadastre uma nova meta.'
)

const form = ref({
  nome: '',
  valor_meta: null,
  data_meta: new Date(),
  prioridade: null,
  concluida: false
})

const optionsPrioridade = [
  { label: 'Rápida', value: 'R' },
  { label: 'Média', value: 'M' },
  { label: 'Longa', value: 'L' }
]

const resetForm = () => {
  form.value = {
    nome: '',
    valor_meta: null,
    data_meta: new Date(),
    prioridade: null,
    concluida: false
  }
}

watch(() => props.visible, async (visible) => {
  if (!visible) {
    resetForm()
    return
  }
  if (props.meta?.id) {
    try {
      const d = await financasService.metas.getById(props.meta.id)
      form.value = {
        nome: d.nome ?? '',
        valor_meta: Number(d.valor_meta) || null,
        data_meta: d.data_meta ? new Date(d.data_meta) : new Date(),
        prioridade: d.prioridade ?? null,
        concluida: d.concluida ?? false
      }
    } catch (error) {
      console.error('Erro ao carregar meta para edição:', error)
      resetForm()
    }
  }
})

function toIsoDate(date) {
  if (!date) return null
  const d = new Date(date)
  if (Number.isNaN(d.getTime())) return null
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

async function salvar() {
  const payload = {
    nome: (form.value.nome || '').trim(),
    valor_meta: Number(form.value.valor_meta) || 0,
    data_meta: toIsoDate(form.value.data_meta),
    prioridade: form.value.prioridade,
    concluida: !!form.value.concluida
  }

  try {
    if (props.meta?.id) {
      await financasService.metas.update(props.meta.id, payload)
    } else {
      await financasService.metas.create(payload)
    }
    dialogVisible.value = false
    emit('saved')
  } catch (error) {
    console.error('Erro ao salvar meta:', error)
    toast.error('Erro ao salvar', 'Não foi possível salvar a meta.')
  }
}
</script>

<style scoped>
.dialog-form {
  width: 100%;
}

.field {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  width: 100%;
  margin-bottom: 1rem;
}

.field:last-child {
  margin-bottom: 0;
}

.field-label {
  flex: 0 0 80px;
  font-weight: 600;
  color: var(--texto-primario);
  padding-top: 0.5rem;
  min-width: 80px;
}

.field-input {
  flex: 1;
  min-width: 0;
}

.field-input .w-full {
  width: 100%;
}

.valor-field :deep(.p-inputgroup) {
  width: 100%;
}

.valor-field :deep(.p-inputgroup-addon) {
  background: var(--neutro);
  color: var(--texto-primario);
  font-weight: 600;
  min-width: 2.5rem;
}

.valor-input {
  flex: 1;
  min-width: 0;
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

