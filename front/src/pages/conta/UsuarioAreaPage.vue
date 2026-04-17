<template>
  <div class="usuario-area">
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
import CardStatus from '@/components/CardStatus.vue'

const route = useRoute()

const titulo = computed(() => String(route.meta.title ?? 'Conta'))
const subtitulo = computed(() => String(route.meta.subtitulo ?? 'Conteúdo em desenvolvimento.'))
const icone = computed(() => String(route.meta.icone ?? 'pi pi-user'))
</script>

<style scoped>
.usuario-area {
  margin-bottom: 1rem;
}
</style>
