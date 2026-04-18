<template>
    <CardStatus
        tituloPrincipal="Categorias"
        subtitulo="Gerencie as categorias de suas movimentações"
        icone="pi pi-tags"
        style="margin-bottom: 1rem;"
    />

    <div class="categorias-grid">
        <!-- Coluna Esquerda: Categorias de Entrada (E) -->
        <div class="coluna">
            <h2 class="coluna-titulo">Categorias de Entrada</h2>
            <div v-if="!readOnly" class="table-toolbar">
                <div class="right">
                    <Button icon="pi pi-plus" text label="Cadastrar nova categoria" @click="abrirNovaCategoria('E')" />
                </div>
            </div>
            <BaseDataTable
                :items="listaEntradas"
                :loading="loadingEntradas"
                :lazy="false"
                :reorderableColumns="true"
            >
                <template #columns>
                    <Column field="icone" columnKey="iconeE" header="Ícone" style="min-width: 4rem; max-width: 4rem">
                        <template #body="{ data }">
                            <i v-if="classeIcone(data.icone)" :class="classeIcone(data.icone)"></i>
                        </template>
                    </Column>
                    <Column field="nome" columnKey="nome" header="Nome" sortable />
                    <Column field="descricao" columnKey="descricao" header="Descrição" sortable />
                    <Column v-if="!readOnly" header="Ações" columnKey="acoesE" :reorderableColumn="false">
                        <template #body="slotProps">
                            <Button icon="pi pi-pencil" text @click="editarCategoria('E', slotProps.data)" />
                            <Button icon="pi pi-trash" text severity="danger" @click="deletarCategoria('E', slotProps.data)" />
                        </template>
                    </Column>
                </template>
            </BaseDataTable>
        </div>

        <!-- Coluna Direita: Categorias de Saída (S) -->
        <div class="coluna">
            <h2 class="coluna-titulo">Categorias de Saída</h2>
            <div v-if="!readOnly" class="table-toolbar">
                <div class="right">
                    <Button icon="pi pi-plus" text label="Cadastrar nova categoria" @click="abrirNovaCategoria('S')" />
                </div>
            </div>
            <BaseDataTable
                :items="listaSaidas"
                :loading="loadingSaidas"
                :lazy="false"
                :reorderableColumns="true"
            >
                <template #columns>
                    <Column field="icone" columnKey="iconeS" header="Ícone" style="min-width: 4rem; max-width: 4rem">
                        <template #body="{ data }">
                            <i v-if="classeIcone(data.icone)" :class="classeIcone(data.icone)"></i>
                        </template>
                    </Column>
                    <Column field="nome" columnKey="nome" header="Nome" sortable />
                    <Column field="descricao" columnKey="descricao" header="Descrição" sortable />
                    <Column v-if="!readOnly" header="Ações" columnKey="acoesS" :reorderableColumn="false">
                        <template #body="slotProps">
                            <Button icon="pi pi-pencil" text @click="editarCategoria('S', slotProps.data)" />
                            <Button icon="pi pi-trash" text severity="danger" @click="deletarCategoria('S', slotProps.data)" />
                        </template>
                    </Column>
                </template>
            </BaseDataTable>
        </div>
    </div>

    <DialogCategoria
        v-model:visible="visibleCategoria"
        :tipo="tipoCategoria"
        :categoria="categoriaEmEdicao"
        @saved="onCategoriaSalva"
    />

    <DialogConfirma
        v-model="visibleExcluir"
        :titulo="tituloExcluir"
        mensagem="Esta ação não pode ser desfeita. Deseja realmente excluir esta categoria?"
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
import { ref, onMounted, watch, computed } from 'vue'
import CardStatus from '@/components/CardStatus.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import Column from 'primevue/column'
import Button from 'primevue/button'
import financasService from '@/services/financasService'
import { useToast } from '@/utils/useToast'
import { useFinancasSubjectReadOnly } from '@/utils/useFinancasSubjectReadOnly'
import DialogCategoria from '@/pages/categorias/DialogCategoria.vue'
import DialogConfirma from '@/components/DialogConfirma.vue'

const toast = useToast()
const { readOnly } = useFinancasSubjectReadOnly()

const TIPO_E = 'E'
const TIPO_S = 'S'

