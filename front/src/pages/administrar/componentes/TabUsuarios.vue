<template>
  <div class="tab-usuarios">
    <BaseDataTable
      :items="lista"
      :loading="loading"
      :totalRecords="totalRecords"
      :first="first"
      :lazy="true"
      :reorderableColumns="true"
      @page="onPage"
      @sort="onSort"
    >
      <template #toolbar>
        <div class="table-toolbar">
          <div class="right">
            <Button icon="pi pi-refresh" text label="Atualizar" @click="atualizarLista" />
            <Button icon="pi pi-search" text label="Filtrar" @click="abrirFiltro" />
          </div>
        </div>
      </template>
      <template #columns>
        <Column
          field="id"
          columnKey="id"
          header="ID"
          style="width: 4.5rem; min-width: 4rem"
          sortable
        />
        <Column
          field="username"
          columnKey="username"
          header="Username"
          style="min-width: 13rem"
          sortable
        >
          <template #body="{ data }">
            <div class="username-cell">
              <span class="username-text">{{ data.username }}</span>
              <span v-if="data.is_superuser || data.is_staff || data.is_gerente" class="username-badges">
                <Tag
                  v-if="data.is_superuser"
                  value="Superuser"
                  severity="danger"
                  class="username-badge"
                />
                <Tag
                  v-if="data.is_staff"
                  value="Staff"
                  severity="warn"
                  class="username-badge"
                />
                <Tag
                  v-if="data.is_gerente"
                  value="Consultor"
                  severity="info"
                  class="username-badge"
                />
              </span>
            </div>
          </template>
        </Column>
        <Column
          field="gruposLabel"
          columnKey="grupos"
          header="Grupos"
          style="min-width: 10rem"
        >
          <template #body="{ data }">
            <div v-if="data.groups?.length" class="grupos-cell">
              <Tag
                v-for="g in data.groups"
                :key="g"
                :value="g"
                severity="secondary"
                class="grupo-tag"
              />
            </div>
            <span v-else class="grupos-vazio">—</span>
          </template>
        </Column>
        <Column
          field="email"
          columnKey="email"
          header="E-mail"
          style="min-width: 12rem"
          sortable
        />
        <Column
          field="nomeCompleto"
          sortField="first_name"
          columnKey="nomeCompleto"
          header="Nome e sobrenome"
          style="min-width: 11rem"
          sortable
        />
        <Column
          field="assinatura"
          sortField="assinatura__plano"
          columnKey="assinatura"
          header="Assinatura"
          style="min-width: 8rem"
          sortable
        >
          <template #body="{ data }">
            <Tag :value="labelAssinatura(data.assinatura)" :severity="tagAssinatura(data.assinatura)" />
          </template>
        </Column>
        <Column
          v-if="mostrarColunaAcoesUsuarios"
          header="Ações"
          columnKey="acoesUsuarios"
          style="min-width: 11.5rem; width: 11.5rem"
          :reorderableColumn="false"
        >
          <template #body="slotProps">
            <div class="acoes-linha">
              <Button
                v-if="caps.users.view"
                icon="pi pi-eye"
                text
                rounded
                title="Abrir app como este utilizador (novo separador)"
                aria-label="Ver como este utilizador"
                @click="abrirVisaoComoUtilizador(slotProps.data)"
              />
              <Button
                v-if="caps.users.change"
                icon="pi pi-pencil"
                text
                rounded
                title="Editar"
                aria-label="Editar utilizador"
                @click="editarUsuario(slotProps.data)"
              />
              <Button
                v-if="caps.users.delete"
                icon="pi pi-trash"
                text
                rounded
                severity="danger"
                title="Excluir (API em desenvolvimento)"
                aria-label="Excluir utilizador"
                @click="confirmarExclusao(slotProps.data)"
              />
            </div>
          </template>
        </Column>
      </template>
    </BaseDataTable>

    <DialogFiltroUsuarios
      v-model="visibleFiltro"
      :filtros-ativos="filtros"
      @apply="onFiltroApply"
      @clear="onFiltroClear"
    />

    <UsuarioDialog
      v-model="visibleUsuario"
      :usuario="usuarioEmEdicao"
      :loading="salvandoUsuario"
      @save="onUsuarioSave"
      @cancel="usuarioEmEdicao = null"
    />

    <DialogConfirma
      v-model="visibleExcluir"
      titulo="Excluir usuário?"
      mensagem="A exclusão de contas pelo painel ainda não está disponível na API."
      icone="pi pi-trash"
      tipo="danger"
      labelConfirmar="Fechar"
      labelCancelar="Cancelar"
      iconeConfirmar="pi pi-times"
      severityConfirmar="secondary"
      :loading="excluindo"
      @confirm="fecharDialogExclusao"
    />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import BaseDataTable from '@/components/BaseDataTable.vue'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import DialogFiltroUsuarios from '../dialogs/DialogFiltroUsuarios.vue'
