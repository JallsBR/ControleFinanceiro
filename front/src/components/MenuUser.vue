<template>
  <div class="menu-user">
    <div class="menu-user__trigger-wrap">
      <button
        type="button"
        class="menu-user__trigger"
        :class="{ 'menu-user__trigger--monitor': modoMonitorFinancas }"
        aria-haspopup="menu"
        :aria-expanded="menuAberto"
        :aria-label="ariaLabelMenu"
        @click="abrirMenu"
      >
        <i class="pi pi-user menu-user__icon" aria-hidden="true" />
        <span class="menu-user__textblock">
          <span class="menu-user__name">{{ displayName }}</span>
        </span>
        <i class="pi pi-angle-down menu-user__chevron" aria-hidden="true" />
      </button>
      <Badge
        v-if="mostrarBadgeOverlay"
        :value="badgeOverlayValor"
        severity="danger"
        class="menu-user__badge-overlay"
      />
    </div>

    <TieredMenu
      ref="menuRef"
      :model="itens"
      popup
      append-to="body"
      ariaLabel="Menu da conta"
      @show="menuAberto = true"
      @hide="menuAberto = false"
    >
      <template #item="{ item, props, hasSubmenu }">
        <RouterLink
          v-if="item.route"
          v-slot="{ href, navigate }"
          :to="item.route"
          custom
        >
          <a
            :href="href"
            class="menu-user__row"
            v-bind="props.action"
            @click="navigate"
          >
            <span v-bind="props.icon" />
            <span class="menu-user__label" v-bind="props.label">{{ item.label }}</span>
            <Badge
              v-if="badgeValor(item) != null"
              :value="badgeValor(item)"
              severity="danger"
              class="menu-user__badge"
            />
            <i
              v-if="hasSubmenu"
              class="pi pi-angle-right menu-user__subcaret"
              aria-hidden="true"
            />
          </a>
        </RouterLink>
        <a
          v-else
          v-bind="props.action"
          class="menu-user__row"
          :class="{ 'p-disabled': item.disabled }"
          href="#"
          @click.prevent
        >
          <span v-if="item.icon" v-bind="props.icon" />
          <span class="menu-user__label" v-bind="props.label">{{ item.label }}</span>
          <Badge
            v-if="badgeValor(item) != null"
            :value="badgeValor(item)"
            severity="danger"
            class="menu-user__badge"
          />
          <i
            v-if="hasSubmenu"
            class="pi pi-angle-right menu-user__subcaret"
            aria-hidden="true"
          />
        </a>
      </template>
    </TieredMenu>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useStore } from 'vuex'
import TieredMenu from 'primevue/tieredmenu'
import Badge from 'primevue/badge'

const store = useStore()
const menuRef = ref(null)
const menuAberto = ref(false)
const perfilMonitorErro = ref(false)

const modoMonitorFinancas = computed(() => store.getters.subjectViewAdminActive)
const monitored = computed(() => store.getters.getSubjectMonitoredUser)
const user = computed(() => store.getters.getUser)

const isConsultor = computed(() => Boolean(user.value?.is_gerente))
const pendentesRecebidas = computed(
  () => store.getters.consultoriaPendentesRecebidas
)

/** Badge no botão do menu: só consultor, só quando há pendentes e menu fechado. */
const mostrarBadgeOverlay = computed(
  () =>
    isConsultor.value &&
    pendentesRecebidas.value > 0 &&
    !menuAberto.value
)

const badgeOverlayValor = computed(() => {
  const n = pendentesRecebidas.value
  return n > 99 ? '99+' : String(n)
})

/** Nome + apelido; senão username ou id (objetos utilizador da API / store). */
function nomeSobrenomeOuUsername (u) {
  if (!u) return 'Visitante'
  const fn = (u.first_name || '').trim()
  const ln = (u.last_name || '').trim()
  const completo = [fn, ln].filter(Boolean).join(' ')
  if (completo) return completo
  if (u.username) return u.username
  if (u.id != null) return `ID ${u.id}`
  return 'Visitante'
}

const displayName = computed(() => {
  if (modoMonitorFinancas.value) {
    const u = monitored.value
    if (!u) {
      return perfilMonitorErro.value ? 'Monitor (erro)' : 'A carregar…'
    }
    const nome = (u.nome_completo || '').trim()
    if (nome && nome !== '—') return nome
    return nomeSobrenomeOuUsername(u)
  }
  return nomeSobrenomeOuUsername(user.value)
})

