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
  store.dispatch('fetchMensagensNaoLidas').catch((e) => {
    console.log('AuthLayout fetchMensagensNaoLidas', e)
  })
})
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  min-height: 100dvh;
  padding-bottom: 60px; /* espaço para o footer fixo */
  box-sizing: border-box;
}

.auth-content {
  padding-bottom: 1rem;
}

@media (max-width: 900px) {
  .auth-layout {
    /* footer + FAB + safe-area */
    padding-bottom: calc(5.5rem + env(safe-area-inset-bottom, 0px));
  }

  .auth-content {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    padding-bottom: 1.5rem;
  }
}
</style>