import UsuarioDialog from '../dialogs/UsuarioDialog.vue'
import DialogConfirma from '@/components/DialogConfirma.vue'
import { PAGE_SIZE } from '@/constants/pagination'
import { drfOrderingFromPrimeSort } from '@/utils/primeLazySort'
import { labelAssinatura } from './usuariosAdminMock'
import { adminService } from '@/services/adminService'
import { useToast } from '@/utils/useToast'
import {
  FINANCAS_VIEW_AS_KIND_QUERY,
  FINANCAS_VIEW_AS_USER_QUERY,
  SUBJECT_VIEW_KIND
} from '@/constants/financasViewAs'
import { resolveAdminCapabilities } from '@/utils/adminCapabilities'

const store = useStore()
const toast = useToast()

const caps = computed(() => resolveAdminCapabilities(store.getters.getUser))

const mostrarColunaAcoesUsuarios = computed(
  () =>
    caps.value.users.view ||
    caps.value.users.change ||
    caps.value.users.delete
)

const loading = ref(false)
const lista = ref([])
const totalRecords = ref(0)
const filtros = ref({})
const ordering = ref(undefined)
const currentPage = ref(1)
const first = ref(0)
const visibleFiltro = ref(false)
const visibleUsuario = ref(false)
const usuarioEmEdicao = ref(null)
const salvandoUsuario = ref(false)
const visibleExcluir = ref(false)
const itemParaExcluir = ref(null)
const excluindo = ref(false)

function tagAssinatura (slug) {
  if (slug === 'premium') return 'success'
  if (slug === 'comum') return 'secondary'
  return 'secondary'
}

function mapApiUser (u) {
  const nomeCompleto =
    u.nome_completo ||
    [u.first_name, u.last_name].map((x) => (x || '').trim()).filter(Boolean).join(' ') ||
    '—'
  const groups = Array.isArray(u.groups) ? u.groups : []
  const group_ids = Array.isArray(u.group_ids)
    ? u.group_ids.map((x) => Number(x)).filter((n) => !Number.isNaN(n))
    : []
  return {
    id: u.id,
    username: u.username,
    email: u.email,
    first_name: u.first_name,
    last_name: u.last_name,
    is_staff: Boolean(u.is_staff),
    is_superuser: Boolean(u.is_superuser),
    is_gerente: Boolean(u.is_gerente),
    groups,
    group_ids,
    gruposLabel: groups.join(', '),
    nomeCompleto,
    assinatura: u.assinatura,
    assinatura_status: u.assinatura_status,
    current_period_end: u.current_period_end
  }
}

function buildQueryParams (page) {
  const f = filtros.value
  const params = { page }
  if (f.username?.trim()) params.username = f.username.trim()
  if (f.email?.trim()) params.email = f.email.trim()
  if (f.nome?.trim()) params.nome = f.nome.trim()
  if (f.assinatura) params.plano = f.assinatura
  if (f.tipoUsuario) params.tipo_usuario = f.tipoUsuario
  if (ordering.value) params.ordering = ordering.value
  return params
}

