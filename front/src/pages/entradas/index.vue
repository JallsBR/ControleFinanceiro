<template>
    <CardStatus
        tituloPrincipal="Entradas"
        subtitulo="Gerencie as suas receitas"
        icone="pi pi-wallet"
        :mostrarAcao="true"
        iconeAcao="pi pi-plus"
        @acao="abrirModalEntrada"
        style="margin-bottom: 1rem;"
    />

    <div class="table-toolbar">
        <div class="right">
            <Button icon="pi pi-refresh" text @click="atualizarLista" label="Atualizar" />
            <Button icon="pi pi-search" text @click="filtrarLista" label="Filtrar" />
        </div>
    </div>

    <BaseDataTable
      :items="lista"
      :loading="loading"
      :totalRecords="totalRecords"
      :first="first"
      @page="onPage"
    >
        <template #columns>
            <Column field="id" header="ID" style="width: 2rem" />
            <Column field="valor" header="Valor" style="width: 6rem">
                <template #body="{ data }">
                    {{ Money.format(data.valor) }}
                </template>
            </Column>
            <Column field="data" header="Data" style="width: 5rem">
                <template #body="{ data }">
                    {{ formatarData(data.data) }}
                </template>
            </Column>
            <Column field="categoria" header="Categoria" style="width: 13rem">
                <template #body="{ data }">
                    {{ nomeCategoria(data.categoria) }}
                </template>
            </Column>
            <Column field="descricao" header="Descrição" />
            <Column header="Ações" style="width: 8rem">
                <template #body="slotProps">
                    <Button icon="pi pi-pencil" text @click="editarMovimentacao(slotProps.data)" />
                    <Button icon="pi pi-trash" text severity="danger" @click="deletarMovimentacao(slotProps.data)" />
                </template>
            </Column>
        </template>
    </BaseDataTable>

    <DialogEntradas
      v-model:visible="visibleEntrada"
      :movimentacao="entradaEmEdicao"
      @saved="carregarLista"
    />

    <DialogConfirma
      v-model="visibleExcluir"
      titulo="Excluir entrada?"
      mensagem="Esta ação não pode ser desfeita. Deseja realmente excluir esta entrada?"
      icone="pi pi-trash"
      tipo="danger"
      labelConfirmar="Excluir"
      labelCancelar="Cancelar"
      iconeConfirmar="pi pi-trash"
      severityConfirmar="danger"
      :loading="excluindo"
      @confirm="executarExclusao"
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
import DialogEntradas from '@/pages/home/DialogEntradas.vue'
import DialogConfirma from '@/components/DialogConfirma.vue'

const visibleEntrada = ref(false)
const visibleExcluir = ref(false)
const itemParaExcluir = ref(null)
const excluindo = ref(false)
const entradaEmEdicao = ref(null)
const lista = ref([])
const loading = ref(false)
const totalRecords = ref(0)
const currentPage = ref(1)
const first = ref(0)
const categoriasMap = ref({})

const carregarCategorias = async () => {
  try {
    const data = await financasService.categorias.getAll({ tipo: 'E' })
    const arr = Array.isArray(data) ? data : (data?.results || data?.data || [])
    categoriasMap.value = Object.fromEntries((arr || []).map(c => [c.id, c.nome]))
  } catch (_) {
    categoriasMap.value = {}
  }
}

const carregarLista = async () => {
  loading.value = true
  try {
    const { data, total } = await financasService.movimentacoes.getPage(currentPage.value, { tipo: 'E' })
    lista.value = data
    totalRecords.value = total
  } catch (error) {
    console.error('Erro ao carregar entradas:', error)
    lista.value = []
    totalRecords.value = 0
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
  return categoriasMap.value[id] ?? id ?? '—'
}

function formatarData(val) {
  if (!val) return '—'
  const d = typeof val === 'string' ? val : (val?.split?.('T')?.[0] ?? '')
  if (!d) return '—'
  const [y, m, day] = d.split('-')
  return [day, m, y].filter(Boolean).join('/')
}

function abrirModalEntrada() {
  entradaEmEdicao.value = null
  visibleEntrada.value = true
}

function editarMovimentacao(item) {
  entradaEmEdicao.value = item
  visibleEntrada.value = true
}

watch(visibleEntrada, (v) => {
  if (!v) entradaEmEdicao.value = null
})

watch(visibleExcluir, (v) => {
  if (!v) itemParaExcluir.value = null
})

function atualizarLista() {
  carregarLista()
}

function filtrarLista() {
  carregarLista()
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
  } catch (error) {
    console.error('Erro ao excluir:', error)
  } finally {
    excluindo.value = false
  }
}

onMounted(async () => {
  await carregarCategorias()
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
</style>