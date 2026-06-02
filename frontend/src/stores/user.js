import { defineStore } from 'pinia'
import { login as loginApi } from '../api/auth'
import { getStoredUser, getToken, removeStoredUser, removeToken, setStoredUser, setToken } from '../utils/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    userInfo: null
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token)
  },
  actions: {
    restoreFromStorage() {
      this.token = getToken() || ''
      this.userInfo = getStoredUser()
    },
    async login(credentials) {
      const data = await loginApi(credentials)
      this.token = data.access_token
      this.userInfo = data.user
      setToken(data.access_token)
      setStoredUser(data.user)
      return data
    },
    logout() {
      this.token = ''
      this.userInfo = null
      removeToken()
      removeStoredUser()
    }
  }
})
