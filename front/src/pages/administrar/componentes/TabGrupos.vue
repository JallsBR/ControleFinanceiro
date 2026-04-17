<template>
  <div class="tab-grupos">
    <BaseDataTable
      :items="lista"
      :loading="loading"
      :totalRecords="totalRecords"
      :first="first"
      :lazy="true"
      :reorderableColumns="true"
      @page="onPage"
    >
      <template #toolbar>
        <div class="table-toolbar">
          <div class="right">
            <Button icon="pi pi-refresh" text label="Atualizar" @click="atualizarLista" />
            <Button icon="pi pi-search" text label="Filtrar" @click="abrirFiltro" />
            <Button icon="pi pi-plus" text label="Criar grupo" @click="abrirCriarGrupo" />
          </div>
        </div>
      </template>
      <template #columns>
        <Column
          field="name"
          columnKey="name"
          header="Nome"
          style="min-width: 14rem"
          sortable
        >
          <template #body="{ data }">
            {{ tituloGrupoComContagem(data) }}
          </template>
        </Column>
        <Column
          columnKey="usuariosGrupo"
          header="Usuários"
          style="min-width: 16rem; max-width: 28rem"
          :reorderableColumn="true"
        >
          <template #body="{ data }">
            <span class="usuarios-grupo-cell">{{ textoListaUsuarios(data) }}</span>
          </template>
        </Column>
        <Column
          field="permissions_count"
          columnKey="permissions_count"
          header="N.º permissões"
          style="min-width: 8rem"
          sortable
        />
        <Column
          header="Ações"
          columnKey="acoesGrupos"
          style="width: 10rem"
          :reorderableColumn="false"
        >
          <template #body="slotProps">
            <Button
              icon="pi pi-shield"
              text
              rounded
              title="Permissões do grupo"
              aria-label="Permissões do grupo"
              @click="abrirPermissoes(slotProps.data)"
            />
            <Button
              icon="pi pi-pencil"
              text
              rounded
              aria-label="Editar nome"
              @click="editarGrupo(slotProps.data)"
            />
          </template>
        </Column>
      </template>
    </BaseDataTable>

    <DialogFiltroGrupos
      v-model="visibleFiltro"
      :filtros-ativos="filtros"
      @apply="onFiltroApply"
      @clear="onFiltroClear"
    />

    <GrupoDialog
      v-model="visibleGrupo"
      :grupo="grupoFormulario"
      :loading="salvandoGrupo"
      @save="onGrupoSave"
      @cancel="grupoFormulario = null"
    />

    <GrupoPermissoesDialog
      v-model="visiblePermissoes"
      :grupo="grupoPermissoes"
      @saved="onPermissoesSaved"
      @cancel="grupoPermissoes = null"
    />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import Column from 'primevue/column'
import Button from 'primevue/button'
import DialogFiltroGrupos from '../dialogs/DialogFiltroGrupos.vue'
import GrupoDialog from '../dialogs/GrupoDialog.vue'
import GrupoPermissoesDialog from '../dialogs/GrupoPermissoesDialog.vue'
import { PAGE_SIZE } from '@/constants/pagination'
import { adminService } from '@/services/adminService'
import { useToast } from '@/utils/useToast'

const toast = useToast()

const loading = ref(false)
const lista = ref([])
const totalRecords = ref(0)
const filtros = ref({})
const currentPage = ref(1)
const first = ref(0)
const visibleFiltro = ref(false)
const visibleGrupo = ref(false)
const grupoFormulario = ref(null)
const salvandoGrupo = ref(false)
const visiblePermissoes = ref(false)
const grupoPermissoes = ref(null)

function mapApiGroup (g) {
  return {
    id: g.id,
    name: g.name,
    permissions_count: g.permissions_count ?? 0,
    users: Array.isArray(g.users) ? g.users : [],
    user_count: g.user_count ?? 0
  }
}

