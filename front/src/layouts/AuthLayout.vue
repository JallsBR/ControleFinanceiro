<template>
  <div class="auth-layout">
    <BarraNavegacao />
    <br />
    <div class="container mt-4 auth-content">
      <router-view />
    </div>
    <FooterApp />
  </div>
</template>

<script>
import BarraNavegacao from '../components/BarraNavegacao.vue'
import FooterApp from '../components/FooterApp.vue'

export default {
  name: 'AuthLayout',
  components: {
    BarraNavegacao,
    FooterApp
  }
}
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