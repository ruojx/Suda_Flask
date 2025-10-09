<!-- /src/Settings.vue -->
<template>
  <div class="container settings">
    <div class="head">
      <h1 class="title">设置</h1>
      <div class="actions">
        <button class="btn" @click="goBack">← 返回</button>
        <button class="btn" @click="resetToDefaults">重置</button>
        <button class="btn primary" @click="saveAll">💾 保存</button>
      </div>
    </div>

    <!-- 外观与偏好 -->
    <section class="card">
      <h2 class="section-title">外观与偏好</h2>
      <div class="grid-2">
        <div class="field">
          <label>主题</label>
          <select v-model="state.appearance.theme" class="input">
            <option value="system">跟随系统</option>
            <option value="light">亮色</option>
            <option value="dark">暗色</option>
          </select>
          <small class="muted">保存后会立即应用到站点。</small>
        </div>
        <div class="field">
          <label>语言</label>
          <select v-model="state.appearance.locale" class="input">
            <option value="zh-CN">简体中文</option>
            <option value="en-US">English</option>
          </select>
        </div>
      </div>
    </section>

    <!-- 个人资料 -->
    <section class="card">
      <h2 class="section-title">个人资料</h2>
      <div class="grid-2">
        <div class="field">
          <label>昵称</label>
          <input v-model="state.profile.name" class="input" placeholder="Your Name" />
        </div>
        <div class="field">
          <label>邮箱</label>
          <input v-model="state.profile.email" class="input" type="email" placeholder="you@example.com" />
        </div>
      </div>
      <div class="grid-2">
        <div class="field">
          <label>所在城市</label>
          <input v-model="state.profile.location" class="input" placeholder="Tokyo / Shanghai" />
        </div>
        <div class="field">
          <label>职位/角色</label>
          <input v-model="state.profile.role" class="input" placeholder="Software Engineer" />
        </div>
      </div>
      <div class="grid-2">
        <div class="field">
          <label>GitHub</label>
          <input v-model="state.profile.links.github" class="input" placeholder="https://github.com/yourname" />
        </div>
        <div class="field">
          <label>博客</label>
          <input v-model="state.profile.links.blog" class="input" placeholder="https://blog.example.com" />
        </div>
      </div>
      <div class="grid-2">
        <div class="field">
          <label>LinkedIn</label>
          <input v-model="state.profile.links.linkedin" class="input" placeholder="https://linkedin.com/in/you" />
        </div>
        <div class="field">
          <label>头像 URL</label>
          <input v-model="state.profile.avatar" class="input" placeholder="/src/assets/avatar.jpg 或在线链接" />
        </div>
      </div>
      <div class="field">
        <label>一句话签名</label>
        <input v-model="state.profile.subtitle" class="input" placeholder="全栈开发 · Vue 3 & Spring Boot" />
      </div>
      <div class="field">
        <label>对外可见</label>
        <label class="switch">
          <input type="checkbox" v-model="state.profile.publicVisible">
          <span>公开展示我的基础资料</span>
        </label>
      </div>
    </section>

    <!-- 通知 -->
    <section class="card">
      <h2 class="section-title">通知</h2>
      <div class="grid-3">
        <div class="field">
          <label class="switch">
            <input type="checkbox" v-model="state.notify.email">
            <span>邮件通知</span>
          </label>
          <small class="muted">新消息、评论、系统公告。</small>
        </div>
        <div class="field">
          <label class="switch">
            <input type="checkbox" v-model="state.notify.inApp">
            <span>站内通知</span>
          </label>
          <small class="muted">右上角铃铛推送。</small>
        </div>
        <div class="field">
          <label>周报时间</label>
          <input class="input" type="time" v-model="state.notify.digestAt" />
          <small class="muted">每周一在此时间发送总结。</small>
        </div>
      </div>
    </section>

    <!-- AI 功能 -->
    <section class="card">
      <h2 class="section-title">AI 功能</h2>
      <div class="grid-3">
        <div class="field">
          <label class="switch">
            <input type="checkbox" v-model="state.ai.autoAnswer">
            <span>启用 AI 回答</span>
          </label>
          <small class="muted">在观点下自动生成参考回答。</small>
        </div>
        <div class="field">
          <label class="switch">
            <input type="checkbox" v-model="state.ai.compareOpinions">
            <span>AI 观点对比</span>
          </label>
          <small class="muted">聚合优缺点，生成对照表。</small>
        </div>
        <div class="field">
          <label class="switch">
            <input type="checkbox" v-model="state.ai.planGen">
            <span>AI 计划生成</span>
          </label>
          <small class="muted">基于主题产出行动清单。</small>
        </div>
      </div>
      <div class="grid-2">
        <div class="field">
          <label>模型温度 (0–1)</label>
          <input class="input" type="number" step="0.05" min="0" max="1" v-model.number="state.ai.temperature" />
        </div>
        <div class="field">
          <label>最大输出 Token</label>
          <input class="input" type="number" min="64" max="4096" v-model.number="state.ai.maxTokens" />
        </div>
      </div>
    </section>

    <!-- 账户与安全 -->
    <section class="card">
      <h2 class="section-title">账户与安全</h2>
      <div class="grid-2">
        <div class="field">
          <label>双重验证 (2FA)</label>
          <label class="switch">
            <input type="checkbox" v-model="state.security.enable2FA">
            <span>启用</span>
          </label>
        </div>
        <div class="field">
          <label>会话有效期（天）</label>
          <input class="input" type="number" min="1" max="30" v-model.number="state.security.sessionTTL" />
        </div>
      </div>
      <div class="danger">
        <button class="btn danger-btn" @click="logoutAll">退出所有设备</button>
        <small class="muted">将使所有已登录会话失效。</small>
      </div>
    </section>

    <footer class="footer">
      <button class="btn" @click="resetToDefaults">重置</button>
      <button class="btn primary" @click="saveAll">保存</button>
    </footer>
  </div>
