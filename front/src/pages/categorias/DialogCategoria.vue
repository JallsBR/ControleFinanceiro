<template>
  <DialogFinancas
    v-model="dialogVisible"
    :titulo="tituloDialog"
    :subtitulo="subtituloDialog"
    :icone="isEdit ? 'pi pi-pencil' : 'pi pi-plus-circle'"
    width="28rem"
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
            placeholder="Nome da categoria"
            :disabled="readOnly"
          />
          <small v-if="errors.nome" class="p-error block">{{ errors.nome }}</small>
        </div>
      </div>
      <div class="field">
        <label for="descricao" class="field-label">Descrição</label>
        <div class="field-input">
          <InputText
            id="descricao"
            v-model="form.descricao"
            class="w-full"
            autocomplete="off"
            placeholder="Opcional"
            :disabled="readOnly"
          />
        </div>
      </div>
      <div class="field">
        <label for="icone" class="field-label">Ícone</label>
        <div class="field-input">
          <Select
            id="icone"
            v-model="form.icone"
            :options="icones"
            optionLabel="nome"
            optionValue="id"
            class="w-full"
            placeholder="Selecione um ícone"
            :showClear="true"
            :disabled="readOnly"
          >
            <template #value="slotProps">
              <div v-if="slotProps.value" class="icone-option">
                <i :class="classeCssPorId(slotProps.value)" class="icone-option__icon" />
                <span>{{ nomeIconePorId(slotProps.value) }}</span>
              </div>
              <span v-else>{{ slotProps.placeholder }}</span>
            </template>
            <template #option="slotProps">
              <div class="icone-option">
                <i :class="slotProps.option.classe_css" class="icone-option__icon" />
                <span>{{ slotProps.option.nome }}</span>
              </div>
            </template>
          </Select>
        </div>
      </div>
    </div>

    <template #actions>
      <Button
        v-if="!readOnly"
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
import { ref, computed, watch, onMounted } from 'vue'
import DialogFinancas from '@/components/DialogFinancas.vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Select from 'primevue/select'
import financasService from '@/services/financasService'
import { useToast } from '@/utils/useToast'
import { useFinancasSubjectReadOnly } from '@/utils/useFinancasSubjectReadOnly'

const toast = useToast()
const { readOnly } = useFinancasSubjectReadOnly()

const props = defineProps({
  visible: { type: Boolean, default: false },
  /** 'E' ou 'S' - define o tipo da categoria ao criar */
  tipo: { type: String, required: true },
  /** Quando preenchido, abre em modo edição */
  categoria: { type: Object, default: null }
})

const emit = defineEmits(['update:visible', 'saved'])

const dialogVisible = computed({
  get: () => props.visible,
  set: (v) => emit('update:visible', v)
})

const isEdit = computed(() => !!props.categoria?.id)

const tituloDialog = computed(() =>
  isEdit.value ? 'Editar categoria' : 'Nova categoria'
)
const subtituloDialog = computed(() =>
  isEdit.value
    ? 'Altere os dados da categoria.'
    : (props.tipo === 'E' ? 'Cadastre uma categoria de entrada.' : 'Cadastre uma categoria de saída.')
)

const form = ref({ nome: '', descricao: '', icone: null })
const errors = ref({ nome: '' })
const icones = ref([])
const iconesMap = ref({})

function resetForm() {
  form.value = { nome: '', descricao: '', icone: null }
  errors.value = { nome: '' }
}

watch(() => props.visible, async (visible) => {
  if (!visible) {
    resetForm()
    return
  }
  if (props.categoria?.id) {
    try {
      const d = await financasService.categorias.getById(props.categoria.id)
      form.value = {
        nome: d.nome ?? '',
        descricao: d.descricao ?? '',
        icone: d.icone ?? null
      }
    } catch (_) {
      resetForm()
    }
  }
})

function validar() {
  errors.value.nome = ''
  const nome = (form.value.nome || '').trim()
  if (!nome) {
    errors.value.nome = 'Informe o nome.'
    return false
  }
  return true
}

async function salvar() {
  if (readOnly.value) return
  if (!validar()) return
  const payload = {
    tipo: props.tipo,
    nome: (form.value.nome || '').trim(),
    descricao: (form.value.descricao || '').trim() || null,
    icone: form.value.icone || null
  }
  try {
    if (props.categoria?.id) {
      await financasService.categorias.update(props.categoria.id, payload)
    } else {
      await financasService.categorias.create(payload)
    }
    dialogVisible.value = false
    emit('saved')
  } catch (error) {
    console.error('Erro ao salvar categoria:', error)
    toast.error('Erro ao salvar', 'Não foi possível salvar a categoria.')
  }
}

async function carregarIcones() {
  try {
    const arr = await financasService.icone.getAllFlat()
    icones.value = arr || []
    iconesMap.value = Object.fromEntries((icones.value || []).map(i => [i.id, i]))
  } catch (error) {
    console.error('Erro ao carregar ícones:', error)
    icones.value = []
    iconesMap.value = {}
  }
}

function classeCssPorId(id) {
  return iconesMap.value[id]?.classe_css || ''
}

function nomeIconePorId(id) {
  return iconesMap.value[id]?.nome || ''
}

onMounted(() => {
  carregarIcones()
})
</script>

<style scoped>
.dialog-form { width: 100%; }
.field {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  width: 100%;
  margin-bottom: 1rem;
}
.field:last-child { margin-bottom: 0; }
.field-label {
  flex: 0 0 80px;
  font-weight: 600;
  color: var(--texto-primario);
  padding-top: 0.5rem;
  min-width: 80px;
}
.field-input { flex: 1; min-width: 0; }
.field-input .w-full { width: 100%; }
.icone-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.icone-option__icon {
  font-size: 1.1rem;
}
.btn-fechar :deep(.p-button) { background: var(--perigo); color: var(--texto-primario); }
.btn-fechar :deep(.p-button:hover) { background: color-mix(in srgb, var(--perigo) 85%, black); color: var(--texto-primario); }
</style>
