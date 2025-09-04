<!-- src/views/layout/Layout.vue -->
<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 顶部导航（保持你的配置不变）
const navs = [
  { label: '首页', path: '/home' },
  { label: '资源', path: '/resource' },
  { label: '讨论', path: '/chat' },
  { label: '咨询', path: '/Consultation' }
]

const keyword = ref('')
const menuOpen = ref(false)

// 认证态
const loginUser = ref(readLoginUser())
const isAuthed = computed(() => !!loginUser.value?.token)
const avatarUrl = computed(
  () => loginUser.value?.avatar || 'https://api.dicebear.com/7.x/initials/svg?seed=U'
)
const unreadCount = ref(0) // 可在 mounted 时请求后端未读数

function readLoginUser () {
  try { return JSON.parse(localStorage.getItem('loginUser') || '{}') } catch { return {} }
}

// 保持与其它标签页状态同步
const onStorage = (e) => {
  if (e.key === 'loginUser') {
    loginUser.value = readLoginUser()
  }
}

onMounted(() => {
  window.addEventListener('storage', onStorage)
  window.addEventListener('click', onWindowClick)
})
onBeforeUnmount(() => {
  window.removeEventListener('storage', onStorage)
  window.removeEventListener('click', onWindowClick)
})
const onWindowClick = () => (menuOpen.value = false)

// 搜索 / 跳转
const onSearch = () => {
  if (!keyword.value) return
  router.push({ path: '/search', query: { q: keyword.value } })
}
const goAsk = () => router.push('/question/ask')
const goNotice = () => router.push('/notifications')

// 头像菜单
const toggleMenu = (e) => {
  e.stopPropagation()
  menuOpen.value = !menuOpen.value
}

const logout = () => {
  localStorage.removeItem('loginUser')
  loginUser.value = {}
  router.replace('/login')
}

// 生成登录后的回跳参数
const loginLink = computed(() => ({
  path: '/login',
  query: { redirect: route.fullPath }
}))
</script>

<template>
  <div class="zh-layout">
    <!-- 顶部导航 -->
    <header class="zh-header">
      <div class="zh-container header-inner">
        <!-- 左区：Logo + 导航 -->
        <div class="left">
          <router-link to="/home" class="logo" aria-label="首页">
            <span class="logo-dot" />
            <span class="logo-text">SUDADA</span>
          </router-link>

          <nav class="top-nav" role="navigation" aria-label="主导航">
            <router-link
              v-for="item in navs"
              :key="item.path"
              :to="item.path"
              class="nav-link"
              active-class="nav-active"
            >
              {{ item.label }}
            </router-link>
          </nav>
        </div>

        <!-- 中区：搜索 -->
        <div class="middle">
          <form class="search" @submit.prevent="onSearch">
            <input
              v-model.trim="keyword"
              type="search"
              placeholder="搜索内容、话题或用户"
              aria-label="搜索"
            />
            <button type="submit" class="search-btn" aria-label="搜索">搜</button>
          </form>
        </div>

        <div class="right">
          <template v-if="!isAuthed">
            <router-link class="text-link" :to="loginLink">登录</router-link>
            <span class="divider-vert" aria-hidden="true">|</span>
            <router-link class="text-link" to="/register">注册</router-link>
          </template>

          <template v-else>
            <button class="ask-btn" @click="goAsk">提问</button>

            <button class="icon-btn" title="通知" aria-label="通知" @click="goNotice">
              🔔
              <span v-if="unreadCount > 0" class="badge">
                {{ unreadCount > 99 ? '99+' : unreadCount }}
              </span>
            </button>

            <div
              class="avatar"
              role="button"
              aria-label="用户菜单"
              :aria-expanded="menuOpen"
              @click.stop="toggleMenu"
            >
              <img :src="avatarUrl" alt="avatar" />
              <ul v-show="menuOpen" class="dropdown" @click.stop>
                <li><router-link to="/user/me">我的主页</router-link></li>
                <li><router-link to="/settings/profile">设置</router-link></li>
                <li class="divider"></li>
                <li><a href="javascript:void(0)" @click="logout">退出登录</a></li>
              </ul>
            </div>
          </template>
        </div>
      </div>
    </header>

    <main class="zh-main">
      <div class="zh-container">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<style scoped>
