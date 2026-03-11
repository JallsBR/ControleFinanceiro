<template>
    <CardStatus
        tituloPrincipal="Saídas"
        subtitulo="Gerencie os seus gastos"
        icone="pi pi-credit-card"
        :mostrarAcao="true"
        iconeAcao="pi pi-minus"
        @acao="abrirModalSaida"
        style="margin-bottom: 1rem;"
    />

    <BaseDataTable
      :items="lista"
      :loading="loading"
      :totalRecords="totalRecords"
      :first="first"
      :lazy="false"
      :reorderableColumns="true"
      @page="onPage"
    >
        <template #toolbar>
            <div class="table-toolbar">
                <div class="right">
                    <Button icon="pi pi-refresh" text @click="atualizarLista" label="Atualizar" />
                    <Button icon="pi pi-search" text @click="abrirFiltro" label="Filtrar" />
                </div>
            </div>
        </template>
        <template #columns>
            <Column field="id" columnKey="id" header="ID" style="min-width: 1.5rem; max-width: 1.5rem" sortable />
            <Column field="valor" columnKey="valor" header="Valor" style="min-width: 2rem; max-width: 2rem" sortable>
                <template #body="{ data }">
                    {{ Money.format(data.valor) }}
                </template>
            </Column>
            <Column field="data" columnKey="data" header="Data" style="min-width: 2rem; max-width: 2rem" sortable>
                <template #body="{ data }">
                    {{ formatarData(data.data) }}
                </template>
            </Column>
            <Column field="categoria" columnKey="categoria" header="Categoria" style="min-width: 4rem; max-width: 4rem" sortable>
                <template #body="{ data }">
                    <span class="categoria-cell">
                        <i
                          v-if="classeIconeCategoria(data.categoria)"
                          :class="classeIconeCategoria(data.categoria)"
                          class="categoria-cell__icon"
                        />
                        <span>{{ nomeCategoria(data.categoria) }}</span>
                    </span>
                </template>
            </Column>
            <Column field="descricao" columnKey="descricao" header="Descrição" sortable />
            <Column header="Ações" columnKey="acoesSaidas" style="width: 8rem" :reorderableColumn="false">
                <template #body="slotProps">
                    <Button icon="pi pi-pencil" text @click="editarMovimentacao(slotProps.data)" />
                    <Button icon="pi pi-trash" text severity="danger" @click="deletarMovimentacao(slotProps.data)" />
                </template>
            </Column>
        </template>
    </BaseDataTable>

    <DialogSaida
      v-model:visible="visibleSaida"
      :movimentacao="saidaEmEdicao"
      @saved="onSaidaSalva"
    />

    <DialogConfirma
      v-model="visibleExcluir"
      titulo="Excluir saída?"
      mensagem="Esta ação não pode ser desfeita. Deseja realmente excluir esta saída?"
      icone="pi pi-trash"
      tipo="danger"
      labelConfirmar="Excluir"
      labelCancelar="Cancelar"
      iconeConfirmar="pi pi-trash"
      severityConfirmar="danger"
      :loading="excluindo"
      @confirm="executarExclusao"
    />

    <DialogFiltroMovimentacoes
      v-model="visibleFiltro"
      tipo="S"
      @apply="onFiltroApply"
      @clear="onFiltroClear"
    />
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import CardStatus from '@/components/CardStatus.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Money from '@/utils/Money.js'
import financasService from '@/services/financasService'
import { useToast } from '@/utils/useToast'
import DialogSaida from '@/pages/home/DialogSaida.vue'
import DialogConfirma from '@/components/DialogConfirma.vue'
import DialogFiltroMovimentacoes from '@/components/DialogFiltroMovimentacoes.vue'

const toast = useToast()

