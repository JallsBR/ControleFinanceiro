import api from '@/services/APIService'

/**
 * Painel administrativo (`/api/v1/auth/admin/...`).
 */
export const adminService = {
  /**
   * Lista usuários com assinatura (paginação DRF: count, results).
   * @param {Object} params — page, username, email, nome, plano (comum|premium), tipo_usuario (superuser|staff|comum)
   */
  async listUsers (params = {}) {
    const { data } = await api.get('/auth/admin/users', { params })
    return data
  },

  /**
   * Detalhe de um utilizador (admin).
   * @param {number|string} id
   */
  async getUser (id) {
    const { data } = await api.get(`/auth/admin/users/${id}`)
    return data
  },

  /**
   * Atualiza utilizador e opcionalmente o plano da assinatura (PATCH).
   * @param {number|string} id
   * @param {Object} payload — email, first_name, last_name, is_staff, is_superuser, plano
   */
  async updateUser (id, payload) {
    const { data } = await api.patch(`/auth/admin/users/${id}`, payload)
    return data
  },

  /** Árvore de permissões Django (app → modelo → permissões). */
  async getPermissionTree () {
    const { data } = await api.get('/auth/admin/permissions/tree')
    return data
  },

  /** Lista grupos (paginação DRF). Query: `name` (icontains). */
  async listGroups (params = {}) {
    const { data } = await api.get('/auth/admin/groups', { params })
    return data
  },

  /** Lista `{ id, name }[]` para selects (até 500 grupos). */
  async getGroupOptions () {
    const { data } = await api.get('/auth/admin/groups/options')
    return data
  },

  async createGroup (payload) {
    const { data } = await api.post('/auth/admin/groups', payload)
    return data
  },

  async updateGroup (id, payload) {
    const { data } = await api.patch(`/auth/admin/groups/${id}`, payload)
    return data
  },

  async deleteGroup (id) {
    await api.delete(`/auth/admin/groups/${id}`)
  },

  async getGroupPermissions (id) {
    const { data } = await api.get(`/auth/admin/groups/${id}/permissions`)
    return data
  },

  async setGroupPermissions (id, permissionIds) {
    const { data } = await api.put(`/auth/admin/groups/${id}/permissions`, {
      permission_ids: permissionIds
    })
    return data
  }
}
