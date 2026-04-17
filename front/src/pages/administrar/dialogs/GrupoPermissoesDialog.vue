<template>
  <Dialog
    v-model:visible="visible"
    modal
    :closable="false"
    :dismissableMask="true"
    :closeOnEscape="true"
    :style="{ width: 'min(94vw, 76rem)' }"
  >
    <template #header>
      <div class="dialog-header">
        <h2 class="dialog-title">Permissões do grupo</h2>
        <p v-if="grupo" class="dialog-subtitle">{{ grupo.name }}</p>
      </div>
    </template>

    <div v-if="erroCarregar" class="erro-msg">{{ erroCarregar }}</div>

    <div v-else class="tree-wrap">
      <div v-if="loading" class="loading-msg">A carregar…</div>
      <template v-else>
        <div v-if="tree.length" class="toolbar-tree">
          <div class="toolbar-tree__left">
            <Button
              type="button"
              label="Abrir todos"
              icon="pi pi-angle-double-down"
              text
              size="small"
              @click="expandirTodos"
            />
            <Button
              type="button"
              label="Fechar todos"
              icon="pi pi-angle-double-up"
              text
              size="small"
              @click="colapsarTodos"
            />
          </div>
          <SelectButton
            v-model="filtroPermissoes"
            :options="filtroPermissoesOpcoes"
            option-label="label"
            option-value="value"
            size="small"
            class="toolbar-filtros-perms"
          />
        </div>

        <div class="split-grid">
          <aside class="panel panel--tree">
            <div class="panel-title">Árvore</div>
            <div class="tree-scroll tree-scroll--left">
              <div v-for="app in tree" :key="app.key" class="tree-app">
                <div class="tree-row tree-row--app">
                  <Button
                    type="button"
                    class="tree-chevron"
                    :icon="isAppExpanded(app.key) ? 'pi pi-chevron-down' : 'pi pi-chevron-right'"
                    text
                    rounded
                    :aria-expanded="isAppExpanded(app.key)"
                    :aria-label="isAppExpanded(app.key) ? 'Fechar secção' : 'Abrir secção'"
                    @click.stop="toggleExpandApp(app.key)"
                  />
                  <Checkbox
                    :input-id="`app-${app.key}`"
                    :binary="true"
                    :model-value="appAllSelected(app)"
                    :indeterminate="appIndeterminate(app)"
                    @update:model-value="(v) => toggleApp(app, Boolean(v))"
                  />
                  <label class="tree-label tree-label--app" :for="`app-${app.key}`">{{ app.label }}</label>
                </div>
                <div v-show="isAppExpanded(app.key)" class="tree-models">
                  <div v-for="model in app.children" :key="model.key" class="tree-model-block">
                    <div class="tree-row tree-row--model">
                      <Button
                        type="button"
                        class="tree-chevron tree-chevron--model"
                        :icon="isModelExpanded(model.key) ? 'pi pi-chevron-down' : 'pi pi-chevron-right'"
                        text
                        rounded
                        :aria-expanded="isModelExpanded(model.key)"
                        :aria-label="isModelExpanded(model.key) ? 'Fechar detalhe do modelo' : 'Abrir detalhe do modelo'"
                        @click.stop="toggleExpandModel(model.key)"
                      />
                      <Checkbox
                        :input-id="`model-${model.key}`"
                        :binary="true"
                        :model-value="modelAllSelected(model)"
                        :indeterminate="modelIndeterminate(model)"
                        @update:model-value="(v) => toggleModel(model, Boolean(v))"
                      />
                      <label class="tree-label tree-label--model" :for="`model-${model.key}`">{{ model.label }}</label>
                    </div>
                    <div v-show="isModelExpanded(model.key)" class="model-preview">
                      <span
                        v-for="p in model.permissions"
                        :key="p.id"
                        class="preview-chip"
                      >{{ p.codename }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </aside>

          <Divider layout="vertical" type="solid" class="split-divider-v" />

          <section class="panel panel--perms">
            <div class="panel-title">Permissões</div>
            <div class="tree-scroll tree-scroll--right">
              <p v-if="!permsFiltradas.length" class="perms-empty">{{ mensagemFiltroVazio }}</p>
              <div v-else class="perms-grid">
                <div
                  v-for="perm in permsFiltradas"
                  :key="perm.id"
                  class="perm-cell"
                >
                  <div class="tree-row tree-row--perm">
                    <Checkbox
                      :input-id="`perm-${perm.id}`"
                      :binary="true"
                      :model-value="selectedSet.has(perm.id)"
                      @update:model-value="(v) => togglePerm(perm.id, Boolean(v))"
                    />
                    <label class="tree-label tree-label--perm" :for="`perm-${perm.id}`">
                      <span class="perm-meta">{{ perm.appLabel }} › {{ perm.modelLabel }}</span>
                      <span class="perm-codename">{{ perm.codename }}</span>
                      <span class="perm-name">{{ perm.name }}</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </template>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <Button
          type="button"
          label="Cancelar"
          icon="pi pi-times"
          class="btn-cancelar-vermelho"
          severity="danger"
          :disabled="salvando"
          @click="fechar"
        />
        <Button
          type="button"
          label="Guardar"
          icon="pi pi-check"
          :loading="salvando"
          :disabled="loading || !grupo || !!erroCarregar"
          @click="guardar"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Divider from 'primevue/divider'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import SelectButton from 'primevue/selectbutton'
import { adminService } from '@/services/adminService'
import { useToast } from '@/utils/useToast'

const toast = useToast()

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  /** { id, name } */
  grupo: { type: Object, default: null }
})

