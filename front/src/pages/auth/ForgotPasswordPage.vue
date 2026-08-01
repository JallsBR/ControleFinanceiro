<template>
  <div class="signin-page">
    <Card class="signin-card" style="width: 600px;">
      <template #content>
        <form @submit.prevent="enviar">
          <div class="signin-header">
            <div class="logo-container">
              <img src="/logoFinancasApp.png" alt="Logo Financas" class="logo-img" />
              <h2 class="brand-title">Finanças <span>APP</span></h2>
            </div>
          </div>

          <Message severity="info" :closable="false" class="signin-mobile-notice">
            Informe o e-mail ou usuário da conta. Se existir, enviaremos um link para redefinir a senha.
          </Message>

          <Message v-if="erro" severity="error" :closable="false" class="signin-error">
            {{ erro }}
          </Message>
          <Message v-if="sucesso" severity="success" :closable="false" class="signin-error">
            {{ sucesso }}
          </Message>

          <div class="field mb-3">
            <label for="login-reset" class="field-label">E-mail ou usuário</label>
            <InputText
              id="login-reset"
              v-model="login"
              type="text"
              class="w-full"
              placeholder="seu@email.com ou nome de usuário"
              autocomplete="username"
              :disabled="loading || !!sucesso"
            />
          </div>

          <Button
            type="submit"
            :label="loading ? 'Enviando...' : 'Enviar link'"
            class="w-full"
            :loading="loading"
            :disabled="loading || !login.trim() || !!sucesso"
          />

          <div class="signin-footer">
            <RouterLink to="/" class="signin-link">Voltar ao login</RouterLink>
          </div>
        </form>
      </template>
    </Card>
  </div>
</template>

<script>
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { RouterLink } from 'vue-router'
import { authService } from '@/services/authService'

export default {
  name: 'ForgotPasswordPage',
  components: { Card, InputText, Button, Message, RouterLink },
  data () {
    return {
      login: '',
      loading: false,
      erro: null,
      sucesso: null
    }
  },
  methods: {
    async enviar () {
      this.erro = null
      this.sucesso = null
      this.loading = true
      try {
        const data = await authService.requestPasswordReset({
          login: this.login.trim()
        })
        this.sucesso =
          data?.detail ||
          'Se existir uma conta com esses dados, enviamos um e-mail com instruções.'
        this.$toast?.add?.({
          severity: 'success',
          summary: 'E-mail',
          detail: this.sucesso,
          life: 6000
        })
      } catch (e) {
        const data = e?.response?.data
        this.erro =
          data?.detail ||
          data?.login?.[0] ||
          'Não foi possível solicitar a redefinição. Tente novamente.'
      } finally {
        this.loading = false
      }
    }
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
.signin-card { width: 100%; max-width: 400px; }
.signin-header { margin-bottom: 1.5rem; text-align: center; }
.signin-mobile-notice, .signin-error { margin-bottom: 1rem; }
.field-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--p-text-color);
}
.mb-3 { margin-bottom: 1rem; }
.w-full { width: 100%; }
.signin-footer { margin-top: 1.5rem; text-align: center; }
.signin-link {
  color: var(--p-primary-color);
  text-decoration: none;
  font-weight: 500;
}
.signin-link:hover { text-decoration: underline; }
.brand-title {
  font-size: 1.6rem;
  font-weight: 600;
  color: var(--texto-primario);
  letter-spacing: 1px;
  margin: 0;
}
.brand-title span { color: var(--sucesso); font-weight: 700; }
.logo-img {
  width: 40px;
  height: 40px;
  min-width: 40px;
  margin: 0 auto 0.5rem;
  display: block;
  object-fit: contain;
}
</style>
