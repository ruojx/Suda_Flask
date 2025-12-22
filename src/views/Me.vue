<template>
  <div class="page">
    <!-- 顶部导航 -->
    <header class="nav">
      <div class="container nav-inner">
        <strong class="logo">👨🏻‍💻 {{ profile.name }}</strong>
        <nav class="nav-links">
          <a href="#about">关于我</a>
          <a href="#skills">技能</a>
          <a href="#projects">项目</a>
          <a href="#timeline">时间线</a>
          <a href="#contact">联系我</a>
        </nav>
        <div class="spacer"></div>
        <a class="btn primary" :href="profile.resumeUrl" download>📄 下载简历</a>
      </div>
    </header>

    <!-- Hero -->
    <section class="hero container">
      <div class="hero-card">
        <img class="avatar" :src="profile.avatar" alt="avatar" />
        <div class="hero-info">
          <h1>{{ profile.title }}</h1>
          <p class="subtitle">{{ profile.subtitle }}</p>
          <div class="chips">
            <span class="chip">📍 {{ profile.location }}</span>
            <span class="chip">💼 {{ profile.role }}</span>
            <span class="chip">🔭 {{ profile.focus }}</span>
          </div>
          <div class="links">
            <a class="btn outline" :href="profile.links.github" target="_blank">GitHub</a>
            <a class="btn outline" :href="profile.links.blog" target="_blank">博客</a>
            <a class="btn outline" :href="profile.links.linkedin" target="_blank">LinkedIn</a>
          </div>
        </div>
      </div>
    </section>

    <!-- 关于我 -->
    <section id="about" class="container">
      <div class="card">
        <h2>关于我</h2>
        <p>
          我是 {{ profile.name }}，一名热爱创造的全栈开发者，专注于
          <b>Vue3</b> 前端与 <b>Spring Boot</b> 后端。  
          我喜欢把复杂系统拆解成优雅的组件，追求性能与美感并存的产品体验。
        </p>
      </div>
    </section>

    <!-- 技能 -->
    <section id="skills" class="container">
      <div class="grid">
        <div class="card" v-for="s in skills" :key="s.title">
          <h3>{{ s.title }}</h3>
          <div class="tags">
            <span v-for="t in s.tags" :key="t" class="tag">{{ t }}</span>
          </div>
          <div class="bar">
            <div class="fill" :style="{width: s.level + '%'}"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 项目 -->
    <section id="projects" class="container">
      <h2>项目展示</h2>
      <div class="project-grid">
        <div class="card project" v-for="p in projects" :key="p.title">
          <img :src="p.cover" class="project-img" alt="封面" />
          <div class="project-info">
            <h3>{{ p.title }}</h3>
            <p>{{ p.desc }}</p>
            <div class="stack">{{ p.stack.join(' · ') }}</div>
            <div class="project-links">
              <a class="btn small" :href="p.demo" target="_blank">🔗 预览</a>
              <a class="btn small" :href="p.repo" target="_blank">🧩 源码</a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 时间线 -->
    <section id="timeline" class="container">
      <h2>时间线</h2>
      <ul class="timeline">
        <li v-for="t in timeline" :key="t.time">
          <span class="dot"></span>
          <div>
            <strong>{{ t.time }}</strong> - {{ t.title }}
            <p class="muted">{{ t.desc }}</p>
          </div>
        </li>
      </ul>
    </section>

    <!-- 联系 -->
    <section id="contact" class="container">
      <h2>联系我</h2>
      <div class="contact">
        <div class="card">
          <p class="muted">合作、内推或项目咨询欢迎联系：</p>
          <div class="links">
            <a class="btn outline" :href="`mailto:${profile.email}`">📨 邮件</a>
            <a class="btn outline" :href="profile.wechat">💬 微信</a>
            <a class="btn outline" :href="profile.telegram">✈️ Telegram</a>
          </div>
        </div>
      </div>
    </section>

    <footer class="footer">
      © {{ new Date().getFullYear() }} {{ profile.name }} · Designed with ❤️
    </footer>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const profile = reactive({
  name: 'Your Name',
  title: 'Hi，我是 Your Name 👋',
  subtitle: '全栈开发 · Vue 3 & Spring Boot',
  role: 'Software Engineer',
  location: 'Shanghai',
  focus: '知乎风格观点社区 + AI 对话系统',
  avatar: '/src/assets/avatar.jpg',
  resumeUrl: '/src/assets/resume.pdf',
  email: 'you@example.com',
  wechat: '#',
  telegram: '#',
  links: {
    github: 'https://github.com/yourname',
    blog: '#',
    linkedin: '#'
  }
})