/** Ex.: Helpdesk (6 usuários) — o total fica junto ao nome do grupo. */
function tituloGrupoComContagem (row) {
  const n = Number(row.user_count) || 0
  const sufixo = n === 1 ? '1 usuário' : `${n} usuários`
  return `${row.name} (${sufixo})`
}

/** Só os nomes; reticências se a API mandou prévia e há mais membros. */
function textoListaUsuarios (row) {
  const total = Number(row.user_count) || 0
  if (!total) return '—'
  const names = (row.users || []).filter(Boolean)
  const head = names.join(', ')
  if (total > names.length) {
    return head ? `${head} …` : '…'
  }
  return head || '—'
}

function buildQueryParams (page) {
  const f = filtros.value
  const params = { page }
  if (f.nomeGrupo?.trim()) params.name = f.nomeGrupo.trim()
  return params
}

function mensagemErroApi (e) {
  const d = e.response?.data
  if (!d) return e.message || 'Erro desconhecido.'
  if (typeof d === 'string') return d
  if (d.detail) return Array.isArray(d.detail) ? d.detail.join(' ') : String(d.detail)
  const partes = []
  for (const [k, v] of Object.entries(d)) {
    partes.push(`${k}: ${Array.isArray(v) ? v.join(' ') : String(v)}`)
  }
  return partes.join(' ') || 'Pedido inválido.'
}

async function carregarLista (page = 1) {
  loading.value = true
  try {
    const data = await adminService.listGroups(buildQueryParams(page))
    lista.value = (data.results || []).map(mapApiGroup)
    totalRecords.value = data.count ?? 0
    currentPage.value = page
    first.value = (page - 1) * PAGE_SIZE
  } catch (e) {
    toast.error('Grupos', mensagemErroApi(e))
    lista.value = []
    totalRecords.value = 0
  } finally {
    loading.value = false
  }
}

function onPage (event) {
  carregarLista((event.page ?? 0) + 1)
}

function atualizarLista () {
  carregarLista(currentPage.value)
}

function abrirFiltro () {
  visibleFiltro.value = true
}

function onFiltroApply (novos) {
  filtros.value = { ...(novos || {}) }
  first.value = 0
  carregarLista(1)
}

function onFiltroClear () {
  filtros.value = {}
  first.value = 0
  carregarLista(1)
}

function abrirCriarGrupo () {
  grupoFormulario.value = null
  visibleGrupo.value = true
}

function editarGrupo (row) {
  grupoFormulario.value = { id: row.id, name: row.name }
  visibleGrupo.value = true
}

watch(visibleGrupo, (aberto) => {
  if (!aberto) grupoFormulario.value = null
})

async function onGrupoSave (payload) {
  salvandoGrupo.value = true
  try {
    if (payload.id != null) {
      await adminService.updateGroup(payload.id, { name: payload.name })
      toast.success('Grupo', 'Nome atualizado.')
    } else {
      await adminService.createGroup({ name: payload.name })
      toast.success('Grupo', 'Grupo criado.')
    }
    visibleGrupo.value = false
    grupoFormulario.value = null
    await carregarLista(payload.id != null ? currentPage.value : 1)
  } catch (e) {
    toast.error('Grupo', mensagemErroApi(e))
  } finally {
    salvandoGrupo.value = false
  }
}

function abrirPermissoes (row) {
  grupoPermissoes.value = { id: row.id, name: row.name }
  visiblePermissoes.value = true
}

watch(visiblePermissoes, (aberto) => {
  if (!aberto) grupoPermissoes.value = null
})

async function onPermissoesSaved () {
  await carregarLista(currentPage.value)
}

onMounted(() => {
  carregarLista(1)
})
</script>

<style scoped>
.tab-grupos {
  padding-top: 0.25rem;
}

.table-toolbar {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}

.table-toolbar .right {
  display: flex;
  gap: 0.5rem;
}

.usuarios-grupo-cell {
  display: inline-block;
  white-space: normal;
  word-break: break-word;
  line-height: 1.35;
}
</style>
