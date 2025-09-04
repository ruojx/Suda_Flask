<!-- src/views/resource/Resource.vue -->
<template>
  <div class="res-page">
    <!-- 顶部工具栏：搜索 / 排序 / 上传 -->
    <section class="toolbar card">
      <div class="left">
        <div class="search">
          <input v-model.trim="q" type="search" placeholder="搜索标题、标签、上传者…" @keyup.enter="doSearch" />
          <button class="primary" @click="doSearch">搜索</button>
        </div>
        <div class="filters">
          <span class="muted">类型：</span>
          <button
            v-for="t in TYPES"
            :key="t.value"
            :class="['chip', type===t.value && 'active']"
            @click="type = t.value; refresh()"
          >{{ t.label }}</button>

          <span class="muted sep">排序：</span>
          <select v-model="sortBy" @change="refresh()">
            <option value="latest">最新</option>
            <option value="popular">最热</option>
            <option value="downloads">下载最多</option>
          </select>
        </div>
      </div>

      <div class="right">
        <button class="ghost" @click="openTagFilter = !openTagFilter">筛选标签</button>
        <button class="primary" @click="upload">上传资源</button>
      </div>
    </section>

    <!-- 标签筛选 -->
    <section v-show="openTagFilter" class="tags card">
      <button
        v-for="t in ALL_TAGS"
        :key="t"
        :class="['tag', selectedTags.includes(t) && 'on']"
        @click="toggleTag(t)"
      >#{{ t }}</button>
      <button class="ghost small" @click="clearTags">清空标签</button>
    </section>

    <!-- 资源网格 -->
    <section class="grid">
      <article v-for="item in list" :key="item.id" class="res-card card">
        <div class="cover" :class="item.type">
          <span class="badge">{{ typeLabel(item.type) }}</span>
        </div>

        <div class="body">
          <h3 class="title" :title="item.title">{{ item.title }}</h3>
          <p class="desc">{{ item.desc }}</p>

          <div class="tags-line">
            <span v-for="t in item.tags" :key="t" class="tag">#{{ t }}</span>
          </div>

          <div class="meta">
            <span>由 <router-link :to="`/user/${item.uploader.id}`">{{ item.uploader.name }}</router-link></span>
            <span class="dot">·</span>
            <span class="muted">{{ item.time }}</span>
            <span class="dot">·</span>
            <span class="muted">下载 {{ format(item.downloads) }}</span>
          </div>
        </div>

        <div class="actions">
          <button class="ghost" @click="preview(item)">预览</button>
          <button class="ghost" @click="aiSummary(item)">AI 摘要</button>
          <button class="primary" @click="download(item)">下载</button>
          <button class="icon" :class="item.collected && 'on'" @click="toggleCollect(item)">⭐</button>
        </div>
      </article>
    </section>

    <!-- 分页 -->
    <div class="pager">
      <button class="ghost" :disabled="page===1" @click="prevPage">上一页</button>
      <span class="muted">第 {{ page }} / {{ totalPages }} 页</span>
      <button class="ghost" :disabled="page===totalPages" @click="nextPage">下一页</button>
    </div>

    <!-- 预览抽屉 -->
    <div v-if="drawer.open" class="drawer" @click.self="drawer.open=false">
      <div class="drawer-panel">
        <header class="drawer-hd">
          <h4 class="ellipsis">{{ drawer.item?.title }}</h4>
          <button class="icon" @click="drawer.open=false">✖</button>
        </header>
        <div class="drawer-bd">
          <!-- 这里只做演示，真实预览按类型切换：PDF/图片/视频/Markdown 等 -->
          <p class="muted">这是 {{ typeLabel(drawer.item?.type) }} 预览占位区域。</p>
          <p>{{ drawer.item?.desc }}</p>
        </div>
        <footer class="drawer-ft">
          <button class="ghost" @click="aiSummary(drawer.item)">AI 摘要</button>
          <button class="primary" @click="download(drawer.item)">下载</button>
        </footer>
      </div>
    </div>

    <!-- AI 摘要弹层 -->
    <div v-if="ai.open" class="modal" @click.self="ai.open=false">
      <div class="modal-panel">
        <header class="modal-hd">
          <h4>AI 摘要</h4>
          <button class="icon" @click="ai.open=false">✖</button>
        </header>
        <div class="modal-bd">
          <div v-if="ai.loading" class="muted">AI 正在生成摘要…</div>
          <div v-else class="ai-text" v-html="ai.text"></div>
        </div>
        <footer class="modal-ft">
          <button class="ghost" @click="aiPlan">生成学习计划</button>
          <button class="primary" @click="ai.open=false">完成</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
// ===== 常量 =====
const TYPES = [
  { label: '全部', value: 'all' },
  { label: '文档', value: 'doc' },
  { label: 'PDF', value: 'pdf' },
  { label: '视频', value: 'video' },
  { label: '代码', value: 'code' },
  { label: '数据集', value: 'data' }
]
const ALL_TAGS = ['AI', '算法', '前端', '后端', 'Java', 'Python', 'NLP', 'CV', '大模型', '论文', '面试', '课程']

