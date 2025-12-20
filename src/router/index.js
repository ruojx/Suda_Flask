import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/home',
    children: [
      { path: 'login', name: 'Login', component: () => import('@/views/Login.vue') },
      { path: 'register', name: 'Register', component: () => import('@/views/Register.vue') },
      { path: 'home', name: 'Home', component: () => import('@/views/Home.vue') },
      { path: 'reset', name: 'Reset', component: () => import('@/views/Reset.vue')},
      { path: 'resource', name: 'Resource', component: () => import('@/views/Resource.vue') },
      // { path: 'chat', name: 'Chat', component: () => import('@/views/Chat.vue') },
      { path: 'me', name: 'Me', component: () => import('@/views/Me.vue') },
      { path: 'consultation', name: 'Consultation', component: () => import('@/views/Consultation.vue') },
      { path: 'settings', name: 'Settings', component: () => import('@/views/Settings.vue') },
    ]
  },

  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/NotFound.vue') }
]

const router = createRouter({
  history: createWebHistory(), // 若后端未配置SPA回退，先用 createWebHashHistory()
  routes
})

// 路由拦截
router.beforeEach((to, from, next) => {
  const token = JSON.parse(localStorage.getItem('loginUser') || '{}')?.token

  if (to.meta.requiresAuth && !token) {
    ElMessage.warning('请先登录后再访问该功能')
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  if (token && (to.path === '/login')) {
    return next('/home')
  }

  next()
})

export default router
