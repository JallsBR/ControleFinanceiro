<template>
  <div class="perfil-page">
    <CardStatus
      tituloPrincipal="Perfil"
      :subtitulo="subtituloCard"
      icone="pi pi-user"
      style="margin-bottom: 1rem;"
    />

    <Message v-if="erroCarregar" severity="warn" :closable="false" class="perfil-msg">
      {{ erroCarregar }}
    </Message>

    <div class="perfil-form-card">
      <Message v-if="erroSalvar" severity="error" :closable="true" class="perfil-msg" @close="erroSalvar = ''">
        {{ erroSalvar }}
      </Message>
      <Message v-if="msgSucesso" severity="success" :closable="true" class="perfil-msg" @close="msgSucesso = ''">
        {{ msgSucesso }}
      </Message>

      <form @submit.prevent="salvar">
        <div class="perfil-grid">
          <!-- Esquerda: todos os dados do usuário -->
          <div class="perfil-col perfil-col--dados">
            <h2 class="perfil-secao-titulo">Dados da conta</h2>

            <div class="field mb-3">
              <label for="perfil-username" class="field-label">Usuário</label>
              <InputText
                id="perfil-username"
                v-model="username"
                class="w-full"
                disabled
                autocomplete="username"
              />
              <p class="perfil-hint">O nome de usuário não pode ser alterado.</p>
            </div>

            <div class="field mb-3">
              <label for="perfil-email" class="field-label">E-mail</label>
              <InputText
                id="perfil-email"
                v-model="email"
                type="email"
                class="w-full"
                required
                autocomplete="email"
                :disabled="somenteLeituraMonitor"
              />
            </div>

            <div class="field mb-3">
              <label for="perfil-first" class="field-label">Nome</label>
              <InputText
                id="perfil-first"
                v-model="firstName"
                class="w-full"
                autocomplete="given-name"
                :disabled="somenteLeituraMonitor"
              />
            </div>

            <div class="field mb-3">
              <label for="perfil-last" class="field-label">Sobrenome</label>
              <InputText
                id="perfil-last"
                v-model="lastName"
                class="w-full"
                autocomplete="family-name"
                :disabled="somenteLeituraMonitor"
              />
            </div>

            <div v-if="!somenteLeituraMonitor" class="field mb-0">
              <label for="perfil-pagina-inicial" class="field-label">Página inicial após login</label>
              <Select
                id="perfil-pagina-inicial"
                v-model="paginaInicial"
                :options="opcoesPaginaInicial"
                optionLabel="label"
                optionValue="value"
                class="w-full"
                placeholder="Onde abrir ao entrar"
                :disabled="carregando"
              />
              <p class="perfil-hint">
                Painel ou relatório para todos; Administrar só para equipa (staff);
                Consultoria só para utilizadores registados como consultor.
              </p>
            </div>
          </div>

          <Divider
          v-if="!somenteLeituraMonitor"
          layout="vertical"
          type="solid"
          class="perfil-divider-v"
        />

          <!-- Direita: toda a alteração de senha -->
          <div v-if="!somenteLeituraMonitor" class="perfil-col perfil-col--senha">
            <h2 class="perfil-secao-titulo">Senha</h2>

            <div class="field mb-3">
              <label for="perfil-cur" class="field-label">Senha atual</label>
              <Password
                id="perfil-cur"
                v-model="currentPassword"
                class="w-full"
                :feedback="false"
                toggleMask
                fluid
                inputClass="w-full"
                autocomplete="current-password"
              />
              <p class="perfil-hint">Obrigatório para definir uma nova senha.</p>
            </div>

            <div class="field mb-3">
              <label for="perfil-nova" class="field-label">Nova senha</label>
              <Password
                id="perfil-nova"
                v-model="newPassword"
                class="w-full"
                toggleMask
                fluid
                inputClass="w-full"
                autocomplete="new-password"
              />
            </div>

            <div class="field mb-0">
              <label for="perfil-nova2" class="field-label">Confirmar nova senha</label>
              <Password
                id="perfil-nova2"
                v-model="newPasswordConfirm"
                class="w-full"
                :feedback="false"
                toggleMask
                fluid
                inputClass="w-full"
                autocomplete="new-password"
              />
            </div>
          </div>
        </div>

        <div v-if="!somenteLeituraMonitor" class="perfil-actions">
          <Button
            type="submit"
            label="Salvar alterações"
            icon="pi pi-check"
            :loading="salvando"
            :disabled="salvando || carregando"
          />
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useStore } from 'vuex'
import CardStatus from '@/components/CardStatus.vue'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import Divider from 'primevue/divider'
import Select from 'primevue/select'
import { authService } from '@/services/authService'
import { useToast } from '@/utils/useToast'