// ===== 状态 =====
const q = ref('')
const type = ref('all')
const sortBy = ref('latest')
const selectedTags = ref([])
const openTagFilter = ref(false)

const list = ref([])
const page = ref(1)
const pageSize = 8
const total = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

// 预览与 AI 摘要
const drawer = ref({ open: false, item: null })
const ai = ref({ open: false, loading: false, text: '' })

// ===== 生命周期 =====
onMounted(() => refresh())

// ===== 行为 =====
function doSearch() {
  page.value = 1
  fetchList()
}

function refresh() {
  page.value = 1
  fetchList()
}

function prevPage() {
  if (page.value > 1) {
    page.value--
    fetchList()
  }
}
function nextPage() {
  if (page.value < totalPages.value) {
    page.value++
    fetchList()
  }
}

function toggleTag(t) {
  const idx = selectedTags.value.indexOf(t)
  if (idx === -1) selectedTags.value.push(t)
  else selectedTags.value.splice(idx, 1)
  refresh()
}
function clearTags() {
  selectedTags.value = []
  refresh()
}

function preview(item) {
  drawer.value = { open: true, item }
}
function typeLabel(t) {
  return { doc: '文档', pdf: 'PDF', video: '视频', code: '代码', data: '数据集' }[t] || '资源'
}
function toggleCollect(item) { item.collected = !item.collected }
function download(item) {
  // TODO: GET /api/resource/{id}/download
  alert(`开始下载：${item.title}`)
}
function upload() {
  // TODO: 打开上传弹窗或跳转到上传页
  alert('上传入口（TODO）')
}
async function aiSummary(item) {
  ai.value = { open: true, loading: true, text: '' }
  // TODO: POST /api/ai/summary { resourceId }
  await sleep(500)
  ai.value.loading = false
  ai.value.text = `
    <p><strong>要点摘要：</strong></p>
    <ol>
      <li>主题：${item.title}</li>
      <li>核心内容：${item.desc.slice(0, 40)}…</li>
      <li>适用人群：初学者 / 进阶者</li>
    </ol>`
}
function aiPlan() {
  // TODO: POST /api/ai/plan { resourceId }
  alert('已根据该资源生成一份个性化学习计划（TODO）')
}

// ===== 数据获取（mock，接入后端时替换） =====
async function fetchList() {
  // 真实接口示例：
  // const { data } = await api.listResource({ q: q.value, type: type.value, tags: selectedTags.value, sortBy: sortBy.value, page: page.value, pageSize })
  // list.value = data.items; total.value = data.total
  await sleep(300)
  const { items, totalCount } = genMock({ page: page.value, pageSize, q: q.value, type: type.value, tags: selectedTags.value, sortBy: sortBy.value })
  list.value = items
  total.value = totalCount
}

// ===== 工具 =====
const sleep = (ms) => new Promise(r => setTimeout(r, ms))
function format(n) {
  if (n >= 10000) return (n/10000).toFixed(1) + '万'
  if (n >= 1000) return (n/1000).toFixed(1) + 'k'
  return n
}

// 生成 mock 数据
function genMock({ page, pageSize, q, type, tags, sortBy }) {
  const base = (page - 1) * pageSize
  let pool = Array.from({ length: 57 }).map((_, i) => ({
    id: i + 1,
    title: pick([
      '大模型提示工程速查手册',
      'Spring Boot 实战课程笔记',
      'Vue3 组件库最佳实践',
      'NLP 数据增强方法综述',
      '算法岗秋招题库与解析',
      '论文精读：Transformer 解读'
    ]),
    desc: pick([
      '涵盖常用提示模板与对话模式，适合新手快速上手与实践。',
      '完整项目骨架与常见踩坑汇总，面向服务端实战。',
      '从组件设计、样式体系到按需加载与性能优化。',
      '整理多种文本增强方式，并对比其在不同任务的效果。',
      '包含选择题、编程题及详细讲解，侧重思维与方法论。',
      '从结构、训练到推理的全面梳理，配图丰富可视化。'
    ]),
    type: pick(['doc', 'pdf', 'video', 'code', 'data']),
    tags: sample(ALL_TAGS, rand(2, 4)),
    uploader: { id: (i%5)+1, name: pick(['阿土','小白','Jason','夏天','木北']) },
    time: pick(['刚刚','1 小时前','昨天','2 天前','上周']),
    downloads: Math.floor(Math.random() * 20000),
    collected: Math.random() > 0.8
  }))

  // 过滤
  if (q) pool = pool.filter(x => (x.title + x.desc).includes(q))
  if (type && type !== 'all') pool = pool.filter(x => x.type === type)
  if (tags && tags.length) pool = pool.filter(x => tags.every(t => x.tags.includes(t)))

  // 排序
  if (sortBy === 'popular' || sortBy === 'downloads') pool.sort((a,b)=> b.downloads - a.downloads)

  const totalCount = pool.length
  const items = pool.slice(base, base + pageSize)
  return { items, totalCount }

  function pick(arr){ return arr[Math.floor(Math.random()*arr.length)] }
  function sample(arr, n){ return arr.slice().sort(()=>0.5-Math.random()).slice(0,n) }
  function rand(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
}
</script>

<style scoped>
.res-page { padding: 16px 0 40px; }

.card {
  background: #fff;
  border: 1px solid #eef0f3;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,.02);
}

.toolbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px; margin-bottom: 12px; gap: 12px;
}
.toolbar .left { display:flex; flex-direction: column; gap: 8px; }
.search { display:flex; gap:8px; }
.search input{
  width: 420px; max-width: 60vw;
  height: 36px; padding: 0 10px; border:1px solid #e5e7eb; border-radius: 8px;
}
.search .primary { padding: 0 12px; height: 36px; }
.filters { display:flex; align-items:center; gap: 8px; flex-wrap: wrap; }
.sep { margin-left: 8px; }

