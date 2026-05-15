<template>
  <Dialog
    v-model:visible="visible"
    modal
    :closable="false"
    :closeOnEscape="false"
    :dismissableMask="false"
    class="termo-uso-dialog"
    :style="{ width: 'min(720px, 96vw)' }"
  >
    <template #header>
      <div class="termo-uso-dialog__header">
        <h2 class="termo-uso-dialog__title">{{ titulo }}</h2>
        <p v-if="versao" class="termo-uso-dialog__version">Versão {{ versao }}</p>
      </div>
    </template>

    <div v-if="carregando" class="termo-uso-dialog__loading">
      <ProgressSpinner style="width: 48px; height: 48px" />
      <span>Carregando Termo de Uso…</span>
    </div>

    <Message v-else-if="erro" severity="error" :closable="false">
      {{ erro }}
    </Message>

    <template v-else>
      <p class="termo-uso-dialog__instrucao">
        Role até o final do documento para habilitar o aceite.
      </p>
      <div
        ref="scrollArea"
        class="termo-uso-dialog__scroll"
        @scroll="verificarScroll"
      >
        <pre class="termo-uso-dialog__texto">{{ conteudo }}</pre>
      </div>
      <p v-if="!leuAteOFim" class="termo-uso-dialog__hint">
        <i class="pi pi-arrow-down" aria-hidden="true" />
        Continue lendo para liberar o botão de aceite.
      </p>
    </template>

    <template #footer>
      <div class="termo-uso-dialog__footer">
        <Button
          type="button"
          label="Cancelar"
          severity="secondary"
          icon="pi pi-times"
          :disabled="processando"
          @click="cancelar"
        />
        <Button
          type="button"
          label="Li e aceito os Termos de Uso"
          icon="pi pi-check"
          :disabled="!podeAceitar || processando || !!erro"
          :loading="processando"
          @click="confirmar"
        />
      </div>
    </template>
  </Dialog>
</template>

<script>
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import api from '@/services/APIService'

const MARGEM_SCROLL_PX = 24

export default {
  name: 'TermoUsoDialog',
  components: {
    Dialog,
    Button,
    Message,
    ProgressSpinner
  },
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    processando: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'aceito', 'cancelado'],
  data() {
    return {
      carregando: false,
      erro: '',
      titulo: 'Termo de Uso de Serviço',
      versao: '',
      conteudo: '',
      leuAteOFim: false
    }
  },
  computed: {
    visible: {
      get() {
        return this.modelValue
      },
      set(value) {
        this.$emit('update:modelValue', value)
      }
    },
    podeAceitar() {
      return this.leuAteOFim && this.versao && !this.carregando
    }
  },
  watch: {
    modelValue(aberto) {
      if (aberto) {
        this.leuAteOFim = false
        this.carregarTermo()
      }
    }
  },
  methods: {
    async carregarTermo() {
      this.carregando = true
      this.erro = ''
      try {
        const { data } = await api.get('/auth/termos-uso/atual')
        this.titulo = data.titulo || 'Termo de Uso de Serviço'
        this.versao = data.version
        this.conteudo = data.conteudo || ''
        await this.$nextTick()
        this.verificarScroll()
        if (this.conteudoCurto()) {
          this.leuAteOFim = true
        }
      } catch (err) {
        this.erro =
          err.response?.data?.detail ||
          'Não foi possível carregar o Termo de Uso. Tente novamente.'
      } finally {
        this.carregando = false
      }
    },
    conteudoCurto() {
      const el = this.$refs.scrollArea
      if (!el) return false
      return el.scrollHeight <= el.clientHeight + MARGEM_SCROLL_PX
    },
    verificarScroll() {
      const el = this.$refs.scrollArea
      if (!el) return
      const noFim =
        el.scrollTop + el.clientHeight >= el.scrollHeight - MARGEM_SCROLL_PX
      if (noFim) {
        this.leuAteOFim = true
      }
    },
    cancelar() {
      this.visible = false
      this.$emit('cancelado')
    },
    confirmar() {
      if (!this.podeAceitar) return
      this.$emit('aceito', { version: this.versao })
    }
  }
}
</script>

<style scoped>
.termo-uso-dialog__header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.termo-uso-dialog__title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  line-height: 1.35;
}

.termo-uso-dialog__version {
  margin: 0;
  font-size: 0.875rem;
  color: var(--p-text-muted-color);
}

.termo-uso-dialog__instrucao {
  margin: 0 0 0.75rem;
  font-size: 0.9rem;
  color: var(--p-text-muted-color);
}

.termo-uso-dialog__scroll {
  max-height: min(52vh, 420px);
  overflow-y: auto;
  border: 1px solid var(--p-content-border-color);
  border-radius: var(--p-border-radius-md);
  padding: 1rem 1.1rem;
  background: var(--p-content-background);
}

.termo-uso-dialog__texto {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  font-size: 0.875rem;
  line-height: 1.55;
  color: var(--p-text-color);
}

.termo-uso-dialog__hint {
  margin: 0.75rem 0 0;
  font-size: 0.85rem;
  color: var(--p-primary-color);
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.termo-uso-dialog__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem 1rem;
  color: var(--p-text-muted-color);
}

.termo-uso-dialog__footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.5rem;
}
</style>
