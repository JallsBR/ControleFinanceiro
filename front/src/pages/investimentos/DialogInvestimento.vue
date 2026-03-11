<template>
  <DialogFinancas
    v-model="dialogVisible"
    :titulo="tituloDialog"
    :subtitulo="subtituloDialog"
    :icone="isEdit ? 'pi pi-pencil' : 'pi pi-chart-line'"
    width="40rem"
  >
    <div class="dialog-form flex flex-column gap-4">
      <div class="field-row">
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
      </div>

      <div class="field-row">
        <div class="field">
          <label for="tipo" class="field-label">Tipo</label>
          <div class="field-input">
            <Select
              id="tipo"
              v-model="form.tipo"
              :options="optionsTipo"
              optionLabel="label"
              optionValue="value"
              placeholder="Selecione"
              class="w-full"
            />
          </div>
        </div>

        <div class="field valor-field">
          <label for="valor_inicial" class="field-label">Valor inicial</label>
          <div class="field-input">
            <InputGroup class="w-full">
              <InputGroupAddon>R$</InputGroupAddon>
              <InputNumber
                id="valor_inicial"
                v-model="form.valor_inicial"
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
      </div>

      <div class="field-row">
        <div class="field">
          <label for="taxa_rendimento" class="field-label">Taxa rendimento % (ano)</label>
          <div class="field-input">
            <InputNumber
              id="taxa_rendimento"
              v-model="form.taxa_rendimento"
              mode="decimal"
              locale="pt-BR"
              :minFractionDigits="2"
              :maxFractionDigits="2"
              :min="0"
              placeholder="Opcional"
              class="w-full"
            />
          </div>
        </div>

        <div class="field">
          <label for="data_aplicacao" class="field-label">Data aplicação</label>
          <div class="field-input">
            <DatePicker
              id="data_aplicacao"
              v-model="form.data_aplicacao"
              dateFormat="dd/mm/yy"
              showIcon
              class="w-full"
            />
          </div>
        </div>
      </div>

      <div class="field-row">
        <div class="field">
          <label for="data_vencimento" class="field-label">Data vencimento</label>
          <div class="field-input">
            <DatePicker
              id="data_vencimento"
              v-model="form.data_vencimento"
              dateFormat="dd/mm/yy"
              showIcon
              class="w-full"
            />
          </div>
        </div>

        <div class="field field-ativo">
          <label class="field-label">Ativo</label>
          <div class="field-input">
            <InputSwitch v-model="form.ativo" />
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
import DatePicker from 'primevue/datepicker'
import Select from 'primevue/select'
import InputSwitch from 'primevue/inputswitch'
import Button from 'primevue/button'
import financasService from '@/services/financasService'
import { useToast } from '@/utils/useToast'

const toast = useToast()

const props = defineProps({
  visible: { type: Boolean, default: false },
  investimento: { type: Object, default: null }
})

const emit = defineEmits(['update:visible', 'saved'])

const dialogVisible = computed({
  get: () => props.visible,
  set: (v) => emit('update:visible', v)
})

const isEdit = computed(() => !!props.investimento?.id)

const tituloDialog = computed(() =>
  isEdit.value ? 'Editar investimento' : 'Novo investimento'
)
const subtituloDialog = computed(() =>
  isEdit.value
    ? 'Altere os dados do investimento.'
    : 'Cadastre um novo investimento.'
)

const form = ref({
  nome: '',
  tipo: null,
  valor_inicial: null,
  taxa_rendimento: null,
  data_aplicacao: new Date(),
  data_vencimento: null,
  ativo: true
})

const optionsTipo = [
  { label: 'CDB', value: 'CDB' },
  { label: 'Ação', value: 'ACAO' },
  { label: 'Fundo Imobiliário', value: 'FII' },
  { label: 'Criptomoeda', value: 'CRIPTO' },
  { label: 'Tesouro Direto', value: 'TESOURO' },
  { label: 'Outro', value: 'OUTRO' }
]

const resetForm = () => {
  form.value = {
    nome: '',
    tipo: null,
    valor_inicial: null,
    taxa_rendimento: null,
    data_aplicacao: new Date(),
    data_vencimento: null,
    ativo: true
  }
}

watch(() => props.visible, async (visible) => {
  if (!visible) {
    resetForm()
    return
  }
  if (props.investimento?.id) {
    try {
      const d = await financasService.investimentos.getById(props.investimento.id)
      form.value = {
        nome: d.nome ?? '',
        tipo: d.tipo ?? null,
        valor_inicial: d.valor_inicial != null ? Number(d.valor_inicial) : null,
        taxa_rendimento: d.taxa_rendimento != null ? Number(d.taxa_rendimento) : null,
        data_aplicacao: d.data_aplicacao ? new Date(d.data_aplicacao) : new Date(),
        data_vencimento: d.data_vencimento ? new Date(d.data_vencimento) : null,
        ativo: d.ativo ?? true
      }
    } catch (error) {
      console.error('Erro ao carregar investimento para edição:', error)
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
    tipo: form.value.tipo,
    valor_inicial: Number(form.value.valor_inicial) || 0,
    taxa_rendimento: form.value.taxa_rendimento != null
      ? Number(form.value.taxa_rendimento)
      : null,
    data_aplicacao: toIsoDate(form.value.data_aplicacao),
    data_vencimento: toIsoDate(form.value.data_vencimento),
    ativo: !!form.value.ativo
  }

  try {
    if (props.investimento?.id) {
      await financasService.investimentos.update(props.investimento.id, payload)
    } else {
      await financasService.investimentos.create(payload)
    }
    dialogVisible.value = false
    emit('saved')
  } catch (error) {
    console.error('Erro ao salvar investimento:', error)
    toast.error('Erro ao salvar', 'Não foi possível salvar o investimento.')
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
  flex: 0 0 110px;
  font-weight: 600;
  color: #ffffff;
  padding-top: 0.5rem;
  min-width: 110px;
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
  background: #e5e7eb;
  color: #374151;
  font-weight: 600;
  min-width: 2.5rem;
}

.valor-input {
  flex: 1;
  min-width: 0;
}

.field-ativo .field-label {
  flex: 0 0 auto;
  min-width: auto;
}

.field-ativo .field-input {
  display: flex;
  align-items: center;
  justify-content: flex-start;
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