.tags.card { padding: 10px; margin-bottom: 12px; display:flex; gap:10px; flex-wrap: wrap; }

.grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 12px;
}
.res-card {
  grid-column: span 6; /* 2列 */
  display:flex; flex-direction: column; gap: 10px; padding: 10px;
}
@media (max-width: 900px) {
  .res-card { grid-column: span 12; } /* 小屏 1 列 */
}

.cover {
  height: 120px; border-radius: 8px; background: #f6f7f9; position: relative;
  display:flex; align-items: center; justify-content: center; color:#999; font-size: 13px;
}
.cover .badge {
  position: absolute; left: 10px; top: 10px;
  background: #eaf2ff; color:#1e80ff; padding: 2px 8px; border-radius: 999px; font-size: 12px;
}
.cover.pdf { background: linear-gradient(135deg,#ffecec,#fff); }
.cover.doc { background: linear-gradient(135deg,#eaf6ff,#fff); }
.cover.video { background: linear-gradient(135deg,#fff4e5,#fff); }
.cover.code { background: linear-gradient(135deg,#eef9f1,#fff); }
.cover.data { background: linear-gradient(135deg,#f3f0ff,#fff); }

.body .title { font-size: 16px; margin: 0; line-height: 1.5; }
.body .desc { color:#666; font-size: 14px; margin: 6px 0 8px; }
.tags-line { display:flex; gap:6px; flex-wrap: wrap; margin-bottom: 6px; }
.tag {
  display:inline-block; padding: 2px 8px; border-radius: 999px;
  background:#f5f7fa; color:#555; font-size:12px;
}
.meta { color:#888; font-size: 12px; display:flex; align-items:center; gap:6px; }
.dot { color:#ccc; }

.actions { display:flex; gap: 8px; justify-content: flex-end; }
.actions .icon { border:none; background:#fff; cursor:pointer; font-size:16px; }
.actions .icon.on { color: #f59e0b; }
.primary, .ghost {
  height: 32px; padding: 0 12px; border-radius: 8px; cursor:pointer;
  border:1px solid #e5e7eb; background:#fff;
}
.primary { background:#1e80ff; color:#fff; border-color:#1e80ff; }
.primary:hover { background:#0b5ed7; }
.ghost:hover { background:#f5f7fa; }

.chip {
  border:1px solid #e5e7eb; background:#fff; padding:4px 10px; border-radius:999px;
  cursor:pointer; font-size: 13px; color:#555;
}
.chip.active { background:#eaf2ff; color:#1e80ff; border-color:#cfe3ff; }

.pager {
  display:flex; gap: 12px; justify-content:center; align-items:center; margin-top: 14px;
}
.muted { color:#888; }

/* 抽屉 */
.drawer {
  position: fixed; inset: 0; background: rgba(0,0,0,.35);
  display:flex; justify-content:flex-end; z-index: 50;
}
.drawer-panel {
  width: min(720px, 96vw); height: 100%; background:#fff; display:flex; flex-direction:column;
}
.drawer-hd { display:flex; justify-content:space-between; align-items:center; padding:12px 16px; border-bottom:1px solid #eee; }
.drawer-bd { padding: 16px; flex:1; overflow:auto; }
.drawer-ft { padding: 12px 16px; border-top:1px solid #eee; display:flex; gap:10px; justify-content:flex-end; }
.ellipsis { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* 模态框（AI 摘要） */
.modal {
  position: fixed; inset:0; background: rgba(0,0,0,.35);
  display:flex; align-items:center; justify-content:center; z-index:60;
}
.modal-panel {
  width: min(720px, 96vw); background:#fff; border-radius: 10px; overflow: hidden;
  display:flex; flex-direction:column;
}
.modal-hd, .modal-ft { padding: 12px 16px; border-bottom:1px solid #eee; }
.modal-ft { border-top:1px solid #eee; border-bottom:none; display:flex; justify-content:flex-end; gap:10px; }
.modal-bd { padding: 16px; max-height: 60vh; overflow:auto; }
.ai-text p { margin: 0 0 8px; }
.small { height: 28px; padding: 0 10px; font-size: 12px; }
</style>
