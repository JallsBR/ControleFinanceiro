<template>
  <div class="signin-page">
    <Card class="signin-card" style="width: 600px;">
      <template #content>
        <div class="signin-header">
          <div class="logo-container">
            <img src="/logoFinancasApp.png" alt="Logo Financas" class="logo-img" />
            <h2 class="brand-title">Finanças <span>APP</span></h2>
          </div>
        </div>

        <Message v-if="erro" severity="error" :closable="false" class="signin-error">
          {{ erro }}
        </Message>
        <Message v-else severity="info" :closable="false" class="signin-mobile-notice">
          {{ mensagem }}
        </Message>

        <Button
          v-if="erro"
          label="Ir para o login"
          class="w-full"
          @click="$router.push({ name: 'signin' })"
        />
      </template>
    </Card>
  </div>
</template>

<script>
import Card from 'primevue/card'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { routeLocationAfterLogin } from '@/utils/postLoginRoute'

export default {
  name: 'TwoFactorLinkPage',
  components: { Card, Button, Message },
  data () {
    return {
      mensagem: 'Concluindo autenticação…',
      erro: null
    }
  },
  async mounted () {
    const challengeId = (this.$route.query.c || '').toString().trim()
    const linkToken = (this.$route.query.t || '').toString().trim()

    if (!challengeId || !linkToken) {
      this.erro = 'Link inválido ou incompleto. Faça login novamente.'
      return
    }

    if (this.$store.getters.isAuthenticated) {
      this.$router.replace(routeLocationAfterLogin(this.$store.getters.getUser))
      return
    }

    const ok = await this.$store.dispatch('verifyTwoFactor', {
      challenge_id: challengeId,
      link_token: linkToken
    })

    if (ok) {
      this.mensagem = 'Login concluído. Redirecionando…'
      const u = this.$store.getters.getUser
      this.$router.replace(routeLocationAfterLogin(u))
      return
    }

    this.erro =
      'Não foi possível autenticar com este link. Ele pode ter expirado ou já ter sido usado.'
  }
}
</script>

<style scoped>
.signin-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  background: var(--bg-primario);
}

.signin-card {
  width: 100%;
  max-width: 400px;
}

.signin-header {
  margin-bottom: 1.5rem;
  text-align: center;
}

.signin-mobile-notice,
.signin-error {
  margin-bottom: 1rem;
}

.w-full {
  width: 100%;
}

.brand-title {
  font-size: 1.6rem;
  font-weight: 600;
  color: var(--texto-primario);
  letter-spacing: 1px;
  margin: 0;
}

.brand-title span {
  color: var(--sucesso);
  font-weight: 700;
}

.logo-img {
  width: 40px;
  height: 40px;
  min-width: 40px;
  margin: 0 auto 0.5rem;
  display: block;
  object-fit: contain;
}
</style>
