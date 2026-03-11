<template>
  <div class="signin-page">
    <Card class="signin-card">
      <template #content>
        <form @submit.prevent="handleLogin">
          <!-- Título -->
          <div class="signin-header">
            <div class="logo-container">
              <img src="/logoFinancasApp.png" alt="Logo Financas" class="logo-img" />
              <h2 class="brand-title">Finanças <span>APP</span></h2>
            </div>
          </div>

          <!-- Mensagem de erro -->
          <Message v-if="error" severity="error" :closable="false" class="signin-error">
            Credenciais não encontradas. Tente novamente.
          </Message>

          <!-- Email -->
          <div class="field mb-3">
            <label for="email" class="field-label">Email</label>
            <InputText
              id="email"
              v-model="email"
              type="email"
              class="w-full"
              placeholder="seu@email.com"
              autocomplete="email"
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
export default {
  name: 'SiginPage',
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
      email: '',
      password: '',
      error: null
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
        email: this.email,
        password: this.password
      })

      if (success) {
        this.$router.push({ name: 'home' })
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
  background: var(--p-surface-ground);
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
    color: #f8f9fa;
    letter-spacing: 1px;
    margin: 0;
}

.brand-title span {
    color: #20c997; /* verde moderno */
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
