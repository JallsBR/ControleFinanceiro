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
            <span class="table-count">{{ contagemTexto }}</span>
            <div class="table-header__toolbar">
              <slot
                name="toolbar"
                :filters="filters"
                :aplicarBusca="aplicarBusca"
                :limparBusca="limparBusca"
              />
            </div>
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

  /* Uma faixa: total (metadado) à esquerda, ações à direita + linha divisória leve */
  .table-header {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem 1rem;
    padding-bottom: 0.6rem;
    margin-bottom: 0.2rem;
    border-bottom: 1px solid color-mix(in srgb, var(--texto-secundario) 16%, transparent);
  }

  .table-header__toolbar {
    flex: 1;
    display: flex;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: 0.5rem;
    min-width: 0;
  }

  .table-count {
    flex-shrink: 0;
    font-size: 0.8125rem;
    font-weight: 500;
    color: var(--texto-secundario);
    letter-spacing: 0.02em;
    white-space: nowrap;
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