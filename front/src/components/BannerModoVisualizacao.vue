<template>
  <div
    v-if="mostrarAlgumModo"
    class="banner-modo-visual"
    role="status"
    aria-live="polite"
  >
    <div class="banner-modo-visual__inner">
      <Tag
        v-if="adminAtivo"
        value="Modo Administrador ativo"
        severity="danger"
        class="modo-tag"
      />
      <template v-else-if="consultorAtivo">
        <Tag
          value="Modo Consultor ativo"
          severity="warn"
          class="modo-tag"
        />

      </template>
    </div>
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

.banner-modo-visual__inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem 0.75rem;
  max-width: 100%;
}

.banner-modo-visual__hint {
  font-size: 0.78rem;
  color: var(--texto-secundario);
  line-height: 1.35;
}

.modo-tag :deep(.p-tag) {
  font-weight: 600;
  font-size: 0.8rem;
  letter-spacing: 0.02em;
}
</style>