:root {
  --bg: #ffffff;
  --text: #111;
  --muted: #666;
  --line: #e5e7eb;
  --primary: #1e80ff;
  --primary-ink: #0b5ed7;
  --header-h: 60px;
}

.zh-layout {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
}

.zh-container {
  width: min(1100px, 92vw);
  margin: 0 auto;
}

/* 顶部栏 */
.zh-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  height: var(--header-h);
  background: rgba(255, 255, 255, .9);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--line);
}

.header-inner {
  height: 100%;
  display: grid;
  grid-template-columns: 1fr 1.2fr auto;
  align-items: center;
  gap: 16px;
}

/* 左侧：Logo + 导航 */
.left {
  display: flex;
  align-items: center;
  gap: 18px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.logo-dot {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  background: var(--primary);
  display: inline-block;
}
.logo-text {
  font-weight: 700;
  color: var(--text);
  letter-spacing: .2px;
}

.top-nav {
  display: flex;
  gap: 12px;
}
.nav-link {
  padding: 6px 10px;
  border-radius: 8px;
  color: var(--muted);
  text-decoration: none;
}
.nav-link:hover {
  background: #f5f7fa;
  color: var(--text);
}
.nav-active {
  background: #eaf2ff;
  color: var(--primary);
}

/* 中间：搜索 */
.middle { display: flex; }
.search {
  width: 100%;
  display: flex;
  border: 1px solid var(--line);
  border-radius: 10px;
  overflow: hidden;
  background: #fafafa;
}
.search input {
  flex: 1;
  height: 36px;
  padding: 0 12px;
  border: none;
  outline: none;
  background: transparent;
  color: var(--text);
}
.search-btn {
  padding: 0 12px;
  border: none;
  border-left: 1px solid var(--line);
  background: var(--primary);
  color: #fff;
  cursor: pointer;
}
.search-btn:hover { background: var(--primary-ink); }

/* 右侧：动作区 */
.right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.text-link {
  color: var(--primary);
  text-decoration: none;
  line-height: 36px;
  padding: 0 2px;
}
.text-link:hover { text-decoration: underline; }
.divider-vert { color: #bbb; padding: 0 4px; }

.ask-btn {
  height: 36px;
  padding: 0 14px;
  border-radius: 10px;
  border: none;
  background: var(--primary);
  color: #fff;
  cursor: pointer;
}
.ask-btn:hover { background: var(--primary-ink); }

.icon-btn {
  position: relative;
  height: 36px;
  padding: 0 10px;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: #fff;
  cursor: pointer;
}
.icon-btn:hover { background: #f5f7fa; }

.badge{
  position: absolute;
  top: -6px; right: -6px;
  min-width: 18px; height: 18px;
  padding: 0 4px;
  border-radius: 9px;
  background: #ff4d4f; color: #fff;
  font-size: 12px; line-height: 18px; text-align: center;
}

/* 头像 + 下拉 */
.avatar {
  position: relative;
  width: 36px; height: 36px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--line);
  cursor: pointer;
  background: #fff;
}
.avatar img {
  width: 100%; height: 100%; object-fit: cover;
}
.dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  width: 160px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 10px;
  box-shadow: 0 12px 30px rgba(0,0,0,.08);
  list-style: none;
  padding: 6px 0;
}
.dropdown li { line-height: 36px; }
.dropdown a, .dropdown :deep(a) {
  display: block;
  padding: 0 12px;
  color: var(--text);
  text-decoration: none;
}
.dropdown a:hover { background: #f5f7fa; }
.dropdown .divider {
  height: 1px; background: var(--line); margin: 6px 0;
}

/* 主体区 */
.zh-main { padding: 18px 0 42px; }
.page-enter-active, .page-leave-active { transition: opacity .2s ease }
.page-enter-from, .page-leave-to { opacity: 0 }

/* 响应式 */
@media (max-width: 960px) {
  .header-inner {
    grid-template-columns: 1fr auto auto;
    gap: 10px;
  }
  .top-nav { display: none; }  /* 小屏隐藏顶栏导航，可改抽屉 */
  .middle { display: none; }   /* 小屏隐藏搜索，可改弹窗 */
}
</style>
