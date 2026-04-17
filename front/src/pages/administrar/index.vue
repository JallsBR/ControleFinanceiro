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
          <Tab value="usuarios">
            <span class="admin-tab-header">
              <i class="pi pi-users" aria-hidden="true" />
              Usuários
            </span>
          </Tab>
          <Tab value="grupos">
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
          <TabPanel value="usuarios">
            <TabUsuarios />
          </TabPanel>
          <TabPanel value="grupos">
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
import { ref } from 'vue'
import CardStatus from '@/components/CardStatus.vue'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import TabUsuarios from './componentes/TabUsuarios.vue'
import TabGrupos from './componentes/TabGrupos.vue'
import TabDashboard from './componentes/TabDashboard.vue'

const abaAtiva = ref('usuarios')
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
