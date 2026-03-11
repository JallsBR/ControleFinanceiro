<template>
    <DialogFinancas
      v-model="dialogVisible"
      :titulo="tituloDialog"
      :subtitulo="subtituloDialog"
      :icone="isEdit ? 'pi pi-pencil' : 'pi pi-minus-circle'"
      width="30rem"
    >
      <div class="dialog-form flex flex-column gap-4">
        <!-- Valor -->
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
            <small v-if="errors.valor" class="p-error block">{{ errors.valor }}</small>
          </div>
        </div>
  
        <!-- Data -->
      <div class="field">
        <label for="data" class="field-label">Data</label>
        <div class="field-input">
          <DatePicker
            id="data"
            v-model="form.data"
            dateFormat="dd/mm/yy"
            showIcon
            class="w-full"
          />
        </div>
      </div>
  
        <!-- Categoria -->
        <div class="field">
          <label for="categoria" class="field-label">Categoria</label>
          <div class="field-input">
            <MultiSelect
              id="categoria"
              v-model="form.categoriasSelecionadas"
              :options="categorias"
              optionLabel="nome"
              optionValue="id"
              :selectionLimit="1"
              display="chip"
              placeholder="Selecione uma categoria"
              class="w-full"
            />
            <small v-if="errors.categoria" class="p-error block">{{ errors.categoria }}</small>
          </div>
        </div>
  
        <!-- Descrição -->
        <div class="field">
          <label for="descricao" class="field-label">Descrição</label>
          <div class="field-input">
            <InputText
              id="descricao"
              v-model="form.descricao"
              class="w-full"
              autocomplete="off"
            />
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
  import { ref, onMounted, computed, watch } from 'vue'
  import DialogFinancas from '@/components/DialogFinancas.vue'
  import InputText from 'primevue/inputtext'
  import InputNumber from 'primevue/inputnumber'
  import InputGroup from 'primevue/inputgroup'
  import InputGroupAddon from 'primevue/inputgroupaddon'
  import DatePicker from 'primevue/datepicker'
  import MultiSelect from 'primevue/multiselect'
  import Button from 'primevue/button'
  import financasService from '@/services/financasService'
  import { useToast } from '@/utils/useToast'
  
  const toast = useToast()
  
  const props = defineProps({
    visible: {
      type: Boolean,
      default: false
    },
    /** Quando preenchido, o dialog abre em modo edição com os dados desta movimentação. */
    movimentacao: {
      type: Object,
      default: null
    }
  })
  
  const emit = defineEmits(['update:visible', 'saved'])
  
  const dialogVisible = computed({
    get: () => props.visible,
    set: (value) => emit('update:visible', value)
  })

  const isEdit = computed(() => !!props.movimentacao?.id)
  const tituloDialog = computed(() =>
    isEdit.value ? 'Editar Saída' : 'Nova Saída'
  )
  const subtituloDialog = computed(() =>
    isEdit.value
      ? 'Altere os dados da movimentação de saída.'
      : 'Cadastre uma nova movimentação de saída.'
  )
  
  const form = ref({
    valor: null,
    data: new Date(),
    categoriasSelecionadas: [],
    descricao: ''
  })
  
  const categorias = ref([])
  const errors = ref({
    valor: '',
    categoria: ''
  })
  
  const resetForm = () => {
    form.value = {
      valor: null,
      data: new Date(),
      categoriasSelecionadas: [],
      descricao: ''
    }
    errors.value = { valor: '', categoria: '' }
  }
  
  watch(() => props.visible, async (isVisible) => {
    if (!isVisible) {
      resetForm()
      return
    }
    if (props.movimentacao?.id) {
      await preencherParaEdicao()
    }
  })

  async function preencherParaEdicao() {
    const m = props.movimentacao
    if (!m?.id) return
    try {
      const dados = await financasService.movimentacoes.getById(m.id)
      form.value = {
        valor: Number(dados.valor) || null,
        data: dados.data ? new Date(dados.data) : new Date(),
        categoriasSelecionadas: dados.categoria ? [dados.categoria] : [],
        descricao: dados.descricao ?? ''
      }
    } catch (error) {
      console.error('Erro ao carregar saída para edição:', error)
      resetForm()
    }
  }
  
  const carregarCategorias = async () => {
    try {
      const data = await financasService.categorias.getAll({ tipo: 'S' })
      categorias.value = Array.isArray(data) ? data : (data?.results || data?.data || [])
    } catch (error) {
      console.error('Erro ao carregar categorias:', error)
      categorias.value = []
    }
  }
  
  const validar = () => {
    errors.value.valor = ''
    errors.value.categoria = ''
  
    const valorNum = Number(form.value.valor || 0)
    if (!valorNum || valorNum <= 0) {
      errors.value.valor = 'O valor deve ser maior que zero.'
    }
  
    if (!form.value.categoriasSelecionadas.length) {
      errors.value.categoria = 'Selecione uma categoria.'
    }
  
    return !errors.value.valor && !errors.value.categoria
  }
  
  const salvar = async () => {
    if (!validar()) return
  
    const payload = {
      tipo: 'S',
      valor: Number(form.value.valor),
      data: form.value.data
        ? new Date(form.value.data).toISOString().split('T')[0]
        : null,
      categoria: form.value.categoriasSelecionadas[0],
      descricao: form.value.descricao
    }
  
    try {
      if (props.movimentacao?.id) {
        await financasService.movimentacoes.update(props.movimentacao.id, payload)
      } else {
        await financasService.movimentacoes.create(payload)
      }
      dialogVisible.value = false
      emit('saved')
    } catch (error) {
      console.error('Erro ao salvar saída:', error)
      toast.error('Erro ao salvar', 'Não foi possível salvar a saída.')
    }
  }
  
  onMounted(() => {
    carregarCategorias()
  })
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
    color: #ffffff;
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
    background: #e5e7eb;
    color: #374151;
    font-weight: 600;
    min-width: 2.5rem;
  }
  
  .valor-input {
    flex: 1;
    min-width: 0;
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