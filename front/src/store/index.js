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
    }
  },

  actions: {
    async login({ commit }, { email, password }) {
      try {
        commit('SET_LOADING', true)

        const response = await api.post('/auth/signin', {
          email,
          password
        })

        const { access, refresh, username } = response.data

        if (!access || !refresh) {
          throw new Error('Tokens inválidos')
        }

        const userData = { username: username || email }

        commit('SET_AUTH', {
          user: userData,
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