const visibleSaida = ref(false)
const visibleExcluir = ref(false)
const visibleFiltro = ref(false)
const itemParaExcluir = ref(null)
const excluindo = ref(false)
const saidaEmEdicao = ref(null)
const lista = ref([])
const loading = ref(false)
const totalRecords = ref(0)
const currentPage = ref(1)
const first = ref(0)
const filtros = ref({})
const categoriasMap = ref({})
const iconesMap = ref({})

const carregarCategorias = async () => {
  try {
    const data = await financasService.categorias.getAll({ tipo: 'S' })
    const arr = Array.isArray(data) ? data : (data?.results || data?.data || [])
    categoriasMap.value = Object.fromEntries((arr || []).map(c => [c.id, c]))
  } catch (_) {
    categoriasMap.value = {}
  }
}

const carregarIcones = async () => {
  try {
    const arr = await financasService.icone.getAllFlat()
    iconesMap.value = Object.fromEntries((arr || []).map(i => [i.id, i.classe_css]))
  } catch (error) {
    console.error('Erro ao carregar ícones:', error)
    iconesMap.value = {}
  }
}

const carregarLista = async () => {
  loading.value = true
  try {
    const { data, total } = await financasService.movimentacoes.getPage(currentPage.value, { tipo: 'S', ...filtros.value })
    lista.value = data
    totalRecords.value = total
  } catch (error) {
    console.error('Erro ao carregar saídas:', error)
    lista.value = []
    totalRecords.value = 0
    toast.error('Erro', 'Não foi possível carregar as saídas.')
  } finally {
    loading.value = false
  }
}

function onPage(event) {
  first.value = event.first
  currentPage.value = event.page + 1
  carregarLista()
}

function nomeCategoria(id) {
  const cat = categoriasMap.value[id]
  return cat?.nome ?? id ?? '—'
}

function classeIconeCategoria(id) {
  const cat = categoriasMap.value[id]
  if (!cat || !cat.icone) return ''
  return iconesMap.value[cat.icone] || ''
}

function formatarData(val) {
  if (!val) return '—'
  const d = typeof val === 'string' ? val : (val?.split?.('T')?.[0] ?? '')
  if (!d) return '—'
  const [y, m, day] = d.split('-')
  return [day, m, y].filter(Boolean).join('/')
}

function abrirModalSaida() {
  saidaEmEdicao.value = null
  visibleSaida.value = true
}

function editarMovimentacao(item) {
  saidaEmEdicao.value = item
  visibleSaida.value = true
}

watch(visibleSaida, (v) => {
  if (!v) saidaEmEdicao.value = null
})

watch(visibleExcluir, (v) => {
  if (!v) itemParaExcluir.value = null
})

function atualizarLista() {
  carregarLista()
}

function abrirFiltro() {
  visibleFiltro.value = true
}

function onFiltroApply(novosFiltros) {
  filtros.value = novosFiltros || {}
  currentPage.value = 1
  carregarLista()
}

function onFiltroClear() {
  filtros.value = {}
  currentPage.value = 1
  carregarLista()
}

function onSaidaSalva() {
  carregarLista()
  toast.success('Saída salva', '')
}

function deletarMovimentacao(item) {
  if (!item?.id) return
  itemParaExcluir.value = item
  visibleExcluir.value = true
}

async function executarExclusao() {
  if (!itemParaExcluir.value?.id) return
  excluindo.value = true
  try {
    await financasService.movimentacoes.delete(itemParaExcluir.value.id)
    visibleExcluir.value = false
    itemParaExcluir.value = null
    await carregarLista()
    toast.success('Saída excluída', '')
  } catch (error) {
    console.error('Erro ao excluir:', error)
    toast.error('Erro', 'Não foi possível excluir a saída.')
  } finally {
    excluindo.value = false
  }
}

onMounted(async () => {
  await Promise.all([carregarIcones(), carregarCategorias()])
  await carregarLista()
})
</script>

<style scoped>
.table-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}
.table-toolbar .right {
  display: flex;
  gap: 0.5rem;
}

.categoria-cell {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.categoria-cell__icon {
  font-size: 1rem;
}
</style>
