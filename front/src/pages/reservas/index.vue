<template>
    <CardStatus
        tituloPrincipal="Reservas"
        subtitulo="Gerencie as suas reservas"
        icone="pi pi-folder-plus"
        :mostrarAcao="!readOnly"
        iconeAcao="pi pi-plus"
        @acao="abrirModalReserva"
        style="margin-bottom: 1rem;"
    />

    <BaseDataTable
      :items="lista"
      :loading="loading"
      :totalRecords="totalRecords"
      :first="first"
      :reorderableColumns="true"
      @page="onPage"
    >
        <template #toolbar>
            <div class="table-toolbar">
                <div class="right">
                    <Button icon="pi pi-refresh" text @click="atualizarLista" label="Atualizar" />
                    <Button icon="pi pi-filter" text @click="abrirFiltro" label="Filtrar" />
                </div>
            </div>
        </template>
        <template #columns>
            <Column field="id" columnKey="id" header="ID" style="min-width: 3rem; max-width: 3rem" sortable />
            <Column field="nome" columnKey="nome" header="Nome" sortable />
            <Column field="valor" columnKey="valor" header="Valor" style="min-width: 7rem; max-width: 7rem" sortable>
                <template #body="{ data }">
                    {{ Money.format(data.valor) }}
                </template>
            </Column>
            <Column field="ativa" columnKey="ativa" header="Ativa" style="min-width: 6rem; max-width: 6rem" sortable>
                <template #body="{ data }">
                    <span :class="['reserva-status', data.ativa ? 'reserva-status--ativa' : 'reserva-status--inativa']">
                        {{ data.ativa ? 'Ativa' : 'Inativa' }}
                    </span>
                </template>
            </Column>
            <Column
              v-if="!readOnly"
              header="Ações"
              columnKey="acoesReservas"
              style="width: 8rem"
              :reorderableColumn="false"
            >
                <template #body="slotProps">
                    <Button icon="pi pi-pencil" text @click="editarReserva(slotProps.data)" />
                    <Button icon="pi pi-trash" text severity="danger" @click="deletarReserva(slotProps.data)" />
                </template>
            </Column>
        </template>
    </BaseDataTable>

    <DialogReserva
      v-model:visible="visibleReserva"
      :reserva="reservaEmEdicao"
      @saved="onReservaSalva"
    />

    <DialogConfirma
      v-model="visibleExcluir"
      titulo="Excluir reserva?"
      mensagem="Esta ação não pode ser desfeita. Deseja realmente excluir esta reserva?"
      icone="pi pi-trash"
      tipo="danger"
      labelConfirmar="Excluir"
      labelCancelar="Cancelar"
      iconeConfirmar="pi pi-trash"
      severityConfirmar="danger"
      :loading="excluindo"
      @confirm="executarExclusao"
    />

    <DialogFiltroReservas
      v-model="visibleFiltro"
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
import { useFinancasSubjectReadOnly } from '@/utils/useFinancasSubjectReadOnly'
import DialogConfirma from '@/components/DialogConfirma.vue'
import DialogReserva from '@/pages/reservas/DialogReserva.vue'
import DialogFiltroReservas from '@/components/DialogFiltroReservas.vue'

const toast = useToast()
const { readOnly } = useFinancasSubjectReadOnly()

const visibleReserva = ref(false)
const visibleExcluir = ref(false)
const visibleFiltro = ref(false)
const reservaEmEdicao = ref(null)
const itemParaExcluir = ref(null)
const excluindo = ref(false)

const lista = ref([])
const loading = ref(false)
const totalRecords = ref(0)
const currentPage = ref(1)
const first = ref(0)
const filtros = ref({})

const carregarLista = async () => {
  loading.value = true
  try {
    const { data, total } = await financasService.reservas.getPage(currentPage.value, filtros.value)
    lista.value = data
    totalRecords.value = total
  } catch (error) {
    console.error('Erro ao carregar reservas:', error)
    lista.value = []
    totalRecords.value = 0
    toast.error('Erro', 'Não foi possível carregar as reservas.')
  } finally {
    loading.value = false
  }
}

function onPage(event) {
  first.value = event.first
  currentPage.value = event.page + 1
  carregarLista()
}

function abrirModalReserva() {
  if (readOnly.value) return
  reservaEmEdicao.value = null
  visibleReserva.value = true
}

function editarReserva(item) {
  if (readOnly.value) return
  reservaEmEdicao.value = item
  visibleReserva.value = true
}

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

function onReservaSalva() {
  carregarLista()
  toast.success('Reserva salva', '')
}

function deletarReserva(item) {
  if (readOnly.value || !item?.id) return
  itemParaExcluir.value = item
  visibleExcluir.value = true
}

async function executarExclusao() {
  if (readOnly.value || !itemParaExcluir.value?.id) return
  excluindo.value = true
  try {
    await financasService.reservas.delete(itemParaExcluir.value.id)
    visibleExcluir.value = false
    itemParaExcluir.value = null
    await carregarLista()
    toast.success('Reserva excluída', '')
  } catch (error) {
    console.error('Erro ao excluir reserva:', error)
    toast.error('Erro', 'Não foi possível excluir a reserva.')
  } finally {
    excluindo.value = false
  }
}

watch(visibleReserva, (v) => {
  if (!v) reservaEmEdicao.value = null
})

watch(visibleExcluir, (v) => {
  if (!v) itemParaExcluir.value = null
})

onMounted(() => {
  carregarLista()
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

.reserva-status {
  display: inline-flex;
  align-items: center;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
}

.reserva-status--ativa {
  background: color-mix(in srgb, var(--sucesso) 20%, transparent);
  color: var(--sucesso);
}

.reserva-status--inativa {
  background: color-mix(in srgb, var(--perigo) 20%, transparent);
  color: var(--perigo);
}
</style>
