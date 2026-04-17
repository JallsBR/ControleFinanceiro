import { createStore } from 'vuex'
import api from '../services/APIService'

export default createStore({
  state: {
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('access') || null,
    loading: false
  },

  getters: {
    isAuthenticated: state => !!state.token,
    getUser: state => state.user,
    isLoading: state => state.loading
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

      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      localStorage.removeItem('user')
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
    }
  }
})