// Estado do dialog de categoria
const visibleCategoria = ref(false)
const tipoCategoria = ref(TIPO_E)
const categoriaEmEdicao = ref(null)

// Coluna Entradas (E)
const listaEntradas = ref([])
const loadingEntradas = ref(false)

// Coluna Saídas (S)
const listaSaidas = ref([])
const loadingSaidas = ref(false)

// Ícones
const iconesMap = ref({})

// Exclusão
const visibleExcluir = ref(false)
const itemParaExcluir = ref(null)
const excluindo = ref(false)

const tituloExcluir = computed(() => {
  const t = itemParaExcluir.value?.tipo
  return t === TIPO_S ? 'Excluir categoria de saída?' : 'Excluir categoria de entrada?'
})

async function carregarEntradas() {
  loadingEntradas.value = true
  try {
    const data = await financasService.categorias.getAll({ tipo: TIPO_E })
    listaEntradas.value = Array.isArray(data) ? data : (data?.results || data?.data || [])
  } catch (error) {
    console.error('Erro ao carregar categorias de entrada:', error)
    listaEntradas.value = []
    toast.error('Erro', 'Não foi possível carregar as categorias de entrada.')
  } finally {
    loadingEntradas.value = false
  }
}

async function carregarSaidas() {
  loadingSaidas.value = true
  try {
    const data = await financasService.categorias.getAll({ tipo: TIPO_S })
    listaSaidas.value = Array.isArray(data) ? data : (data?.results || data?.data || [])
  } catch (error) {
    console.error('Erro ao carregar categorias de saída:', error)
    listaSaidas.value = []
    toast.error('Erro', 'Não foi possível carregar as categorias de saída.')
  } finally {
    loadingSaidas.value = false
  }
}

async function carregarIcones() {
  try {
    const arr = await financasService.icone.getAllFlat()
    iconesMap.value = Object.fromEntries((arr || []).map(i => [i.id, i.classe_css]))
  } catch (error) {
    console.error('Erro ao carregar ícones:', error)
    iconesMap.value = {}
    toast.error('Erro', 'Não foi possível carregar os ícones.')
  }
}

function classeIcone(id) {
  return id && iconesMap.value[id] ? iconesMap.value[id] : ''
}

function filtrarEntradas() {
  carregarEntradas()
}

function filtrarSaidas() {
  carregarSaidas()
}

function abrirNovaCategoria(tipo) {
  if (readOnly.value) return
  tipoCategoria.value = tipo
  categoriaEmEdicao.value = null
  visibleCategoria.value = true
}

function editarCategoria(tipo, item) {
  if (readOnly.value) return
  tipoCategoria.value = tipo
  categoriaEmEdicao.value = item
  visibleCategoria.value = true
}

function onCategoriaSalva() {
  if (tipoCategoria.value === TIPO_E) carregarEntradas()
  else carregarSaidas()
  toast.success('Categoria salva', '')
}

watch(visibleCategoria, (v) => {
  if (!v) categoriaEmEdicao.value = null
})

function deletarCategoria(tipo, item) {
  if (readOnly.value || !item?.id) return
  itemParaExcluir.value = { ...item, tipo }
  visibleExcluir.value = true
}

watch(visibleExcluir, (v) => {
  if (!v) itemParaExcluir.value = null
})

async function executarExclusao() {
  if (readOnly.value || !itemParaExcluir.value?.id) return
  excluindo.value = true
  try {
    await financasService.categorias.delete(itemParaExcluir.value.id)
    visibleExcluir.value = false
    const tipo = itemParaExcluir.value.tipo
    itemParaExcluir.value = null
    if (tipo === TIPO_E) await carregarEntradas()
    else await carregarSaidas()
    toast.success('Categoria excluída', '')
  } catch (error) {
    console.error('Erro ao excluir categoria:', error)
    toast.error('Erro', 'Não foi possível excluir a categoria.')
  } finally {
    excluindo.value = false
  }
}

onMounted(async () => {
  await Promise.all([carregarIcones(), carregarEntradas(), carregarSaidas()])
})
</script>

<style scoped>
.categorias-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 900px) {
  .categorias-grid {
    grid-template-columns: 1fr;
  }
}

.coluna {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.coluna-titulo {
  margin: 0 0 0.75rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--texto-primario);
}

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
