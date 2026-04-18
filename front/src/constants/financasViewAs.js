/** sessionStorage: id do utilizador cujas finanças estão a ser vistas. */
export const FINANCAS_VIEW_AS_USER_KEY = 'financas_view_as_user_id'

/** sessionStorage: ``admin`` | ``consultor``. */
export const FINANCAS_VIEW_AS_KIND_KEY = 'financas_view_as_kind'

/** sessionStorage: nome a mostrar no menu (opcional; URL-encoded). */
export const FINANCAS_VIEW_AS_DISPLAY_KEY = 'financas_view_as_display'

/** Query na URL ao abrir o separador (consumida pelo router). */
export const FINANCAS_VIEW_AS_USER_QUERY = 'viewAsUser'

/** Query: ``admin`` | ``consultor`` (omissão = admin para staff). */
export const FINANCAS_VIEW_AS_KIND_QUERY = 'viewAsKind'

/** Query: rótulo opcional para o menu (encodeURIComponent). */
export const FINANCAS_VIEW_AS_DISPLAY_QUERY = 'viewAsDisplay'

/** Modo de visualização subject (banner + API). */
export const SUBJECT_VIEW_KIND = Object.freeze({
  ADMIN: 'admin',
  CONSULTOR: 'consultor'
})

/**
 * Lê sessionStorage e devolve { kind, userId, displayName } ou null.
 * Compatível com sessões antigas só com user id (assume admin).
 */
export function readSubjectViewModeFromStorage () {
  try {
    const id = sessionStorage.getItem(FINANCAS_VIEW_AS_USER_KEY)
    if (!id || !/^\d+$/.test(id)) return null
    const rawKind = sessionStorage.getItem(FINANCAS_VIEW_AS_KIND_KEY)
    const kind =
      rawKind === SUBJECT_VIEW_KIND.CONSULTOR
        ? SUBJECT_VIEW_KIND.CONSULTOR
        : SUBJECT_VIEW_KIND.ADMIN
    let displayName = sessionStorage.getItem(FINANCAS_VIEW_AS_DISPLAY_KEY)
    if (displayName) {
      try {
        displayName = decodeURIComponent(displayName)
      } catch (_) {
        /* usar bruto */
      }
    } else {
      displayName = null
    }
    return { kind, userId: id, displayName: displayName || null }
  } catch (_) {}
  return null
}
