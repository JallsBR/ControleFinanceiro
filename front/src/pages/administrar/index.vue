<template>
  <div class="administrar-page">
    <CardStatus
      tituloPrincipal="Administrar"
      subtitulo="Ferramentas restritas a staff e superusuário"
      icone="pi pi-cog"
      style="margin-bottom: 1rem;"
    />

    <div class="administrar-tabs-wrap">
      <Tabs v-model:value="abaAtiva" scrollable>
        <TabList>
          <Tab v-if="podeVerUsuarios" value="usuarios">
            <span class="admin-tab-header">
              <i class="pi pi-users" aria-hidden="true" />
              Usuários
            </span>
          </Tab>
          <Tab v-if="podeVerGrupos" value="grupos">
            <span class="admin-tab-header">
              <i class="pi pi-th-large" aria-hidden="true" />
              Grupos
            </span>
          </Tab>
          <Tab value="dashboard">
            <span class="admin-tab-header">
              <i class="pi pi-chart-bar" aria-hidden="true" />
              Dashboard
            </span>
          </Tab>
        </TabList>
        <TabPanels>
          <TabPanel v-if="podeVerUsuarios" value="usuarios">
            <TabUsuarios />
          </TabPanel>
          <TabPanel v-if="podeVerGrupos" value="grupos">
            <TabGrupos />
          </TabPanel>
          <TabPanel value="dashboard">
            <TabDashboard />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useStore } from 'vuex'
import CardStatus from '@/components/CardStatus.vue'
import { authService } from '@/services/authService'
import { resolveAdminCapabilities } from '@/utils/adminCapabilities'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import TabUsuarios from './componentes/TabUsuarios.vue'
import TabGrupos from './componentes/TabGrupos.vue'
import TabDashboard from './componentes/TabDashboard.vue'

const store = useStore()
const abaAtiva = ref('usuarios')

const caps = computed(() => resolveAdminCapabilities(store.getters.getUser))
const podeVerUsuarios = computed(() => caps.value.users.view)
const podeVerGrupos = computed(() => caps.value.groups.view)

watch(
  [podeVerUsuarios, podeVerGrupos],
  () => {
    const tab = abaAtiva.value
    if (tab === 'usuarios' && !podeVerUsuarios.value) {
      abaAtiva.value = podeVerGrupos.value ? 'grupos' : 'dashboard'
    } else if (tab === 'grupos' && !podeVerGrupos.value) {
      abaAtiva.value = podeVerUsuarios.value ? 'usuarios' : 'dashboard'
    }
  },
  { immediate: true }
)

onMounted(async () => {
  try {
    const u = await authService.getProfile()
    store.commit('UPDATE_USER', u)
  } catch (_) {
    /* mantém user em cache */
  }
})
</script>

<style scoped>
.administrar-page {
  margin-bottom: 1.5rem;
}

.administrar-tabs-wrap {
  background: var(--bg-secundario);
  border-radius: 18px;
  padding: 0.75rem 0.75rem 1rem;
  border: 1px solid color-mix(in srgb, var(--texto-secundario) 18%, transparent);
}

.admin-tab-header {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  white-space: nowrap;
}
</style>
