<!-- src/views/public/Home.vue -->
<template>
  <div class="home">
    <!-- <section class="banner">
      <img
        src="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=1600&q=80&auto=format&fit=crop"
        alt="banner"
      />
    </section> -->

    <!-- 发布入口 -->
    <section class="composer card">
      <input
        class="composer-input"
        placeholder="分享此刻的想法..."
        @focus="goAsk"
        readonly
      />
      <div class="composer-actions">
        <button @click="goAsk">提问题</button>
        <button @click="writeAnswer">写回答</button>
        <button @click="writeArticle">写文章</button>
        <button @click="postVideo">发视频</button>
      </div>
    </section>

    <!-- 顶部标签 -->
    <section class="tabs">
      <button
        v-for="t in tabs"
        :key="t.key"
        :class="['tab', currentTab === t.key && 'active']"
        @click="switchTab(t.key)"
      >
        {{ t.label }}
      </button>
    </section>

    <!-- 信息流 -->
    <section class="feed">
      <article v-for="item in feed" :key="item.id" class="feed-item card">
        <h3 class="title">{{ item.title }}</h3>
        <p class="summary">{{ item.summary }}</p>
        <div class="actions">
          <span>👍 {{ item.like }}</span>
          <span>💬 {{ item.comment }}</span>
          <span>⭐ {{ item.collect }}</span>
        </div>
      </article>

      <div class="load-more">
        <button v-if="!noMore" @click="fetchMore">加载更多</button>
        <div v-else class="muted">没有更多了</div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 顶部标签
const tabs = [
  { key: 'follow', label: '关注' },
  { key: 'recommend', label: '推荐' },
  { key: 'hot', label: '热榜' },
  { key: 'column', label: '专栏' }
]
const currentTab = ref('recommend')

// 信息流
const feed = ref([])
const page = ref(1)
const noMore = ref(false)

onMounted(() => {
  fetchFeed()
})

function switchTab(key) {
  currentTab.value = key
  page.value = 1
  noMore.value = false
  feed.value = []
  fetchFeed()
}

function fetchFeed() {
  // TODO: 接后端 API
  const mock = Array.from({ length: 5 }).map((_, i) => ({
    id: (page.value - 1) * 5 + i + 1,
    title: `示例标题 ${i + 1} (${currentTab.value})`,
    summary: '这里是内容摘要，后续可从后端接口获取实际内容。',
    like: Math.floor(Math.random() * 1000),
    comment: Math.floor(Math.random() * 200),
    collect: Math.floor(Math.random() * 50)
  }))
  feed.value.push(...mock)
  if (page.value >= 3) noMore.value = true
}

function fetchMore() {
  if (noMore.value) return
  page.value++
  fetchFeed()
}

// 发布入口
const goAsk = () => router.push('/question/ask')
const writeAnswer = () => router.push('/answer/write')
const writeArticle = () => router.push('/article/edit')
const postVideo = () => router.push('/video/post')
</script>

<style scoped>
.home {
  padding: 16px 0 40px;
}
.banner img {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 16px;
}
.card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
}
.composer-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: text;
}
.composer-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.composer-actions button {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  background: #fafafa;
}
.tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.tab {
  padding: 6px 12px;
  border: none;
  background: none;
  cursor: pointer;
  color: #666;
}
.tab.active {
  color: #1e80ff;
  font-weight: bold;
  border-bottom: 2px solid #1e80ff;
}
.feed-item .title {
  margin-bottom: 8px;
}
.actions {
  display: flex;
  gap: 12px;
  font-size: 14px;
  color: #666;
}
.load-more {
  text-align: center;
  margin-top: 16px;
}
.muted {
  color: #999;
}
</style>
