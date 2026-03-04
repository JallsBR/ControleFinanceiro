<template>
    <div class="table-wrapper">
      <DataTable
        :value="items"
        :loading="loading"
        :paginator="true"
        :rows="rows"
        :first="first"
        :totalRecords="totalRecords"
        :lazy="true"
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
  import { ref } from 'vue'
  import DataTable from 'primevue/datatable'
  import { PAGE_SIZE } from '@/constants/pagination'

  defineProps({
    items: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    dataKey: { type: String, default: 'id' },
    /** Total de registros (backend). Usado pelo paginador. */
    totalRecords: { type: Number, default: 0 },
    /** Índice do primeiro registro da página atual (para modo lazy). */
    first: { type: Number, default: 0 },
    /** Linhas por página. Padrão: constante da app (10). */
    rows: { type: Number, default: PAGE_SIZE }
  })

  defineEmits(['rowClick', 'rowSelect', 'page'])

  const selection = ref([])
  const expandedRows = ref({})
  </script>
  
  <style scoped>
  .table-wrapper {
    background: #1f242d;
    border-radius: 18px;
    padding: 20px;
  }
  </style>