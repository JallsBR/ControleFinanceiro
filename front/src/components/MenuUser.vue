<template>
  <div class="menu-user">
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
            v-bind="props.action"
            @click="navigate"
          >
            <span v-bind="props.icon" />
            <span v-bind="props.label">{{ item.label }}</span>
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
          :class="{ 'p-disabled': item.disabled }"
          href="#"
          @click.prevent
        >
          <span v-if="item.icon" v-bind="props.icon" />
          <span v-bind="props.label">{{ item.label }}</span>
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

const store = useStore()
const menuRef = ref(null)
const menuAberto = ref(false)
const perfilMonitorErro = ref(false)

const modoMonitorFinancas = computed(() => store.getters.subjectViewAdminActive)
const monitored = computed(() => store.getters.getSubjectMonitoredUser)
const user = computed(() => store.getters.getUser)

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

/** Em modo “ver como”, menu como utilizador comum: sem Administrar. */
const mostrarLinkAdministrar = computed(
  () => podeAdministrar.value && !modoMonitorFinancas.value
)

const itens = computed(() => {
  const base = [
    { label: 'Perfil', icon: 'pi pi-user', route: '/perfil' },
    { label: 'Assinatura', icon: 'pi pi-id-card', route: '/assinatura' },
    { label: 'Consultoria', icon: 'pi pi-comments', route: '/consultoria' }
  ]
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

.menu-user__subcaret {
  margin-left: auto;
  font-size: 0.8rem;
  opacity: 0.8;
}
</style>
