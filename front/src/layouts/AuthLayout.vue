<template>
  <div class="auth-layout">
    <BarraNavegacao />
    <BannerModoVisualizacao />
    <div class="container mt-4 auth-content">
      <router-view />
    </div>
    <FooterApp />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useStore } from 'vuex'
import BarraNavegacao from '../components/BarraNavegacao.vue'
import BannerModoVisualizacao from '../components/BannerModoVisualizacao.vue'
import FooterApp from '../components/FooterApp.vue'

const store = useStore()

onMounted(() => {
  if (!store.getters.isAuthenticated) return
  store.dispatch('refreshUserProfile').catch((e) => {
    console.log('AuthLayout refreshUserProfile', e)
  })
  store.dispatch('fetchConsultoriaResumo').catch((e) => {
    console.log('AuthLayout fetchConsultoriaResumo', e)
  })
})
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  padding-bottom: 60px; /* espaço para o footer fixo */
}

.auth-content {
  padding-bottom: 1rem;
}
</style>