const skills = reactive([
  { title: '前端', tags: ['Vue3', 'TypeScript', 'Vite', 'Pinia', 'ECharts'], level: 90 },
  { title: '后端', tags: ['Spring Boot', 'MySQL', 'Redis', 'MyBatis'], level: 85 },
  { title: '工程化', tags: ['Docker', 'Nginx', 'CI/CD', 'Linux'], level: 80 }
])

const projects = reactive([
  { title: '观点社区', stack: ['Vue3', 'Pinia', 'Axios'], desc: '知乎式观点平台，支持AI回答与观点对比。', cover: '/src/assets/p1.jpg', demo: '#', repo: '#' },
  { title: 'AI 智能问答', stack: ['Spring Boot', 'LLM API'], desc: '集成大模型进行多话题智能问答和观点聚合。', cover: '/src/assets/p2.jpg', demo: '#', repo: '#' }
])

const timeline = reactive([
  { time: '2025-09', title: '上线协作编辑', desc: '多人实时协作草稿与讨论。' },
  { time: '2025-06', title: '发布群体讨论会', desc: 'AI 自动生成会议要点与纪要。' }
])
</script>

<style>

/* 导航栏 */
.nav {
  position: sticky;
  top: 0;
  backdrop-filter: blur(12px);
  background: rgba(255, 255, 255, 0.7);
  border-bottom: 1px solid #e0e3eb;
  z-index: 10;
}
.nav-inner {
  display: flex;
  align-items: center;
  padding: 14px 0;
}
.nav-links a {
  margin: 0 10px;
  color: #444;
  text-decoration: none;
  font-weight: 500;
}
.nav-links a:hover {
  color: #0078ff;
}

/* Hero */
.hero-card {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 40px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.7);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  backdrop-filter: blur(10px);
  margin-top: 40px;
}
.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
}
.subtitle {
  color: #666;
  margin: 8px 0 16px;
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.chip {
  padding: 6px 10px;
  background: #eef2f9;
  border-radius: 999px;
  font-size: 14px;
  color: #555;
}
.links {
  margin-top: 16px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* 按钮 */
.btn {
  border: none;
  border-radius: 10px;
  padding: 8px 16px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: 0.2s;
}
.btn.primary {
  background: #0078ff;
  color: #fff;
}
.btn.outline {
  border: 1px solid #0078ff;
  color: #0078ff;
  background: transparent;
}
.btn.small {
  padding: 6px 12px;
  font-size: 13px;
}
.btn:hover {
  opacity: 0.9;
}

/* 卡片布局 */
.container {
  max-width: 1080px;
  margin: 0 auto;
  padding: 40px 20px;
}
.card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  padding: 24px;
  margin-bottom: 30px;
}

/* 技能 */
.grid {
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.tag {
  background: #eef3ff;
  color: #3366ff;
  border-radius: 8px;
  padding: 4px 10px;
  font-size: 13px;
}
.bar {
  margin-top: 10px;
  height: 8px;
  background: #f1f3f9;
  border-radius: 8px;
  overflow: hidden;
}
.fill {
  height: 100%;
  background: linear-gradient(90deg, #3366ff, #7ad3ff);
}

/* 项目 */
.project-grid {
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
}
.project-img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 12px;
}
.project-info {
  padding: 16px 0;
}
.stack {
  color: #666;
  font-size: 13px;
  margin-bottom: 10px;
}

/* 时间线 */
.timeline {
  list-style: none;
  padding: 0;
  border-left: 2px solid #e0e3eb;
  margin-left: 12px;
}
.timeline li {
  position: relative;
  margin: 20px 0;
  padding-left: 20px;
}
.timeline .dot {
  position: absolute;
  width: 10px;
  height: 10px;
  background: #0078ff;
  border-radius: 50%;
  left: -6px;
  top: 5px;
}
.muted {
  color: #777;
  font-size: 14px;
}

/* 底部 */
.footer {
  text-align: center;
  padding: 40px 0;
  font-size: 14px;
  color: #777;
}

/* 响应式 */
@media (max-width: 768px) {
  .hero-card {
    flex-direction: column;
    text-align: center;
  }
  .avatar {
    width: 100px;
    height: 100px;
  }
}
</style>