const store = useStore()
const toast = useToast()

const modoMonitor = computed(() => store.getters.subjectViewAdminActive)
const monitored = computed(() => store.getters.getSubjectMonitoredUser)
const somenteLeituraMonitor = computed(() => modoMonitor.value)

const subtituloCard = computed(() =>
  somenteLeituraMonitor.value
    ? 'Dados do utilizador que está a visualizar (somente leitura).'
    : 'Atualize seus dados e, se quiser, sua senha'
)

const carregando = ref(true)
const salvando = ref(false)
const erroCarregar = ref('')
const erroSalvar = ref('')
const msgSucesso = ref('')

const username = ref('')
const email = ref('')
const firstName = ref('')
const lastName = ref('')
const paginaInicial = ref('dashboard')
const currentPassword = ref('')
const newPassword = ref('')
const newPasswordConfirm = ref('')

function opcoesPaginaInicialParaUsuario (u) {
  const list = [
    { label: 'Painel (dashboard)', value: 'dashboard' },
    { label: 'Relatório', value: 'relatorio' }
  ]
  if (u?.is_staff || u?.is_superuser) {
    list.push({ label: 'Administrar', value: 'administrar' })
  }
  if (u?.is_gerente) {
    list.push({ label: 'Consultoria', value: 'consultoria' })
  }
  return list
}

const opcoesPaginaInicial = computed(() =>
  opcoesPaginaInicialParaUsuario(store.getters.getUser)
)

function paginaInicialCoerente (u, valor) {
  const v = (valor && String(valor).trim()) || 'dashboard'
  const permitidas = new Set(opcoesPaginaInicialParaUsuario(u).map((o) => o.value))
  return permitidas.has(v) ? v : 'dashboard'
}

function aplicarUsuario (u) {
  if (!u) return
  username.value = u.username ?? ''
  email.value = u.email ?? ''
  firstName.value = u.first_name ?? ''
  lastName.value = u.last_name ?? ''
  paginaInicial.value = paginaInicialCoerente(u, u.pagina_inicial)
}

function formatarErroApi (data) {
  if (!data || typeof data !== 'object') return 'Não foi possível salvar.'
  if (data.detail) return String(data.detail)
  const partes = []
  for (const [campo, val] of Object.entries(data)) {
    if (campo === 'detail') continue
    const texto = Array.isArray(val) ? val.join(' ') : String(val)
    partes.push(texto)
  }
  return partes.join(' ') || 'Verifique os dados informados.'
}

async function carregar () {
  erroCarregar.value = ''
  carregando.value = true
  if (modoMonitor.value) {
    if (!monitored.value) {
      await store.dispatch('fetchSubjectMonitoredProfile')
    }
    const m = store.getters.getSubjectMonitoredUser
    if (m) {
      aplicarUsuario(m)
    } else {
      aplicarUsuario(store.getters.getUser)
      erroCarregar.value =
        'Não foi possível carregar os dados do utilizador monitorizado.'
      toast.error('Perfil', erroCarregar.value)
    }
    carregando.value = false
    return
  }
  aplicarUsuario(store.getters.getUser)
  try {
    const u = await authService.getProfile()
    aplicarUsuario(u)
    store.commit('UPDATE_USER', u)
  } catch (e) {
    console.error(e)
    erroCarregar.value = 'Não foi possível carregar o perfil. Tente novamente mais tarde.'
    toast.error('Erro', erroCarregar.value)
  } finally {
    carregando.value = false
  }
}

