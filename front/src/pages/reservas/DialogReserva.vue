<template>
  <DialogFinancas
    v-model="dialogVisible"
    :titulo="tituloDialog"
    :subtitulo="subtituloDialog"
    :icone="isEdit ? 'pi pi-pencil' : 'pi pi-folder-plus'"
    width="30rem"
  >
    <div class="dialog-form flex flex-column gap-4">
      
      <div class="dialog-form flex flex-column gap-3">

        <!-- LINHA 1 -->
        <div class="field-row">
          <div class="field field-full">
            <label for="nome" class="field-label">Nome</label>
            <div class="field-input">
              <InputText
                id="nome"
                v-model="form.nome"
                class="w-full"
                style="width: 100%;"
                autocomplete="off"
                
              />
            </div>
          </div>
        </div>

        <!-- LINHA 2 -->
        <div class="field-row">
          <div class="field valor-field">
            <label for="valor" class="field-label">Valor</label>
            <div class="field-input">
              <InputGroup class="w-full">
                <InputGroupAddon>R$</InputGroupAddon>
                <InputNumber
                  id="valor"
                  v-model="form.valor"
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

          <div class="field field-ativa">
            <label class="field-label">Ativa</label>
            <div class="field-input">
              <InputSwitch v-model="form.ativa" />
            </div>
          </div>
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
import InputSwitch from 'primevue/inputswitch'
import Button from 'primevue/button'
import financasService from '@/services/financasService'
import { useToast } from '@/utils/useToast'

const toast = useToast()

const props = defineProps({
  visible: { type: Boolean, default: false },
  reserva: { type: Object, default: null }
})

const emit = defineEmits(['update:visible', 'saved'])

const dialogVisible = computed({
  get: () => props.visible,
  set: (v) => emit('update:visible', v)
})

const isEdit = computed(() => !!props.reserva?.id)

const tituloDialog = computed(() =>
  isEdit.value ? 'Editar reserva' : 'Nova reserva'
)
const subtituloDialog = computed(() =>
  isEdit.value
    ? 'Altere os dados da reserva.'
    : 'Cadastre uma nova reserva.'
)

const form = ref({ nome: '', valor: null, ativa: true })

const resetForm = () => {
  form.value = { nome: '', valor: null, ativa: true }
}

watch(() => props.visible, async (visible) => {
  if (!visible) {
    resetForm()
    return
  }
  if (props.reserva?.id) {
    try {
      const d = await financasService.reservas.getById(props.reserva.id)
      form.value = {
        nome: d.nome ?? '',
        valor: Number(d.valor) || null,
        ativa: d.ativa ?? true
      }
    } catch (error) {
      console.error('Erro ao carregar reserva para edição:', error)
      resetForm()
    }
  }
})

async function salvar() {
  const payload = {
    nome: (form.value.nome || '').trim(),
    valor: Number(form.value.valor) || 0,
    ativa: !!form.value.ativa
  }

  try {
    if (props.reserva?.id) {
      await financasService.reservas.update(props.reserva.id, payload)
    } else {
      await financasService.reservas.create(payload)
    }
    dialogVisible.value = false
    emit('saved')
  } catch (error) {
    console.error('Erro ao salvar reserva:', error)
    toast.error('Erro ao salvar', 'Não foi possível salvar a reserva.')
  }
}
</script>

<style scoped>
.dialog-form {
  width: 100%;
}

.field-row {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  width: 100%;
}

.field {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  width: 100%;
  margin-bottom: 1rem;
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

.field-ativa .field-label {
  flex: 0 0 auto;
  min-width: auto;
}

.field-ativa .field-input {
  display: flex;
  align-items: center;
  justify-content: flex-start;
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

