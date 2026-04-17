/** Opções de filtro da coluna Assinatura (plano no backend). */
export const ASSINATURA_FILTRO_OPCOES = [
  { label: 'Comum', value: 'comum' },
  { label: 'Premium', value: 'premium' }
]

export function labelAssinatura (slug) {
  const o = ASSINATURA_FILTRO_OPCOES.find((x) => x.value === slug)
  return o?.label ?? (slug || '—')
}
