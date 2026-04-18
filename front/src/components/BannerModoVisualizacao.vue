<template>
  <div
    v-if="mostrarAlgumModo"
    class="banner-modo-visual"
    role="status"
    aria-live="polite"
  >
    <Tag
      v-if="adminAtivo"
      value="Modo Administrador ativo"
      severity="danger"
      class="modo-tag"
    />
    <Tag
      v-else-if="consultorAtivo"
      value="Modo Consultor ativo"
      severity="warn"
      class="modo-tag"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'
import Tag from 'primevue/tag'

const store = useStore()

const adminAtivo = computed(() => store.getters.subjectViewAdminActive)
const consultorAtivo = computed(() => store.getters.subjectViewConsultorActive)
const mostrarAlgumModo = computed(() => adminAtivo.value || consultorAtivo.value)
</script>

<style scoped>
.banner-modo-visual {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  width: 100%;
  padding: 0.35rem 1rem 0.45rem;
  box-sizing: border-box;
}

.modo-tag :deep(.p-tag) {
  font-weight: 600;
  font-size: 0.8rem;
  letter-spacing: 0.02em;
}
</style>