async function carregarLista (page = 1) {
  loading.value = true
  try {
    const data = await adminService.listUsers(buildQueryParams(page))
    lista.value = (data.results || []).map(mapApiUser)
    totalRecords.value = data.count ?? 0
    currentPage.value = page
    first.value = (page - 1) * PAGE_SIZE
  } catch (e) {
    const msg = e.response?.data?.detail || e.message || 'Erro ao carregar usuários.'
    toast.error('Lista de usuários', String(msg))
    lista.value = []
    totalRecords.value = 0
  } finally {
    loading.value = false
  }
}

function onPage (event) {
  const page = (event.page ?? 0) + 1
  carregarLista(page)
}

function onSort (event) {
  ordering.value = drfOrderingFromPrimeSort(event.sortField, event.sortOrder)
  first.value = 0
  carregarLista(1)
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
  ordering.value = undefined
  carregarLista(1)
}

function onFiltroClear () {
  filtros.value = {}
  first.value = 0
  ordering.value = undefined
  carregarLista(1)
}

/**
 * Novo separador com a app em modo finanças desse utilizador (JWT do staff +
 * cabeçalho X-Financas-Subject-User nas rotas /financas/).
 */
function abrirVisaoComoUtilizador (row) {
  if (!caps.value.users.view) return
  const basePath = import.meta.env.BASE_URL || '/'
  const path = basePath.endsWith('/') ? basePath : `${basePath}/`
  const url = new URL(path, window.location.origin)
  url.searchParams.set(FINANCAS_VIEW_AS_USER_QUERY, String(row.id))
  url.searchParams.set(FINANCAS_VIEW_AS_KIND_QUERY, SUBJECT_VIEW_KIND.ADMIN)
  window.open(url.toString(), '_blank', 'noopener,noreferrer')
}

function editarUsuario (row) {
  if (!caps.value.users.change) return
  usuarioEmEdicao.value = row
  visibleUsuario.value = true
}

watch(visibleUsuario, (aberto) => {
  if (!aberto) usuarioEmEdicao.value = null
})

function mensagemErroApi (e) {
  const d = e.response?.data
  if (!d) return e.message || 'Erro desconhecido.'
  if (typeof d === 'string') return d
  if (d.detail) {
    return Array.isArray(d.detail) ? d.detail.join(' ') : String(d.detail)
  }
  const partes = []
  for (const [k, v] of Object.entries(d)) {
    const msg = Array.isArray(v) ? v.join(' ') : String(v)
    partes.push(`${k}: ${msg}`)
  }
  return partes.join(' ') || 'Pedido inválido.'
}

async function onUsuarioSave (payload) {
  if (!caps.value.users.change) return
  salvandoUsuario.value = true
  try {
    await adminService.updateUser(payload.id, {
      email: payload.email,
      first_name: payload.first_name,
      last_name: payload.last_name,
      is_staff: payload.is_staff,
      is_superuser: payload.is_superuser,
      is_gerente: payload.is_gerente,
      group_ids: payload.group_ids,
      plano: payload.plano
    })
    toast.success('Utilizador', 'Alterações guardadas.')
    visibleUsuario.value = false
    usuarioEmEdicao.value = null
    await carregarLista(currentPage.value)
  } catch (e) {
    toast.error('Utilizador', mensagemErroApi(e))
  } finally {
    salvandoUsuario.value = false
  }
}

function confirmarExclusao (row) {
  if (!caps.value.users.delete) return
  itemParaExcluir.value = row
  visibleExcluir.value = true
}

watch(visibleExcluir, (v) => {
  if (!v) itemParaExcluir.value = null
})

function fecharDialogExclusao () {
  excluindo.value = true
  try {
    visibleExcluir.value = false
    itemParaExcluir.value = null
  } finally {
    excluindo.value = false
  }
}

onMounted(() => {
  carregarLista(1)
})
</script>

<style scoped>
.tab-usuarios {
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

.username-cell {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.5rem;
}

.username-text {
  font-weight: 500;
}

.username-badges {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.username-badge :deep(.p-tag) {
  font-size: 0.7rem;
  padding: 0.15rem 0.4rem;
}

.grupos-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.grupo-tag :deep(.p-tag) {
  font-size: 0.75rem;
}

.grupos-vazio {
  color: var(--texto-secundario);
}

.acoes-linha {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.15rem;
}
</style>
