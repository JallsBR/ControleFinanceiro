<template>
  <Dialog
    :visible="modelValue"
    modal
    :header="tituloDialog"
    class="dialog-nova-msg"
    :style="{ width: 'min(34rem, 96vw)' }"
    :dismissableMask="true"
    @update:visible="onUpdateVisible"
    @hide="onHide"
  >
    <div class="dialog-nova-msg__body">
      <p v-if="modoResposta" class="dialog-nova-msg__contexto">
        A mensagem será enviada na conversa atual (resposta encadeada).
      </p>
      <div class="dialog-nova-msg__grid">
        <div v-if="!modoResposta" class="field field--full">
          <label for="dnm-dest" class="field-label">Destinatário</label>
          <Dropdown
            id="dnm-dest"
            v-model="form.destino_id"
            class="w-full"
            :options="opcoesDest"
            option-label="label"
            option-value="value"
            placeholder="Selecione o contacto…"
            :filter="opcoesDest.length > 6"
            :loading="loadingDest"
            show-clear
          />
        </div>
        <div class="field field--full mb-0">
          <label for="dnm-msg" class="field-label">Mensagem</label>
          <Textarea
            id="dnm-msg"
            v-model="form.mensagem"
            class="w-full"
            rows="5"
            maxlength="500"
            autoResize
            placeholder="Escreva a sua mensagem…"
          />
        </div>
      </div>
      <p v-if="erroLocal" class="dialog-nova-msg__erro">{{ erroLocal }}</p>
    </div>
    <template #footer>
      <Button type="button" label="Cancelar" severity="secondary" text @click="fechar" />
      <Button
        type="button"
        label="Enviar"
        icon="pi pi-send"
        :loading="enviando"
        :disabled="enviando"
        @click="enviar"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'
import { criarMensagem, getDestinatariosMensagens } from '@/services/mensagens'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  /** Se definido, envia como resposta na thread (sem escolher destinatário). */
  respostaId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'enviada'])

const form = ref({ destino_id: null, mensagem: '' })
const destinatarios = ref([])
const loadingDest = ref(false)
const enviando = ref(false)
const erroLocal = ref('')

const modoResposta = computed(() => props.respostaId != null && Number(props.respostaId) > 0)

const tituloDialog = computed(() =>
  modoResposta.value ? 'Continuar conversa' : 'Nova mensagem'
)

const opcoesDest = computed(() =>
  destinatarios.value.map((u) => ({
    value: u.id,
    label: etiquetaDestinatario(u)
  }))
)

function etiquetaDestinatario (u) {
  if (!u) return '—'
  const fn = (u.first_name || '').trim()
  const ln = (u.last_name || '').trim()
  const nome = [fn, ln].filter(Boolean).join(' ')
  if (nome) return nome
  return u.username || u.email || `ID ${u.id}`
}

watch(
  () => props.modelValue,
  async (aberto) => {
    if (!aberto) return
    erroLocal.value = ''
    if (modoResposta.value) {
      form.value = { destino_id: null, mensagem: '' }
      return
    }
    loadingDest.value = true
    try {
      destinatarios.value = await getDestinatariosMensagens()
    } catch (e) {
      console.error(e)
      destinatarios.value = []
      erroLocal.value = 'Não foi possível carregar os destinatários.'
    } finally {
      loadingDest.value = false
    }
  }
)

function limpar () {
  form.value = { destino_id: null, mensagem: '' }
  erroLocal.value = ''
}

function onHide () {
  limpar()
}

function fechar () {
  emit('update:modelValue', false)
}

function onUpdateVisible (v) {
  emit('update:modelValue', v)
}

function extrairErro (error) {
  const d = error?.response?.data
  if (typeof d?.detail === 'string') return d.detail
  if (d?.destino_id) {
    const x = d.destino_id
    return Array.isArray(x) ? x.join(' ') : String(x)
  }
  if (d?.resposta) {
    const x = d.resposta
    return Array.isArray(x) ? x.join(' ') : String(x)
  }
  if (d?.non_field_errors) {
    const x = d.non_field_errors
    return Array.isArray(x) ? x.join(' ') : String(x)
  }
  return 'Operação falhou. Tente novamente.'
}

async function enviar () {
  erroLocal.value = ''
  const texto = (form.value.mensagem || '').trim()
  if (!texto) {
    erroLocal.value = 'Escreva a mensagem.'
    return
  }
  if (!modoResposta.value && (form.value.destino_id == null || form.value.destino_id === '')) {
    erroLocal.value = 'Selecione um destinatário.'
    return
  }
  enviando.value = true
  try {
    const payload =
      modoResposta.value
        ? {
            resposta: Number(props.respostaId),
            mensagem: texto
          }
        : {
            destino_id: Number(form.value.destino_id),
            mensagem: texto
          }
    const body = await criarMensagem(payload)
    emit('enviada', body)
    emit('update:modelValue', false)
    limpar()
  } catch (e) {
    erroLocal.value = extrairErro(e)
  } finally {
    enviando.value = false
  }
}
</script>

<style scoped>
.dialog-nova-msg__body {
  padding: 0.25rem 0.15rem 0;
}

.dialog-nova-msg__contexto {
  margin: 0 0 1rem;
  font-size: 0.85rem;
  color: var(--texto-secundario);
  line-height: 1.45;
}

.dialog-nova-msg__grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field--full {
  width: 100%;
  min-width: 0;
}

.field-label {
  display: block;
  margin-bottom: 0.4rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--texto-secundario);
}

.w-full {
  width: 100%;
  box-sizing: border-box;
}

.dialog-nova-msg__erro {
  margin: 0.75rem 0 0;
  font-size: 0.85rem;
  color: var(--red-400, #f87171);
}
</style>

<style>
.dialog-nova-msg .p-dialog-content {
  padding-top: 0.5rem;
}
</style>
