<template>
    <BlockUI :blocked="blocked" @block="setSpinnerZIndex" v-bind="$attrs">
        <slot></slot>
        <ProgressSpinner
            v-if="blocked"
            class="flex align-self-center fixed-spinner"
            :style="{ 'z-index': spinnerZIndex }"
            strokeWidth="3"
            style="width: 30px; height: 30px;"
            />
        <div
            v-if="blocked && title"
            class="spinner-title"
            :style="{ 'z-index': spinnerZIndex }"
            >
            {{ title }}
        </div>
    </BlockUI>
</template>

<script>
import BlockUI from 'primevue/blockui';
import ProgressSpinner from 'primevue/progressspinner';

export default {
  // O componente pode ter um nome mais descritivo como BlockWithSpinner ou LoadingOverlay
  name: 'LoadBlock',
  components: { BlockUI, ProgressSpinner },
  props: {
    id: {
      type: String,
      default: null,
    },
    blocked: {
      type: Boolean,
      default: false,
    },
    title: {
        type: String,
        default: null,
    },
    // Opcional: Propriedade para controlar o z-index base do spinner, se necessário
    baseZIndex: {
      type: Number,
      default: 1000 // Um valor alto padrão, caso precise sobrescrever o do BlockUI ou para uso geral
    }
  },
  data() {
    return {
      spinnerZIndex: 0, // Z-index do spinner
    };
  },
  methods: {
    cleanupOverlay() {
      // PrimeVue mantém a div de overlay enquanto o transition roda.
      // Se por algum motivo ela ficar presa, removemos manualmente.
      requestAnimationFrame(() => {
        const overlays = this.$el.querySelectorAll('.p-blockui.p-component-overlay');
        overlays.forEach((overlay) => {
          if (overlay?.parentNode) {
            overlay.parentNode.removeChild(overlay);
          }
        });
      });
    },
    setSpinnerZIndex() {
      // Usamos requestAnimationFrame pra garantir que o DOM esteja atualizado
      // após o BlockUI ter possivelmente aplicado seu z-index.
      // O setTimeout(0) também funcionaria na maioria dos casos, mas RAF é mais semântico pra atualizações visuais.
      requestAnimationFrame(() => {
        const blockUIElement = this.$el.querySelector('.p-blockui');
        if (blockUIElement) {
          // Pega o z-index computado do elemento BlockUI
          const blockUIComputedZIndex = window.getComputedStyle(blockUIElement).zIndex;
          let baseBlockZIndex = parseInt(blockUIComputedZIndex, 10);

          // Se não for um número válido ou for 'auto', usa um fallback ou a prop baseZIndex
          if (isNaN(baseBlockZIndex) || baseBlockZIndex === 'auto') {
            baseBlockZIndex = this.baseZIndex;
          }

          // Define o z-index do spinner um pouco acima do BlockUI pai
          this.spinnerZIndex = baseBlockZIndex + 1;
        } else {
          // Fallback caso não encontre o elemento BlockUI (o que é improvável)
          this.spinnerZIndex = this.baseZIndex + 1;
        }

        if(!this.blocked && this.baseZIndex < 0) {
          this.spinnerZIndex = this.baseZIndex - 1;
        }
      });
    },
  },
  // Opcional: Observar a prop 'blocked' para resetar o z-index ou redefinir
  watch: {
    blocked(newVal) {
      if (newVal) {
        this.setSpinnerZIndex();
      } else {
        this.cleanupOverlay();
      }
    }
  },
  mounted() {
    // Se o componente já nascer blocked
    if (this.blocked) {
      this.setSpinnerZIndex();
    }
  }
};
</script>

<style scoped>
/* Estilo pro ProgressSpinner */
.fixed-spinner {
  position: absolute !important; /* Mantém o spinner fixado em relação ao BlockUI */
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%); /* Centraliza o spinner */
  /* Remove margin-top e margin-left, pois transform é mais preciso */
}
.spinner-title {
  position: absolute;
  top: calc(50% + 25px); /* Ajuste para aparecer abaixo do spinner */
  left: 50%;
  transform: translate(-50%, 0);
  color: var(--texto-primario);
  font-size: 1rem;
  text-align: center;
  pointer-events: none;
}
:deep(.p-blockui.p-component-overlay-leave-active),
:deep(.p-blockui.p-component-overlay-leave-to) {
  pointer-events: none;
}
</style>
