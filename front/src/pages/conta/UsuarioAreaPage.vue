<template>
  <div class="usuario-area">
    <Message
      v-if="modoMonitorVisualizacao"
      severity="info"
      :closable="false"
      class="usuario-area__aviso-monitor"
    >
      Conteúdo desta área reflete a navegação como o utilizador monitorizado; o painel Administrar não está disponível neste modo.
    </Message>
    <CardStatus
      :titulo-principal="titulo"
      :subtitulo="subtitulo"
      :icone="icone"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import CardStatus from '@/components/CardStatus.vue'
import Message from 'primevue/message'

const route = useRoute()
const store = useStore()

const modoMonitorVisualizacao = computed(() => store.getters.subjectViewAdminActive)

const titulo = computed(() => String(route.meta.title ?? 'Conta'))
const subtitulo = computed(() => String(route.meta.subtitulo ?? 'Conteúdo em desenvolvimento.'))
const icone = computed(() => String(route.meta.icone ?? 'pi pi-user'))
</script>

<style scoped>
.usuario-area {
  margin-bottom: 1rem;
}

.usuario-area__aviso-monitor {
  margin-bottom: 0.75rem;
}
</style>
