/**
 * Destino após login/cadastro automático, conforme `pagina_inicial` e permissões.
 */
export function routeLocationAfterLogin (user) {
  if (!user || typeof user !== 'object') {
    return { name: 'home' }
  }
  const v = String(user.pagina_inicial || 'dashboard').trim().toLowerCase()
  const staff = Boolean(user.is_staff || user.is_superuser)
  const consultor = Boolean(user.is_gerente)

  if (v === 'relatorio') return { name: 'relatorio' }
  if (v === 'administrar' && staff) return { name: 'administrar' }
  if (v === 'consultoria' && consultor) return { name: 'consultoria' }
  return { name: 'home' }
}
