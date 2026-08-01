<template>
  <div class="signin-page">
    <Card class="signin-card" style="width: 600px;">
      <template #content>
        <form v-if="!challengeId" @submit.prevent="handleLogin">
          <div class="signin-header">
            <div class="logo-container">
              <img src="/logoFinancasApp.png" alt="Logo Financas" class="logo-img" />
              <h2 class="brand-title">Finanças <span>APP</span></h2>
            </div>
          </div>

          <Message
            v-if="isMobileView"
            severity="warn"
            :closable="false"
            class="signin-mobile-notice"
          >
            A experiência foi otimizada apenas para desktop.
          </Message>

          <Message v-if="error" severity="error" :closable="false" class="signin-error">
            Credenciais não encontradas. Tente novamente.
          </Message>

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
            <p class="signin-forgot">
              <RouterLink to="/auth/esqueci-senha" class="signin-link">
                Esqueceu a senha?
              </RouterLink>
            </p>
          </div>

          <Button
            type="submit"
            :label="loading ? 'Entrando...' : 'Entrar'"
            class="w-full"
            :loading="loading"
            :disabled="loading"
          />
          <div class="signin-footer">
            <p class="signin-footer-text">
              Não é cadastrado?
              <RouterLink to="/signup" class="signin-link">
                Registre-se
              </RouterLink>
            </p>
          </div>
        </form>

        <form v-else @submit.prevent="handleVerify2fa">
          <div class="signin-header">
            <div class="logo-container">
              <img src="/logoFinancasApp.png" alt="Logo Financas" class="logo-img" />
              <h2 class="brand-title">Finanças <span>APP</span></h2>
            </div>
          </div>

          <Message severity="info" :closable="false" class="signin-mobile-notice">
            Enviamos um código e um link para o e-mail cadastrado. Digite o código abaixo ou abra o link “Entrar agora”.
          </Message>

          <Message v-if="error2fa" severity="error" :closable="false" class="signin-error">
            Código inválido ou expirado. Tente novamente.
          </Message>

          <div class="field mb-3">
            <label for="otp-code" class="field-label">Código de verificação</label>
            <InputText
              id="otp-code"
              v-model="otpCode"
              type="text"
              inputmode="numeric"
              maxlength="6"
              class="w-full"
              placeholder="000000"
              autocomplete="one-time-code"
            />
          </div>

          <Button
            type="submit"
            :label="loading ? 'Verificando...' : 'Verificar código'"
            class="w-full"
            :loading="loading"
            :disabled="loading || otpCode.trim().length !== 6"
          />

          <div class="signin-footer">
            <button type="button" class="signin-link signin-link-btn" @click="voltarLogin">
              Voltar ao login
            </button>
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
      error2fa: null,
      challengeId: null,
      otpCode: '',
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
      this.error2fa = null
      const result = await this.$store.dispatch('login', {
        login: this.login,
        password: this.password
      })

      if (result?.requires_2fa && result.challenge_id) {
        this.challengeId = result.challenge_id
        this.otpCode = ''
        this.$toast.add({
          severity: 'info',
          summary: 'Verificação em dois fatores',
          detail: 'Enviamos um código para o seu e-mail.',
          life: 5000
        })
        return
      }

      if (result?.ok) {
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
    },

    async handleVerify2fa() {
      this.error2fa = null
      const success = await this.$store.dispatch('verifyTwoFactor', {
        challenge_id: this.challengeId,
        code: this.otpCode.trim()
      })

      if (success) {
        const u = this.$store.getters.getUser
        this.$router.push(routeLocationAfterLogin(u))
      } else {
        this.error2fa = true
        this.$toast.add({
          severity: 'error',
          summary: 'Código inválido',
          detail: 'Código inválido ou expirado. Tente novamente.',
          life: 5000
        })
      }
    },

    voltarLogin() {
      this.challengeId = null
      this.otpCode = ''
      this.error2fa = null
      this.password = ''
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

.signin-forgot {
  margin: 0.5rem 0 0;
  text-align: right;
  font-size: 0.875rem;
}

.w-full {
  width: 100%;
}

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

.signin-link-btn {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  font: inherit;
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
