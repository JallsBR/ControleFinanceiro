<template>
  <div class="menu-user">
    <button
      type="button"
      class="menu-user__trigger"
      aria-haspopup="menu"
      :aria-expanded="menuAberto"
      aria-label="Abrir menu da conta"
      @click="abrirMenu"
    >
      <i class="pi pi-user menu-user__icon" aria-hidden="true" />
      <span class="menu-user__name">{{ displayName }}</span>
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
      </template>
    </TieredMenu>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useStore } from 'vuex'
import TieredMenu from 'primevue/tieredmenu'

const store = useStore()
const menuRef = ref(null)
const menuAberto = ref(false)

const displayName = computed(() => store.getters.getUser?.username || 'Visitante')

const user = computed(() => store.getters.getUser)

/** Staff ou superuser: vê item Configurações (API expõe is_staff / is_superuser no login). */
const podeConfiguracoes = computed(() => {
  const u = user.value
  if (!u) return false
  return Boolean(u.is_staff || u.is_superuser)
})

const itens = computed(() => {
  const base = [
    { label: 'Perfil', icon: 'pi pi-user', route: '/perfil' },
    { label: 'Assinatura', icon: 'pi pi-id-card', route: '/assinatura' },
    { label: 'Consultoria', icon: 'pi pi-comments', route: '/consultoria' }
  ]
  if (!podeConfiguracoes.value) return base
  return [
    ...base,
    { label: 'Configurações', icon: 'pi pi-cog', route: '/configuracoes' }
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

.menu-user__trigger:hover {
  background-color: var(--bg-primario);
  color: var(--texto-primario);
}

.menu-user__icon {
  font-size: 1.2rem;
  min-width: 20px;
  text-align: center;
}

.menu-user__name {
  font-size: 0.95rem;
  max-width: 160px;
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
