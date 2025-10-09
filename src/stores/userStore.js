// src/stores/userStore.js
import { defineStore } from 'pinia'

const LS_KEY = 'loginUser'

// 安全解析，避免 JSON.parse(null) 或损坏数据抛错
function safeParseLoginUser() {
  try {
    const raw = localStorage.getItem(LS_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    localStorage.removeItem(LS_KEY)
    return null
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    // 只在启动时尝试读取一次，剩下都走 setUser/clearUser 维护
    user: safeParseLoginUser(), // 结构形如：{ id, name, username, token, refreshToken? }
  }),

  getters: {
    isLoggedIn: (s) => !!s.user && !!s.user.token,     // 既有用户又有 token 才算登录
    userId:     (s) => s.user?.id ?? null,
    userName:   (s) => s.user?.name || '匿名用户',
    token:      (s) => s.user?.token || null,
  },

  actions: {
    // 登录成功后调用，user 要包含 token
    setUser(userObj) {
      this.user = userObj || null
      if (this.user) localStorage.setItem(LS_KEY, JSON.stringify(this.user))
      else localStorage.removeItem(LS_KEY)
    },

    // 退出登录/401/刷新失败时调用
    clearUser() {
      this.user = null
      localStorage.removeItem(LS_KEY)
    },

    // 应用启动或页面刷新后调用：用后端 /auth/me 校验本地 token 是否有效
    async initAuth(validateFn) {
      // validateFn 是一个返回用户信息的异步函数，如：() => api.get('/auth/me')
      if (!this.user?.token) { this.clearUser(); return false }
      try {
        const freshUser = await validateFn() // 由调用方决定如何请求
        // 可选择把后端返回的最新资料合并回本地
        this.user = { ...this.user, ...freshUser }
        localStorage.setItem(LS_KEY, JSON.stringify(this.user))
        return true
      } catch (e) {
        this.clearUser()
        return false
      }
    }
  }
})