</template>

<script setup>
import { reactive, onMounted, watch, computed } from 'vue'

/** 本地持久化键 */
const LS_KEY = 'app.settings.v1'

/** 默认设置 */
const defaults = {
  appearance: {
    theme: 'system', // 'light' | 'dark' | 'system'
    locale: 'zh-CN'
  },
  profile: {
    name: 'Your Name',
    email: 'you@example.com',
    location: 'Tokyo / Shanghai',
    role: 'Software Engineer',
    subtitle: '全栈开发 · Vue 3 & Spring Boot',
    avatar: '/src/assets/avatar.jpg',
    publicVisible: true,
    links: {
      github: 'https://github.com/yourname',
      blog: '#',
      linkedin: '#'
    }
  },
  notify: {
    email: true,
    inApp: true,
    digestAt: '09:00'
  },
  ai: {
    autoAnswer: true,
    compareOpinions: true,
    planGen: true,
    temperature: 0.4,
    maxTokens: 1024
  },
  security: {
    enable2FA: false,
    sessionTTL: 7
  }
}

const state = reactive(structuredClone(defaults))

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(LS_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      deepMerge(state, parsed)
    }
  } catch (e) {
    console.warn('[settings] load failed:', e)
  }
}

function saveAll() {
  localStorage.setItem(LS_KEY, JSON.stringify(state))
  applyTheme(state.appearance.theme)
  alert('已保存设置')
}

/** 主题应用到 <html> */
function applyTheme(theme) {
  let t = theme
  if (t === 'system') {
    t = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  document.documentElement.style.colorScheme = t
}

/** 重置为默认 */
function resetToDefaults() {
  deepMerge(state, structuredClone(defaults), true)
  saveAll()
}

/** 返回上一页（若父级使用 <Settings @back="..."> 可改造 emit） */
function goBack() {
  history.length > 1 ? history.back() : null
}

/** 退出所有设备（演示） */
function logoutAll() {
  if (confirm('确定要退出所有设备吗？')) {
    // 这里可调用后端 API：/api/account/logout-all
    alert('已请求退出所有设备（演示）')
  }
}

/** 深合并工具 */
function deepMerge(target, src, replace = false) {
  for (const k of Object.keys(src)) {
    const v = src[k]
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      if (!target[k] || replace) target[k] = {}
      deepMerge(target[k], v, replace)
    } else {
      target[k] = v
    }
  }
}

onMounted(() => {
  loadFromStorage()
  applyTheme(state.appearance.theme)
})

/** 跟随系统主题变化（当选择“跟随系统”时） */
const media = window.matchMedia('(prefers-color-scheme: dark)')
media.addEventListener?.('change', () => {
  if (state.appearance.theme === 'system') applyTheme('system')
})
</script>

<style scoped>
.settings { padding-top: 24px; padding-bottom: 40px; }
.head { display:flex; align-items:center; gap:14px; margin-bottom:14px; }
.head .actions { margin-left:auto; display:flex; gap:10px; flex-wrap: wrap; }
.title { font-size:24px; margin:0; }
.card {
  margin: 16px 0;
  background: linear-gradient(180deg, color-mix(in oklab, var(--card) 92%, transparent), var(--card));
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 18px;
}
.section-title { margin:0 0 12px; font-size:18px; }
.grid-2 { display:grid; grid-template-columns: 1fr 1fr; gap:14px; }
.grid-3 { display:grid; grid-template-columns: 1fr 1fr 1fr; gap:14px; }
.field { display:flex; flex-direction:column; gap:8px; }
label { font-weight:600; }
.input {
  border:1px solid var(--border);
  background:linear-gradient(180deg, color-mix(in oklab, var(--card) 90%, transparent), var(--card));
  color:var(--text); padding:10px 12px; border-radius:12px; outline:none;
}
.input:focus { box-shadow: 0 0 0 3px color-mix(in oklab, var(--brand) 25%, transparent); }
.switch { display:flex; align-items:center; gap:10px; }
.btn{
  border:1px solid var(--border); background:linear-gradient(180deg, color-mix(in oklab, var(--card) 90%, transparent), var(--card)); color:var(--text);
  padding:8px 14px; border-radius:12px; display:inline-flex; align-items:center; gap:8px; cursor:pointer; transition:.2s;
}
.btn:hover{ transform: translateY(-1px); }
.btn.primary{ background: linear-gradient(180deg, color-mix(in oklab, var(--brand) 25%, var(--card)), var(--card)); }
.danger{ margin-top:12px; display:flex; align-items:center; gap:10px; }
.danger-btn{ border-color:#ff5959; }
.footer{ display:flex; justify-content:flex-end; gap:10px; padding-top:10px; }

@media (max-width: 860px){
  .grid-2, .grid-3 { grid-template-columns: 1fr; }
  .head { flex-direction: column; align-items: flex-start; gap:8px; }
  .head .actions { margin-left:0; }
}
</style>
