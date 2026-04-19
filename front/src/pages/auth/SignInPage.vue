<template>
  <div class="signin-page">
    <Card class="signin-card" style="width: 600px;">
      <template #content>
        <form @submit.prevent="handleLogin">
          <!-- Título -->
          <div class="signin-header">
            <div class="logo-container">
              <img src="/logoFinancasApp.png" alt="Logo Financas" class="logo-img" />
              <h2 class="brand-title">Finanças <span>APP</span></h2>
            </div>
          </div>

          <!-- Aviso em telas pequenas (celular) -->
          <Message
            v-if="isMobileView"
            severity="warn"
            :closable="false"
            class="signin-mobile-notice"
          >
            A experiência foi otimizada apenas para desktop.
          </Message>

          <!-- Mensagem de erro -->
          <Message v-if="error" severity="error" :closable="false" class="signin-error">
            Credenciais não encontradas. Tente novamente.
          </Message>

          <!-- E-mail ou nome de usuário -->
          <div class="field mb-3">
            <label for="login" class="field-label">E-mail ou usuário</label>
            <InputText
              id="login"
              v-model="login"
              type="text"
              class="w-full"
              placeholder="seu@email.com ou nome de usuário"
              autocomplete="username"
            />
          </div>

          <!-- Senha -->
          <div class="field mb-3">
            <label for="password" class="field-label">Senha</label>
            <Password
              id="password"
              v-model="password"
              class="w-full"
              placeholder="Sua senha"
              :feedback="false"
              toggleMask
              fluid
              inputClass="w-full"
            />
          </div>

          <!-- Botão -->
          <Button
            type="submit"
            :label="loading ? 'Entrando...' : 'Entrar'"
            class="w-full"
            :loading="loading"
            :disabled="loading"
          />

          <!-- Link registro -->
          <div class="signin-footer">
            <p class="signin-footer-text">
              Não é cadastrado?
              <RouterLink to="/signup" class="signin-link">
                Registre-se
              </RouterLink>
            </p>
          </div>
        </form>
      </template>
    </Card>
  </div>
</template>

<script>
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { RouterLink } from 'vue-router'
import { routeLocationAfterLogin } from '@/utils/postLoginRoute'

export default {
  name: 'SignInPage',
  components: {
    Card,
    InputText,
    Password,
    Button,
    Message,
    RouterLink
  },
  data() {
    return {
      login: '',
      password: '',
      error: null,
      isMobileView: false,
      _mobileMq: null,
      _onMobileMqChange: null
    }
  },

  mounted() {
    this._mobileMq = window.matchMedia('(max-width: 768px)')
    this.isMobileView = this._mobileMq.matches
    this._onMobileMqChange = (e) => {
      this.isMobileView = e.matches
    }
    this._mobileMq.addEventListener('change', this._onMobileMqChange)
  },

  beforeUnmount() {
    if (this._mobileMq && this._onMobileMqChange) {
      this._mobileMq.removeEventListener('change', this._onMobileMqChange)
    }
  },

  computed: {
    loading() {
      return this.$store.getters.isLoading
    }
  },

  methods: {
    async handleLogin() {
      this.error = null
      const success = await this.$store.dispatch('login', {
        login: this.login,
        password: this.password
      })

      if (success) {
        const u = this.$store.getters.getUser
        this.$router.push(routeLocationAfterLogin(u))
      } else {
        this.error = true
        this.$toast.add({
          severity: 'error',
          summary: 'Erro ao entrar',
          detail: 'Credenciais não encontradas. Tente novamente.',
          life: 5000
        })
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

.signin-card {
  width: 100%;
  max-width: 400px;
}

.signin-card :deep(.p-card-content) {
  padding: 0;
}

.signin-header {
  margin-bottom: 1.5rem;
  text-align: center;
}

.signin-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--p-text-color);
}

.signin-title .brand {
  font-weight: 700;
}

.signin-mobile-notice {
  margin-bottom: 1rem;
}

.signin-error {
  margin-bottom: 1rem;
}

.field-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--p-text-color);
}

.mb-3 {
  margin-bottom: 1rem;
}

.w-full {
  width: 100%;
}

/* Password: mesma largura do email, ícone do olho no fim do input */
.signin-card :deep(.p-password) {
  width: 100%;
}
.signin-card :deep(.p-password .p-password-input),
.signin-card :deep(.p-password .p-inputtext) {
  flex: 1 1 auto;
  min-width: 0;
}

.signin-footer {
  margin-top: 1.5rem;
  text-align: center;
}

.signin-footer-text {
  margin: 0;
  color: var(--p-text-muted-color);
  font-size: 0.9375rem;
}

.signin-link {
  color: var(--p-primary-color);
  text-decoration: none;
  font-weight: 500;
}

.signin-link:hover {
  text-decoration: underline;
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