const ariaLabelMenu = computed(() => 'Abrir menu da conta')

watch(
  () => [
    store.getters.subjectViewAdminActive,
    store.state.subjectViewMode?.userId
  ],
  async ([admin, uid]) => {
    perfilMonitorErro.value = false
    if (!admin) {
      store.commit('SET_SUBJECT_MONITORED_USER', null)
      return
    }
    if (!uid) return
    await store.dispatch('fetchSubjectMonitoredProfile')
    if (store.getters.subjectViewAdminActive && !store.state.subjectMonitoredUser) {
      perfilMonitorErro.value = true
    }
  },
  { immediate: true }
)

const podeAdministrar = computed(() => {
  const u = user.value
  if (!u) return false
  return Boolean(u.is_staff || u.is_superuser)
})

/** Só consultores (gerentes) vêem o separador Solicitações. */
const podeVerSolicitacoes = computed(() => isConsultor.value)

/** Valor do Badge na linha “Solicitações” (menu aberto). */
function badgeCountSolicitacoes () {
  if (!isConsultor.value) return null
  const n = pendentesRecebidas.value
  return n > 0 ? n : null
}

/** Valor do Badge PrimeVue (string). */
function badgeValor (item) {
  const n = item?.badgeCount
  if (n == null || n <= 0) return null
  return n > 99 ? '99+' : String(n)
}

/** Em modo “ver como”, menu como utilizador comum: sem Administrar. */
const mostrarLinkAdministrar = computed(
  () => podeAdministrar.value && !modoMonitorFinancas.value
)

const itens = computed(() => {
  const bcSol = badgeCountSolicitacoes()
  const base = [
    { label: 'Perfil', icon: 'pi pi-user', route: '/perfil' },
    { label: 'Assinatura', icon: 'pi pi-id-card', route: '/assinatura' },
    {
      label: 'Consultoria',
      icon: 'pi pi-comments',
      route: '/consultoria'
    }
  ]
  if (podeVerSolicitacoes.value) {
    base.push({
      label: 'Solicitações',
      icon: 'pi pi-inbox',
      route: '/consultoria/solicitacoes',
      badgeCount: bcSol
    })
  }
  if (!mostrarLinkAdministrar.value) {
    return base
  }
  return [
    ...base,
    { label: 'Administrar', icon: 'pi pi-cog', route: '/administrar' }
  ]
})

function abrirMenu (event) {
  menuRef.value?.toggle(event)
}
</script>

<style scoped>
.menu-user {
  display: inline-flex;
  align-items: center;
}

.menu-user__trigger-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.menu-user__badge-overlay {
  position: absolute;
  top: 2px;
  right: 2px;
  transform: translate(40%, -40%);
  z-index: 2;
  pointer-events: none;
  line-height: 0;
  box-shadow: 0 0 0 2px var(--bg-primario, #14161c);
  border-radius: 9999px;
}

/* Badge redondo (círculo / cápsula) — evita distorção do PrimeVue */
.menu-user__badge-overlay :deep(.p-badge),
.menu-user__badge :deep(.p-badge) {
  border-radius: 9999px !important;
  min-width: 1.25rem;
  height: 1.25rem;
  box-sizing: border-box;
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  padding: 0 0.35rem;
  line-height: 1 !important;
  font-size: 0.65rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.menu-user__trigger {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  margin: 0;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--texto-secundario);
  font: inherit;
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.menu-user__trigger--monitor {
  max-width: min(320px, 42vw);
}

.menu-user__trigger:hover {
  background-color: var(--bg-primario);
  color: var(--texto-primario);
}

.menu-user__icon {
  font-size: 1.2rem;
  min-width: 20px;
  text-align: center;
}

.menu-user__textblock {
  display: block;
  min-width: 0;
  text-align: left;
}

.menu-user__name {
  font-size: 0.95rem;
  font-weight: 600;
  max-width: 280px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.menu-user__chevron {
  font-size: 0.75rem;
  opacity: 0.85;
}

.menu-user__row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
}

.menu-user__label {
  flex: 1;
  min-width: 0;
}

.menu-user__badge {
  flex-shrink: 0;
}

.menu-user__subcaret {
  margin-left: auto;
  font-size: 0.8rem;
  opacity: 0.8;
}
</style>
