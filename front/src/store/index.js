import { createStore } from 'vuex'
import api from '../services/APIService'
import {
  FINANCAS_VIEW_AS_USER_KEY,
  readSubjectViewModeFromStorage,
  SUBJECT_VIEW_KIND
} from '@/constants/financasViewAs'

export default createStore({
  state: {
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('access') || null,
    loading: false,
    /** { kind, userId } | null — alinhado com sessionStorage (modo ver como). */
    subjectViewMode: readSubjectViewModeFromStorage(),
    /** Perfil admin GET do utilizador monitorizado (só modo admin). */
    subjectMonitoredUser: null
  },

  getters: {
    isAuthenticated: state => !!state.token,
    getUser: state => state.user,
    isLoading: state => state.loading,
    subjectViewAdminActive: (state) =>
      state.subjectViewMode?.kind === SUBJECT_VIEW_KIND.ADMIN,
    subjectViewConsultorActive: (state) =>
      state.subjectViewMode?.kind === SUBJECT_VIEW_KIND.CONSULTOR,
    getSubjectMonitoredUser: (state) => state.subjectMonitoredUser
  },

  mutations: {
    SET_LOADING(state, value) {
      state.loading = value
    },

    SET_AUTH(state, { user, access, refresh }) {
      state.user = user
      state.token = access

      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
      localStorage.setItem('user', JSON.stringify(user))
    },

    LOGOUT(state) {
      state.user = null
      state.token = null
      state.subjectViewMode = null
      state.subjectMonitoredUser = null

      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      localStorage.removeItem('user')
      try {
        sessionStorage.removeItem(FINANCAS_VIEW_AS_USER_KEY)
      } catch (_) {}
    },

    SET_SUBJECT_VIEW_MODE (state, payload) {
      state.subjectViewMode = payload || null
      if (!payload) {
        state.subjectMonitoredUser = null
      }
    },

    SET_SUBJECT_MONITORED_USER (state, payload) {
      state.subjectMonitoredUser = payload || null
    },

    /** Mescla dados do usuário após atualizar perfil (mantém is_staff etc.). */
    UPDATE_USER (state, user) {
      if (!user) return
      state.user = { ...(state.user || {}), ...user }
      try {
        localStorage.setItem('user', JSON.stringify(state.user))
      } catch (_) {}
    }
  },

  actions: {
    async login({ commit }, { login, email, password }) {
      try {
        commit('SET_LOADING', true)

        const identifier = (login ?? email ?? '').trim()
        const response = await api.post('/auth/signin', {
          login: identifier,
          password
        })

        const { user, access, refresh } = response.data

        if (!access || !refresh) {
          throw new Error('Tokens inválidos')
        }

        commit('SET_AUTH', {
          user: user || { username: identifier },
          access,
          refresh
        })

        return true
      } catch (error) {
        console.error('Erro no login:', error)
        return false
      } finally {
        commit('SET_LOADING', false)
      }
    },

    logout({ commit }) {
      commit('LOGOUT')
      window.location.href = '/'
    },

    /** Carrega perfil admin do utilizador em modo “ver como” (rotas /financas). */
    async fetchSubjectMonitoredProfile ({ commit, state }) {
      const m = state.subjectViewMode
      if (!m || m.kind !== SUBJECT_VIEW_KIND.ADMIN || !m.userId) {
        commit('SET_SUBJECT_MONITORED_USER', null)
        return
      }
      try {
        const { adminService } = await import('@/services/adminService')
        const data = await adminService.getUser(m.userId)
        commit('SET_SUBJECT_MONITORED_USER', data)
      } catch (_) {
        commit('SET_SUBJECT_MONITORED_USER', null)
      }
    }
  }
})