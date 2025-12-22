// src/utils/request.js
import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 60000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const loginUserStr = localStorage.getItem('loginUser')
    let loginUser = null
    try {
      loginUser = loginUserStr ? JSON.parse(loginUserStr) : null
    } catch (e) {
      loginUser = null
    }

    // ✅ 所有请求都带上 token，如果没有则传 null
    config.headers.token = loginUser?.token ?? null

    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response && error.response.status === 401) {
      // 只提示，不动 token
      ElMessage.error(error.response.data?.message || '未授权或登录状态失效')
      // 如果你希望401时跳转登录页，可以在这里打开 router.push
    }
    return Promise.reject(error)
  }
)

export default request