const emit = defineEmits(['update:modelValue', 'saved', 'cancel'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const tree = ref([])
const selectedIds = ref([])
const loading = ref(false)
const salvando = ref(false)
const erroCarregar = ref('')
/** Apps com modelos visíveis na árvore. */
const expandedApps = ref(new Set())
/** Modelos com linha extra visível (reserva espaço para evolução; hoje só controla a seta). */
const expandedModels = ref(new Set())

/** Filtro da grelha à direita: ativas (marcadas), negadas (não marcadas), todas. */
const filtroPermissoes = ref('ativas')
const filtroPermissoesOpcoes = [
  { label: 'Permissões ativas', value: 'ativas' },
  { label: 'Permissões negadas', value: 'negadas' },
  { label: 'Todas as permissões', value: 'todas' }
]

const selectedSet = computed(() => new Set(selectedIds.value))

const flatPerms = computed(() => {
  const list = []
  for (const app of tree.value) {
    for (const model of app.children || []) {
      for (const perm of model.permissions || []) {
        list.push({
          id: perm.id,
          codename: perm.codename,
          name: perm.name,
          appLabel: app.label,
          modelLabel: model.label
        })
      }
    }
  }
  return list
})

const permsFiltradas = computed(() => {
  const all = flatPerms.value
  const sel = selectedSet.value
  if (filtroPermissoes.value === 'ativas') {
    return all.filter((p) => sel.has(p.id))
  }
  if (filtroPermissoes.value === 'negadas') {
    return all.filter((p) => !sel.has(p.id))
  }
  return all
})

const mensagemFiltroVazio = computed(() => {
  if (filtroPermissoes.value === 'ativas') {
    return 'Nenhuma permissão selecionada. Marque itens na grelha ou na árvore à esquerda.'
  }
  if (filtroPermissoes.value === 'negadas') {
    return 'O grupo já inclui todas as permissões — não há permissões “em falta”.'
  }
  return 'Sem permissões a mostrar.'
})

function isAppExpanded (key) {
  return expandedApps.value.has(key)
}

function isModelExpanded (key) {
  return expandedModels.value.has(key)
}

function toggleExpandApp (key) {
  const next = new Set(expandedApps.value)
  if (next.has(key)) next.delete(key)
  else next.add(key)
  expandedApps.value = next
}

function toggleExpandModel (key) {
  const next = new Set(expandedModels.value)
  if (next.has(key)) next.delete(key)
  else next.add(key)
  expandedModels.value = next
}

function expandirTodos () {
  const apps = new Set()
  const models = new Set()
  for (const a of tree.value) {
    apps.add(a.key)
    for (const m of a.children || []) {
      models.add(m.key)
    }
  }
  expandedApps.value = apps
  expandedModels.value = models
}

function colapsarTodos () {
  expandedApps.value = new Set()
  expandedModels.value = new Set()
}

function appAllSelected (app) {
  const ids = app.allPermissionIds || []
  return ids.length > 0 && ids.every((id) => selectedSet.value.has(id))
}

function appIndeterminate (app) {
  const ids = app.allPermissionIds || []
  const any = ids.some((id) => selectedSet.value.has(id))
  return any && !appAllSelected(app)
}

function modelAllSelected (model) {
  const ids = model.allPermissionIds || []
  return ids.length > 0 && ids.every((id) => selectedSet.value.has(id))
}

function modelIndeterminate (model) {
  const ids = model.allPermissionIds || []
  const any = ids.some((id) => selectedSet.value.has(id))
  return any && !modelAllSelected(model)
}

function setIds (mutate) {
  const s = new Set(selectedIds.value)
  mutate(s)
  selectedIds.value = [...s].sort((a, b) => a - b)
}

function togglePerm (id, checked) {
  setIds((s) => {
    if (checked) s.add(id)
    else s.delete(id)
  })
}

function toggleModel (model, checked) {
  const ids = model.allPermissionIds || []
  setIds((s) => {
    for (const id of ids) {
      if (checked) s.add(id)
      else s.delete(id)
    }
  })
}

function toggleApp (app, checked) {
  const ids = app.allPermissionIds || []
  setIds((s) => {
    for (const id of ids) {
      if (checked) s.add(id)
      else s.delete(id)
    }
  })
}

async function carregar () {
  erroCarregar.value = ''
  tree.value = []
  selectedIds.value = []
  colapsarTodos()
  if (!props.grupo?.id) return
  loading.value = true
  try {
    const [treeRes, permRes] = await Promise.all([
      adminService.getPermissionTree(),
      adminService.getGroupPermissions(props.grupo.id)
    ])
    tree.value = Array.isArray(treeRes.tree) ? treeRes.tree : []
    selectedIds.value = [...(permRes.permission_ids || [])].map(Number).filter((n) => !Number.isNaN(n))
    filtroPermissoes.value = 'ativas'
    expandirTodos()
  } catch (e) {
    erroCarregar.value =
      e.response?.data?.detail || e.message || 'Não foi possível carregar as permissões.'
    tree.value = []
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.modelValue, props.grupo?.id],
  ([aberto]) => {
    if (aberto && props.grupo?.id) {
      carregar()
    }
    if (!aberto) {
      erroCarregar.value = ''
      tree.value = []
      selectedIds.value = []
      filtroPermissoes.value = 'ativas'
      colapsarTodos()
    }
  }
)

function fechar () {
  emit('cancel')
  visible.value = false
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

async function guardar () {
  if (!props.grupo?.id) return
  salvando.value = true
  try {
    await adminService.setGroupPermissions(props.grupo.id, selectedIds.value)
    toast.success('Permissões', 'Alterações guardadas.')
    emit('saved')
    visible.value = false
  } catch (e) {
    toast.error('Permissões', mensagemErroApi(e))
  } finally {
    salvando.value = false
  }
}
</script>

<style scoped>
.dialog-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.dialog-title {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 600;
  color: var(--texto-primario);
}

.dialog-subtitle {
  margin: 0;
  font-size: 0.9rem;
  color: var(--texto-secundario);
}

.erro-msg {
  color: var(--perigo);
  font-size: 0.9rem;
  padding: 0.5rem 0;
}

.loading-msg {
  color: var(--texto-secundario);
  font-size: 0.9rem;
}

.tree-wrap {
  min-height: 4rem;
}

.toolbar-tree {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.65rem 1rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid color-mix(in srgb, var(--texto-secundario) 18%, transparent);
}

.toolbar-tree__left {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.5rem;
}

.toolbar-filtros-perms {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  justify-content: flex-end;
}

.toolbar-filtros-perms :deep(.p-selectbutton) {
  flex-wrap: wrap;
  justify-content: flex-end;
}

.toolbar-filtros-perms :deep(.p-togglebutton) {
  font-size: 0.78rem;
}

.split-grid {
  display: flex;
  align-items: stretch;
  width: 100%;
  gap: 0;
  min-height: min(58vh, 32rem);
}

.panel {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.panel--tree {
  flex: 0 0 28%;
  max-width: 20rem;
  padding-right: 0.5rem;
}

.panel--perms {
  flex: 1 1 0;
  min-width: 0;
  padding-left: 0.5rem;
}

.panel-title {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--texto-secundario);
  margin-bottom: 0.4rem;
}

.split-divider-v {
  flex: 0 0 auto;
  align-self: stretch;
  margin: 0;
}

:deep(.split-divider-v.p-divider-vertical) {
  min-height: 100%;
}

.tree-scroll {
  overflow: auto;
  padding-right: 0.25rem;
}

.tree-scroll--left {
  max-height: min(58vh, 32rem);
}

.tree-scroll--right {
  max-height: min(58vh, 32rem);
}

.tree-app {
  margin-bottom: 0.65rem;
}

.tree-models {
  margin-left: 0.25rem;
  padding-left: 0.35rem;
  border-left: 2px solid color-mix(in srgb, var(--texto-secundario) 22%, transparent);
}

.tree-model-block {
  margin: 0.25rem 0 0.35rem 0;
}

.model-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 0.2rem 0.35rem;
  margin: 0.2rem 0 0.35rem 1.85rem;
  max-height: 5.5rem;
  overflow: auto;
}

.preview-chip {
  font-family: ui-monospace, monospace;
  font-size: 0.65rem;
  padding: 0.08rem 0.28rem;
  border-radius: 4px;
  background: color-mix(in srgb, var(--texto-secundario) 14%, transparent);
  color: var(--texto-primario);
}

.tree-chevron {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  padding: 0;
  color: var(--texto-secundario);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.tree-chevron :deep(.p-button) {
  width: 2rem;
  height: 2rem;
  min-width: 2rem;
  min-height: 2rem;
  padding: 0;
  margin: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.tree-chevron--model {
  width: 1.75rem;
  height: 1.75rem;
}

.tree-chevron--model :deep(.p-button) {
  width: 1.75rem;
  height: 1.75rem;
  min-width: 1.75rem;
  min-height: 1.75rem;
}

.tree-row {
  display: flex;
  align-items: flex-start;
  gap: 0.35rem;
}

.tree-row--app,
.tree-row--model {
  align-items: center;
}

.tree-row--app :deep(.p-checkbox),
.tree-row--model :deep(.p-checkbox) {
  display: inline-flex;
  align-items: center;
  line-height: 0;
}

.tree-row--app :deep(.p-checkbox .p-checkbox-box),
.tree-row--model :deep(.p-checkbox .p-checkbox-box) {
  margin: 0;
}

.tree-row--app {
  margin-bottom: 0.15rem;
}

.tree-row--model {
  padding-left: 0.15rem;
}

.tree-label {
  cursor: pointer;
  font-size: 0.88rem;
  line-height: 1.35;
  color: var(--texto-primario);
  padding-top: 0.15rem;
  min-width: 0;
}

.tree-row--app .tree-label,
.tree-row--model .tree-label {
  padding-top: 0;
  align-self: center;
}

.tree-label--app {
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  font-size: 0.78rem;
}

.tree-label--model {
  font-weight: 600;
  font-size: 0.82rem;
}

.perms-empty {
  margin: 0;
  padding: 1rem 0.25rem;
  font-size: 0.9rem;
  color: var(--texto-secundario);
  line-height: 1.45;
}

.perms-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.5rem 0.85rem;
  align-content: start;
}

.perm-cell {
  min-width: 0;
  border-radius: 8px;
  padding: 0.35rem 0.25rem;
  background: color-mix(in srgb, var(--bg-primario) 88%, transparent);
}

.tree-row--perm {
  align-items: flex-start;
}

.tree-label--perm {
  display: flex;
  flex-direction: column;
  gap: 0.12rem;
  padding-top: 0.05rem;
}

.perm-meta {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--texto-secundario);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.perm-codename {
  font-family: ui-monospace, monospace;
  font-size: 0.75rem;
  color: var(--texto-secundario);
}

.perm-name {
  font-size: 0.78rem;
  color: var(--texto-secundario);
  line-height: 1.3;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-cancelar-vermelho :deep(.p-button) {
  background: var(--perigo);
  color: var(--texto-primario);
}

.btn-cancelar-vermelho :deep(.p-button:hover) {
  background: color-mix(in srgb, var(--perigo) 85%, black);
  color: var(--texto-primario);
}

@media (max-width: 900px) {
  .split-grid {
    flex-direction: column;
    min-height: 0;
  }

  .panel--tree {
    flex: none;
    max-width: none;
    width: 100%;
    padding-right: 0;
    padding-bottom: 0.5rem;
  }

  .panel--perms {
    padding-left: 0;
    padding-top: 0.5rem;
    border-top: 1px solid color-mix(in srgb, var(--texto-secundario) 18%, transparent);
  }

  .split-divider-v {
    display: none;
  }

  .perms-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .tree-scroll--left,
  .tree-scroll--right {
    max-height: 40vh;
  }
}

@media (max-width: 520px) {
  .perms-grid {
    grid-template-columns: 1fr;
  }
}
</style>
