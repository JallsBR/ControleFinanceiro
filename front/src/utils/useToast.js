/**
 * Composable para usar o Toast do PrimeVue.
 * Facilita exibir mensagens com severidade (success, error, warn, info).
 *
 * Exemplo de uso (Composition API):
 *   import { useToast } from '@/utils/useToast'
 *   const toast = useToast()
 *   toast.success('Sucesso!', 'Operação concluída')
 *   toast.error('Erro!', 'Algo deu errado')
 *
 * Ou via Options API: this.$toast.add({ severity: 'success', ... })
 */
import { useToast as usePrimeToast } from 'primevue/usetoast'

export function useToast() {
  const toast = usePrimeToast()

  return {
    success: (summary, detail = '') => {
      toast.add({ severity: 'success', summary, detail, life: 4000 })
    },
    error: (summary, detail = '') => {
      toast.add({ severity: 'error', summary, detail, life: 6000 })
    },
    warn: (summary, detail = '') => {
      toast.add({ severity: 'warn', summary, detail, life: 5000 })
    },
    info: (summary, detail = '') => {
      toast.add({ severity: 'info', summary, detail, life: 4000 })
    },
    add: toast.add,
    remove: toast.remove,
    removeGroup: toast.removeGroup,
    removeAllGroups: toast.removeAllGroups,
    clear: () => toast.removeAllGroups()
  }
}
