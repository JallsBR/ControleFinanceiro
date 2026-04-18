import { computed } from 'vue'
import { useStore } from 'vuex'

/** Modo consultor a ver dados do cliente: só leitura na API e na UI. */
export function useFinancasSubjectReadOnly () {
  const store = useStore()
  const readOnly = computed(() => store.getters.subjectViewFinancasReadOnly)
  return { readOnly }
}
