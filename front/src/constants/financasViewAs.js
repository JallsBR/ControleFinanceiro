/** sessionStorage: staff a ver dados de outro utilizador (separador dedicado). */
export const FINANCAS_VIEW_AS_USER_KEY = 'financas_view_as_user_id'

/** Query na URL ao abrir o separador (consumida pelo router). */
export const FINANCAS_VIEW_AS_USER_QUERY = 'viewAsUser'

/** Modo de visualização subject (banner + API); consultor será ligado depois. */
export const SUBJECT_VIEW_KIND = Object.freeze({
  ADMIN: 'admin',
  CONSULTOR: 'consultor'
})

/** Lê sessionStorage e devolve modo admin se ativo; caso contrário null. */
export function readSubjectViewModeFromStorage () {
  try {
    const id = sessionStorage.getItem(FINANCAS_VIEW_AS_USER_KEY)
    if (id && /^\d+$/.test(id)) {
      return { kind: SUBJECT_VIEW_KIND.ADMIN, userId: id }
    }
  } catch (_) {}
  return null
}
