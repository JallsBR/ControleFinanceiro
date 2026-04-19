/**
 * Converte `sortField` / `sortOrder` do evento `@sort` do PrimeVue DataTable em modo lazy
 * para o parâmetro `ordering` do Django REST Framework (`?ordering=-campo`).
 *
 * @param {string|null|undefined} sortField
 * @param {number|null|undefined} sortOrder — 1 = asc, -1 = desc (PrimeVue 4)
 * @returns {string|undefined}
 */
export function drfOrderingFromPrimeSort (sortField, sortOrder) {
  if (sortField == null || sortField === '') return undefined
  if (sortOrder == null || sortOrder === 0) return undefined
  return sortOrder === -1 ? `-${sortField}` : String(sortField)
}
