/**
 * Capacidades do painel Administrar (espelho de `admin_capabilities` no GET /auth/user).
 * `users` / `groups`: permissões Django view/add/change/delete sobre os modelos.
 */

function allCrudTrue () {
  return { view: true, add: true, change: true, delete: true }
}

function emptyCrud () {
  return { view: false, add: false, change: false, delete: false }
}

function mergeCrud (base, patch) {
  return { ...base, ...(patch || {}) }
}

/** @param {Record<string, unknown>|null|undefined} user — objeto `user` do Vuex */
export function resolveAdminCapabilities (user) {
  if (!user?.is_staff && !user?.is_superuser) {
    return {
      users: emptyCrud(),
      groups: emptyCrud(),
      group_permissions: false,
      view_financas_as_subject: false
    }
  }
  const c = user.admin_capabilities
  if (user.is_superuser || c?.superuser) {
    return {
      users: allCrudTrue(),
      groups: allCrudTrue(),
      group_permissions: true,
      view_financas_as_subject: true
    }
  }
  if (!c) {
    // Sessão antiga sem campo: comportamento permissivo até o próximo GET /auth/user
    return {
      users: allCrudTrue(),
      groups: allCrudTrue(),
      group_permissions: true,
      view_financas_as_subject: true
    }
  }
  return {
    users: mergeCrud(emptyCrud(), c.users),
    groups: mergeCrud(emptyCrud(), c.groups),
    group_permissions: Boolean(c.group_permissions),
    view_financas_as_subject: Boolean(c.view_financas_as_subject)
  }
}
