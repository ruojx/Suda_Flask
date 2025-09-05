import { createRouter, createWebHistory /* 或 createWebHashHistory */ } from 'vue-router'
import { ElMessage } from 'element-plus'

const routes = [
  // 公共页（任何人可见）
  
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/home',
    children: [
      { path: '/login', name: 'Login', component: () => import('@/views/Login.vue') },
      { path: '/reset', name: 'Reset', component: () => import('@/views/Reset.vue') },
      // 首页：不需要登录
      { path: 'home', name: 'Home', component: () => import('@/views/Home.vue') },
      { path: 'resource', name: 'Resource', component: () => import('@/views/Resource.vue') },
      { path: 'chat', name: 'Chat', component: () => import('@/views/Chat.vue') },
      { path: 'consultation', name: 'Consultation', component: () => import('@/views/Consultation.vue') },

      // { path: 'user/:id', name: 'UserProfile', component: () => import('@/views/user/Profile.vue'), meta: { requiresAuth: true } },
      // { path: 'editor', name: 'Editor', component: () => import('@/views/editor/Editor.vue'), meta: { requiresAuth: true } },
      // { path: 'notifications', name: 'Notifications', component: () => import('@/views/notify/Notifications.vue'), meta: { requiresAuth: true } },
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

  if (token && (to.path === '/login' || to.path === '/reset')) {
    return next('/home')
  }

  next()
})

export default router