async function salvar () {
  if (somenteLeituraMonitor.value) return
  erroSalvar.value = ''
  msgSucesso.value = ''

  const nova = newPassword.value.trim()
  const conf = newPasswordConfirm.value.trim()

  if (nova !== conf) {
    erroSalvar.value = 'A nova senha e a confirmação devem ser iguais.'
    toast.error('Validação', erroSalvar.value)
    return
  }

  if ((nova || conf) && !nova) {
    erroSalvar.value = 'Preencha a nova senha nos dois campos ou deixe ambos em branco.'
    toast.error('Validação', erroSalvar.value)
    return
  }

  if (nova && !currentPassword.value) {
    erroSalvar.value = 'Informe a senha atual para definir uma nova senha.'
    toast.error('Validação', erroSalvar.value)
    return
  }

  salvando.value = true
  try {
    const payload = {
      email: email.value.trim(),
      first_name: firstName.value.trim(),
      last_name: lastName.value.trim(),
      pagina_inicial: paginaInicial.value
    }
    if (nova) {
      payload.current_password = currentPassword.value
      payload.new_password = newPassword.value
    }
    const atualizado = await authService.updateProfile(payload)
    store.commit('UPDATE_USER', atualizado)
    currentPassword.value = ''
    newPassword.value = ''
    newPasswordConfirm.value = ''
    msgSucesso.value = 'Perfil atualizado com sucesso.'
    toast.success('Perfil', 'Dados salvos com sucesso.')
  } catch (e) {
    const data = e?.response?.data
    erroSalvar.value = formatarErroApi(data)
    toast.error('Erro', erroSalvar.value)
  } finally {
    salvando.value = false
  }
}

watch(
  [modoMonitor, monitored],
  () => {
    if (modoMonitor.value && monitored.value) {
      aplicarUsuario(monitored.value)
    }
  },
  { deep: true }
)

onMounted(() => {
  carregar()
})
</script>

<style scoped>
/* Mesmo fluxo das outras páginas: largura do .container do AuthLayout, sem max-width local */
.perfil-page {
  margin-bottom: 1.5rem;
}

.perfil-form-card {
  background: var(--bg-secundario);
  border-radius: 18px;
  padding: 1.25rem 1.5rem;
  width: 100%;
}

.perfil-msg {
  margin-bottom: 1rem;
}

/* Alinhado ao título de seções (ex.: relatório filtros-wrapper .card-title) */
.perfil-secao-titulo {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--texto-primario);
}

.perfil-grid {
  display: flex;
  align-items: stretch;
  width: 100%;
  gap: 0;
}

.perfil-col {
  flex: 1 1 0;
  min-width: 0;
  padding: 0 1rem;
}

.perfil-col--dados {
  padding-left: 0;
}

.perfil-col--senha {
  padding-right: 0;
}

.perfil-divider-v {
  flex: 0 0 auto;
  align-self: stretch;
  margin: 0;
}

.field-label {
  display: block;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--texto-primario);
  margin-bottom: 0.35rem;
}

.perfil-hint {
  margin: 0.35rem 0 0;
  font-size: 0.8rem;
  color: var(--texto-secundario);
}

.perfil-hint--intro {
  margin: 0 0 1rem 0;
  line-height: 1.45;
}

.perfil-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid color-mix(in srgb, var(--texto-secundario) 18%, transparent);
}

.w-full {
  width: 100%;
}

@media (max-width: 768px) {
  .perfil-grid {
    flex-direction: column;
  }

  .perfil-divider-v {
    display: none;
  }

  .perfil-col {
    padding: 0;
  }

  .perfil-col--senha {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid color-mix(in srgb, var(--texto-secundario) 22%, transparent);
  }
}

:deep(.perfil-divider-v.p-divider-vertical) {
  min-height: 100%;
}
</style>
