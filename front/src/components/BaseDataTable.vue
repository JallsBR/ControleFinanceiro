<template>
    <div class="table-wrapper">
      <DataTable
        :value="items"
        :loading="loading"
        :paginator="true"
        :rows="rows"
        :first="first"
        :totalRecords="totalRecords"
        :lazy="lazy"
        :reorderableColumns="reorderableColumns"
        stripedRows
        showGridlines
        responsiveLayout="scroll"
        :dataKey="dataKey"
        :rowHover="true"
        v-model:expandedRows="expandedRows"
        @rowClick="$emit('rowClick', $event)"
        @rowSelect="$emit('rowSelect', $event)"
        @page="$emit('page', $event)"
        v-model:selection="selection"
      >
        <template #header>
          <div class="table-header">
            <slot
              name="toolbar"
              :filters="filters"
              :aplicarBusca="aplicarBusca"
              :limparBusca="limparBusca"
            />
          </div>
        </template>
        <slot name="columns" />

        <template #empty>
          <div class="text-center py-4">
            Nenhum registro encontrado.
          </div>
        </template>

        <template #expansion="slotProps">
          <slot name="expansion" :data="slotProps.data" />
        </template>
      </DataTable>
      <div class="table-footer">
        {{ contagemTexto }}
      </div>
    </div>
  </template>

  <script setup>
  import { ref, computed } from 'vue'
  import DataTable from 'primevue/datatable'
  import { PAGE_SIZE } from '@/constants/pagination'

  const props = defineProps({
    items: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    dataKey: { type: String, default: 'id' },
    /** Total de registros (backend). Usado pelo paginador em modo lazy. */
    totalRecords: { type: Number, default: 0 },
    /** Índice do primeiro registro da página atual (para modo lazy). */
    first: { type: Number, default: 0 },
    /** Linhas por página. Padrão: constante da app (10). */
    rows: { type: Number, default: PAGE_SIZE },
    /** Quando true, espera paginação/sort no backend. Quando false, DataTable faz tudo no client. */
    lazy: { type: Boolean, default: true },
    /** Habilita arrastar colunas para reordenar. */
    reorderableColumns: { type: Boolean, default: false }
  })

  const emit = defineEmits(['rowClick', 'rowSelect', 'page', 'filterApply', 'filterClear'])

  const selection = ref([])
  const expandedRows = ref({})
  const filters = ref({})

  const aplicarBusca = () => {
    emit('filterApply', filters.value)
  }

  const limparBusca = () => {
    filters.value = {}
    emit('filterClear')
  }

  const contagemTexto = computed(() => {
    const total = props.lazy ? props.totalRecords : (props.items?.length ?? 0)
    return total === 1 ? '1 registro' : `${total} registros`
  })
  </script>
  
  <style scoped>
  .table-wrapper {
    background: var(--bg-secundario);
    border-radius: 18px;
    padding: 20px;
  }

  .table-header {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 0.75rem;
  }

  .table-footer {
    margin-top: 0.75rem;
    font-size: 0.875rem;
    color: var(--texto-secundario);
  }

  /* Altura uniforme: cabeçalho e linhas de dados com o mesmo espaço vertical */
  :deep(.p-datatable thead th),
  :deep(.p-datatable tbody td) {
    padding-top: 0.625rem;
    padding-bottom: 0.625rem;
    min-height: 2.5rem;
    vertical-align: middle;
    box-sizing: border-box;
  }
  </style>