<!-- /src/NotFound.vue -->
<template>
  <main class="nf">
    <div class="bg-grad"></div>

    <section class="card">
      <div class="code">404</div>
      <h1 class="title">页面不存在</h1>
      <p class="desc">
        抱歉，您访问的地址已失效或被移动。<br />
        也许试试回到首页，或检查一下链接是否正确。
      </p>

      <div class="actions">
        <button class="btn outline" @click="goBack">← 返回上一页</button>
        <button class="btn primary" @click="goHome">🏠 回到首页</button>
      </div>

   
    </section>

    <footer class="footer">
      © {{ year }} · 自学 · Vue3
    </footer>
  </main>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const year = new Date().getFullYear()
const q = ref('')

function goHome() {
  // 若使用 vue-router，可改为：router.push({ path: '/' })
  location.href = '/'
}
function goBack() {
  // 没有历史时也回首页
  if (history.length > 1) history.back()
  else goHome()
}
function onSearch() {
  if (!q.value) return
  // 这里替换为你的站内搜索路由或第三方搜索
  // 例如：/search?q=xxx
  const target = `/search?q=${encodeURIComponent(q.value)}`
  location.href = target
}

// 自动跳转倒计时
const countdown = ref(8)
let timer = null

onMounted(() => {
  timer = setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0) {
      clearInterval(timer)
      goHome()
    }
  }, 1000)
})

function cancelAuto() {
  if (timer) clearInterval(timer)
  timer = null
}

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
/* 页面基底 */
.nf {
  min-height: 100vh;
  display: grid;
  grid-template-rows: 1fr auto;
  background: #f6f7fb;
  color: #2c2f36;
  place-items: center;
  padding: 40px 16px;
  position: relative;
  overflow: hidden;
}

/* 柔和渐变背景 */
.bg-grad {
  position: absolute;
  inset: -30% -10% auto -10%;
  height: 65vh;
  background:
    radial-gradient(600px 400px at 10% 20%, rgba(123, 201, 255, 0.25), transparent 60%),
    radial-gradient(500px 380px at 90% 10%, rgba(124, 246, 211, 0.22), transparent 60%),
    radial-gradient(700px 420px at 40% 120%, rgba(179, 157, 255, 0.18), transparent 60%);
  filter: blur(20px);
  z-index: 0;
}

/* 主卡片 */
.card {
  position: relative;
  z-index: 1;
  width: min(780px, 100%);
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(10px);
  border: 1px solid #e6e9f1;
  border-radius: 20px;
  padding: 36px 28px;
  box-shadow: 0 10px 30px rgba(13, 28, 62, 0.08);
  text-align: center;
}

/* 404 大号数字 + 轻微抖动动画 */
.code {
  font-size: clamp(56px, 10vw, 112px);
  line-height: 1;
  font-weight: 800;
  letter-spacing: 2px;
  color: #0f62fe;
  text-shadow: 0 6px 24px rgba(15, 98, 254, 0.25);
  animation: float 3.2s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0) }
  50%      { transform: translateY(-6px) }
}

.title {
  margin: 10px 0 6px;
  font-size: clamp(20px, 4vw, 28px);
}
.desc {
  margin: 0 auto 18px;
  color: #636b7a;
  max-width: 46ch;
}

/* 操作按钮 */
.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.btn {
  border: none;
  cursor: pointer;
  border-radius: 12px;
  padding: 10px 16px;
  font-weight: 600;
  font-size: 14px;
  transition: transform .15s ease, box-shadow .15s ease, opacity .2s;
}
.btn:hover { transform: translateY(-1px) }
.btn:active { transform: translateY(0) scale(.99) }
.btn.primary {
  background: #0f62fe;
  color: #fff;
  box-shadow: 0 6px 18px rgba(15, 98, 254, .25);
}
.btn.outline {
  background: transparent;
  color: #0f62fe;
  border: 1px solid #b9cdfd;
}
.btn.small {
  padding: 8px 12px;
  font-size: 13px;
}

/* 额外区：搜索 + 提示 */
.extras {
  margin-top: 6px;
}
.search {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin: 6px 0 8px;
}
.search input {
  width: min(380px, 70vw);
  border: 1px solid #d9deea;
  background: #fff;
  color: #2d3340;
  padding: 10px 12px;
  border-radius: 12px;
  outline: none;
  transition: box-shadow .15s, border-color .15s;
}
.search input:focus {
  border-color: #9bb7ff;
  box-shadow: 0 0 0 3px rgba(15, 98, 254, .12);
}
.hint {
  color: #7a8396;
  font-size: 13px;
  margin: 6px 0 0;
}
.link {
  appearance: none;
  background: none;
  border: none;
  color: #0f62fe;
  cursor: pointer;
  font-weight: 600;
  padding: 0 4px;
}

/* 页脚 */
.footer {
  position: relative;
  z-index: 1;
  text-align: center;
  color: #8a90a0;
  font-size: 13px;
  padding-top: 10px;
}

/* 响应式 */
@media (max-width: 520px) {
  .card { padding: 28px 18px; }
  .search input { width: 100%; }
}
</style>
