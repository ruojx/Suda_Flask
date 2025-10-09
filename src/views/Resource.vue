<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  listApi, previewApi, downloadApi,
  likeApi, unlikeApi, favoriteApi, unfavoriteApi,
  aiSummaryApi, aiPlanApi,
  createFileApi, createLinkApi, tagListApi
} from '@/api/resource'
import dayjs from "dayjs"
import { useUserStore } from '@/stores/userStore'

const userStore = useUserStore()
const userName = userStore.userName
/** ====== 上传弹窗 ====== */
const uploader = ref({
  open: false,
  form: {
    title: '',
    type: 'doc', // 'doc' | 'docx' | 'ppt' | 'pptx' | 'pdf' | 'zip' | 'link'
    desc: '',
    tagsText: '',   // 逗号分隔 -> 提交时转数组
    cover: '',
    file: null,
    url: ''
  }
})

function upload() { uploader.value.open = true }
function onPickFile(e) {
  const files = e.target.files
  uploader.value.form.file = files && files[0] ? files[0] : null
}

async function submitUpload() {
  const f = uploader.value.form
  if (!f.title || !f.type) return alert('请填写标题和类型')

  try {
    if (f.type === 'link') {
      await createLinkApi({
        title: f.title,
        type: 'link',
        desc: f.desc || '',
        tags: splitTags(f.tagsText),
        cover: f.cover || '',
        url: f.url || ''
      })
    } else {
      if (!f.file) return alert('请选择资源文件')
      const formData = new FormData()
      formData.append('title', f.title)
      formData.append('type', f.type)
      formData.append('desc', f.desc || '')
      const tags = splitTags(f.tagsText)
      if (tags.length) formData.append('tags', tags.join(','))
      if (f.cover) formData.append('cover', f.cover)
      formData.append('file', f.file)
      await createFileApi(formData)
    }
    uploader.value.open = false
    refresh()
    alert('上传成功！')
  } catch (err) {
    console.error(err)
    alert('上传失败，请稍后重试')
  }
}

/** ====== 常量（前端筛选）====== */
const TYPES = [
  { label: '全部', value: 'all' },
  { label: '文档', value: 'doc/docx' },
  { label: 'ppt', value: 'ppt/pptx' },
  { label: 'PDF', value: 'pdf' },
  { label: '压缩包', value: 'zip' },
  { label: '网页链接', value: 'link' }
]

/** ====== 标签（从接口获取，失败则用默认） ====== */
const ALL_TAGS = ref(['AI', '算法', '前端', '后端', 'Java', 'Python', 'NLP', 'CV', '大模型', '论文', '面试', '课程'])
async function loadTags() {
  try {
    const { data } = await tagListApi({})
    if (Array.isArray(data?.items) && data.items.length) {
      ALL_TAGS.value = data.items
    }
  } catch (e) { console.warn('tagListApi failed, fallback to default') }
}

/** ====== 列表状态 ====== */
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

const drawer = ref({ open: false, item: null })
const ai = ref({ open: false, loading: false, text: '' })

onMounted(async () => {
  await loadTags()
  refresh()
})

function toggleTagFilter() { openTagFilter.value = !openTagFilter.value }
function doSearch() { page.value = 1; fetchList() }
function refresh() { page.value = 1; fetchList() }
function prevPage() { if (page.value > 1) { page.value--; fetchList() } }
function nextPage() { if (page.value < totalPages.value) { page.value++; fetchList() } }

function toggleTag(t) {
  const i = selectedTags.value.indexOf(t)
  i === -1 ? selectedTags.value.push(t) : selectedTags.value.splice(i, 1)
  refresh()
}
function clearTags() { selectedTags.value = []; refresh() }

const loadingPreview = ref(false)

function buildPreviewUrl(rawUrl, fileType) {
  const t = String(fileType || '').toLowerCase()
  // Office 文档走 Office Online
  if (/^docx?$|^pptx?$|^xlsx?$/.test(t)) {
    return 'https://view.officeapps.live.com/op/embed.aspx?src=' +
      encodeURIComponent(rawUrl)
  }
  // 其他：直接用原地址
  return rawUrl
}

async function preview(item) {
  if (item.type === 'zip') return alert('该类型不支持在线预览')
  if (item.type === 'link' && item.url) {
    window.open(item.url, '_blank', 'noopener')
    return
  }

  try {
    const { data } = await previewApi(item.id) // { previewUrl, expiresIn }
    if (!data?.previewUrl) return alert('预览地址为空')

    const finalUrl = buildPreviewUrl(data.previewUrl, item.type)
    // 🚀 直接新开页面
    window.open(finalUrl, '_blank', 'noopener')
  } catch (e) {
    console.error(e)
    alert('预览失败')
  }
}




function typeLabel(t) {
  const map = { doc: '文档', docx: '文档', ppt: 'PPT', pptx: 'PPT', pdf: 'PDF', zip: '压缩包', link: '网页链接' }
  return map[t] || '资源'
}

/** —— 收藏 —— */
async function togglefavorite(item) {
  try {
    let api
    if (item.favorited) {
      api = unfavoriteApi
    } else {
      api = favoriteApi
    }
    const { data } = await api(item.id)
    if (typeof data?.favoriteCount === 'number') {
      item.favoriteCount = data.favoriteCount
      item.favorited = data.favorite
    }
  } catch (e) {
    console.error('收藏失败', e)
  }
}

/** —— 点赞 —— */
async function toggleLike(item) {
  try {
    let api
    if (item.liked) {
      api = unlikeApi   // 已点赞 → 取消
    } else {
      api = likeApi     // 未点赞 → 点赞
    }
    const { data } = await api(item.id)
    if (typeof data?.likeCount === 'number') {
      item.likeCount = data.likeCount
      item.liked = data.like
    }

  } catch (e) {
    console.error('点赞失败', e)
  }
}


/** —— 下载 —— */
async function download(item) {
  if (item.type === 'link' && item.url) { window.open(item.url, '_blank', 'noopener'); return }
  try {
    const { data } = await downloadApi(item.id)
    const url = data?.url
    if (url) window.open(url, '_blank', 'noopener')
    else alert('下载地址获取失败')
  } catch (e) {
    console.error(e); alert('下载失败')
  }
}

/** —— AI 摘要 / 计划 —— */
async function aiSummary(item) {
  if (item.type === 'zip' || item.type === 'link') return
  ai.value = { open: true, loading: true, text: '' }
  try {
    const { data } = await aiSummaryApi({ id: item.id })
    ai.value.text = data?.html || '<p>暂无摘要</p>'
  } catch (e) {
    console.error(e); ai.value.text = '<p>生成失败，请稍后重试</p>'
  } finally {
    ai.value.loading = false
  }
}
async function aiPlan() {
  const item = drawer.value.item
  if (!item) return
  ai.value = { open: true, loading: true, text: '' }
  try {
    const { data } = await aiPlanApi({ id: item.id })
    ai.value.text = data?.html || '<p>暂无学习计划</p>'
  } catch (e) {
    console.error(e); ai.value.text = '<p>生成失败，请稍后重试</p>'
  } finally {
    ai.value.loading = false
  }
}

/** —— 列表：统一走接口 —— */
async function fetchList() {
  try {
    const types = resolveTypes(type.value) // 'doc/docx' -> ['doc','docx']
    const { data } = await listApi({
      q: q.value || '',
      types,                       // 多类型筛选
      tags: selectedTags.value,    // 直接传数组
      sortBy: sortBy.value,        // latest | popular | downloads
      page: page.value,
      pageSize
    })
    list.value = (data?.rows || []).map(item => ({
      ...item,
      favorited: false, // 默认未收藏，需登录后从用户收藏列表获取
      liked: false   // 新增字段，默认未点赞
    }))
    total.value = data?.total || 0
  } catch (e) {
    console.error(e)
    list.value = []
    total.value = 0
  }
}

/** —— 工具 —— */
function resolveTypes(v) {
  if (v === 'all') return []
  if (v.includes('/')) return v.split('/').map(s => s.trim()).filter(Boolean)
  return [v]
}
function splitTags(text) {
  return (text || '')
    .split(',')
    .map(s => s.trim())
    .filter(Boolean)
}
function format(n) {
  if (n >= 10000) return (n / 10000).toFixed(1) + '万'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k'
  return String(n || 0)
}
</script>

<template>
  <!-- 上传弹窗 -->
  <div class="res-page">
    <div v-if="uploader.open" class="modal" @click.self="uploader.open = false">
      <div class="modal-panel">
        <header class="modal-hd">
          <h4>上传资源</h4>
          <button class="icon" @click="uploader.open = false">✖</button>
        </header>
        <div class="modal-bd form">
          <label>
            标题
            <input v-model.trim="uploader.form.title" placeholder="请输入标题" />
          </label>

          <label>
            类型
            <select v-model="uploader.form.type">
              <option value="doc">文档（doc / docx）</option>
              <!-- <option value="docx">文档（docx）</option> -->
              <option value="ppt">PPT（ppt / pptx）</option>
              <!-- <option value="pptx">PPT（pptx）</option> -->
              <option value="pdf">PDF</option>
              <option value="zip">压缩包</option>
              <option value="link">网页链接</option>
            </select>
          </label>

          <label>
            描述
            <textarea v-model.trim="uploader.form.desc" rows="3" placeholder="简要描述资源内容"></textarea>
          </label>

          <label>
            标签（逗号分隔）
            <input v-model.trim="uploader.form.tagsText" placeholder="AI, 前端, 算法…" />
          </label>

          <label>
            封面图片 URL
            <input v-model.trim="uploader.form.cover" placeholder="可选，展示用图片链接" />
          </label>

          <label v-if="uploader.form.type !== 'link'">
            资源文件
            <input type="file" @change="onPickFile" />
          </label>

          <label v-else>
            网页地址
            <input v-model.trim="uploader.form.url" placeholder="https://example.com" />
          </label>
        </div>
        <footer class="modal-ft">
          <button class="ghost" @click="uploader.open = false">取消</button>
          <button class="primary" @click="submitUpload">提交</button>
        </footer>
      </div>
    </div>


    <!-- 顶部工具栏 -->
    <section class="toolbar card">
      <div class="left">
        <div class="search">
          <input v-model.trim="q" type="search" placeholder="搜索标题、标签、上传者…" @keyup.enter="doSearch" />
          <button class="primary" @click="doSearch">搜索</button>
        </div>
        <div class="filters">
          <span class="muted">类型：</span>
          <button v-for="t in TYPES" :key="t.value" :class="['chip', type === t.value && 'active']"
            @click="type = t.value; refresh()">{{ t.label }}</button>

          <span class="muted sep">排序：</span>
          <select v-model="sortBy" @change="refresh()">
            <option value="latest">最新</option>
            <option value="popular">最热</option>
            <option value="downloads">下载最多</option>
          </select>
        </div>
      </div>

      <div class="right">
        <button class="ghost" @click="toggleTagFilter">筛选标签</button>
        <button class="primary" @click="upload">上传资源</button>
      </div>
    </section>

    <!-- 标签筛选 -->
    <section v-show="openTagFilter" class="tags card">
      <button v-for="t in ALL_TAGS" :key="t" :class="['tag', selectedTags.includes(t) && 'on']"
        @click="toggleTag(t)">#{{ t }}</button>
      <button class="ghost small" @click="clearTags">清空标签</button>
    </section>

    <!-- 资源网格 -->
    <section class="grid">
      <article v-for="item in list" :key="item.id" class="res-card card">
        <div class="cover" :class="item.type">
          <img v-if="item.cover" :src="item.cover" alt="cover" class="cover-img" />
          <span class="badge">{{ typeLabel(item.type) }}</span>
        </div>

        <div class="body">
          <h3 class="title" :title="item.title">{{ item.title }}</h3>
          <p class="desc">{{ item.description }}</p>

          <div class="tags-line">
            <span v-for="t in (item.tags ? item.tags.split(',') : [])" :key="t" class="tag">#{{ t }}</span>
          </div>

          <div class="meta">
            <span class="dot">{{ userName }}</span>
            <span class="dot">·</span>
            <span class="muted">
              {{ dayjs(item.updateTime).format("YYYY-MM-DD HH:mm:ss") }}
            </span>
            <span class="dot">·</span>
            <span class="muted">下载 {{ format(item.downloadCount) }}</span>
          </div>
        </div>

        <div class="actions">
          <!-- 网页链接：只显示跳转 -->
          <template v-if="item.type === 'link'">
            <button class="primary" @click="download(item)">跳转</button>
          </template>

          <!-- 压缩包：仅下载 -->
          <template v-else-if="item.type === 'zip'">
            <button class="primary" @click="download(item)">下载</button>
          </template>

          <!-- 其他(doc/docx/ppt/pptx/pdf)：预览+AI摘要+下载 -->
          <template v-else>
            <button class="ghost" @click="preview(item)">预览</button>
            <button class="ghost" @click="aiSummary(item)">AI 摘要</button>
            <button class="primary" @click="download(item)">下载</button>
          </template>

          <div class="spacer"></div>
          <button @click="toggleLike(item)">
            <span v-if="item.liked">💖 已赞 {{ item.likeCount }}</span>
            <span v-else>🤍 点赞 {{ item.likeCount }}</span>
          </button>
          <button class="icon favorite-btn" :class="{ on: item.favorited }" @click="togglefavorite(item)">
            <span>{{ item.favorited ? '★' : '☆' }}{{ item.favoriteCount }}</span>
          </button>
        </div>
      </article>
    </section>

    <!-- 分页 -->
    <div class="pager">
      <button class="ghost" :disabled="page === 1" @click="prevPage">上一页</button>
      <span class="muted">第 {{ page }} / {{ totalPages }} 页</span>
      <button class="ghost" :disabled="page === totalPages" @click="nextPage">下一页</button>
    </div>

    <div v-if="drawer.open" class="viewer-wrap">
      <header class="viewer-hd">
        <h3>{{ drawer.item?.title }}</h3>
        <div class="actions">
          <small v-if="drawer.expiresIn">链接 {{ Math.ceil(drawer.expiresIn / 60) }} 分钟内有效</small>
          <button class="close-btn" @click="drawer.open = false">✖</button>
        </div>
      </header>


    </div>




    <!-- AI 摘要弹层 -->
    <div v-if="ai.open" class="modal" @click.self="ai.open = false">
      <div class="modal-panel">
        <header class="modal-hd">
          <h4>AI 摘要</h4>
          <button class="icon" @click="ai.open = false">✖</button>
        </header>
        <div class="modal-bd">
          <div v-if="ai.loading" class="muted">AI 正在生成摘要…</div>
          <div v-else class="ai-text" v-html="ai.text"></div>
        </div>
        <footer class="modal-ft">
          <button class="ghost" @click="aiPlan">生成学习计划</button>
          <button class="primary" @click="ai.open = false">完成</button>
        </footer>
      </div>
    </div>
  </div>
</template>


<style scoped>
.res-page {
  padding: 16px 0 40px;
}

.card {
  background: #fff;
  border: 1px solid #eef0f3;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, .02);
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 12px;
  gap: 12px;
}

.toolbar .left {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.search {
  display: flex;
  gap: 8px;
}

.search input {
  width: 420px;
  max-width: 60vw;
  height: 36px;
  padding: 0 10px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.search .primary {
  padding: 0 12px;
  height: 36px;
}

.filters {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.sep {
  margin-left: 8px;
}

/* 标签筛选 */
.tags .tag {
  margin: 4px;
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 16px;
  background: #f8f9fa;
  color: #333;
  cursor: pointer;
  transition: all 0.2s;
}

.tags .tag:hover {
  border-color: #409eff;
  color: #409eff;
}

/* 选中态 */
.tags .tag.on {
  background: #409eff;
  /* 蓝底 */
  color: #fff;
  /* 白字 */
  border-color: #409eff;
  /* 去掉灰边 */
  font-weight: bold;
  /* 粗体更明显 */
  box-shadow: 0 0 4px rgba(64, 158, 255, 0.5);
}

/* 网格 */
.grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 12px;
}

.res-card {
  grid-column: span 6;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
}

@media (max-width: 900px) {
  .res-card {
    grid-column: span 12;
  }
}

/* 封面 */
.cover {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  height: 160px;
  background: #f6f7f9;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.cover .badge {
  position: absolute;
  left: 10px;
  top: 10px;
  background: #eaf2ff;
  color: #1e80ff;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, .08);
}

.cover.pdf {
  background: linear-gradient(135deg, #ffecec, #fff);
}

.cover.doc {
  background: linear-gradient(135deg, #eaf6ff, #fff);
}

.cover.docx {
  background: linear-gradient(135deg, #eaf6ff, #fff);
}

.cover.ppt {
  background: linear-gradient(135deg, #fff4e5, #fff);
}

.cover.pptx {
  background: linear-gradient(135deg, #fff4e5, #fff);
}

.cover.zip {
  background: linear-gradient(135deg, #fff8d6, #fff);
}

.cover.link {
  background: linear-gradient(135deg, #f3f0ff, #fff);
}

.body .title {
  font-size: 16px;
  margin: 0;
  line-height: 1.5;
}

.body .desc {
  color: #666;
  font-size: 14px;
  margin: 6px 0 8px;
}

.tags-line {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  background: #f5f7fa;
  color: #555;
  font-size: 12px;
}

.meta {
  color: #888;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  color: #ccc;
}

/* 操作区 */
.actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.actions .spacer {
  flex: 1;
}

.actions .icon {
  border: none;
  background: #fff;
  cursor: pointer;
  font-size: 16px;
}

.actions .icon.on {
  color: #f59e0b;
}

.favorite-btn {
  font-size: 20px;
  cursor: pointer;
  border: none;
  background: transparent;
  transition: transform .2s ease, color .2s ease, text-shadow .2s ease;
  color: #999;
  /* 默认灰色 */
}

.favorite-btn:hover {
  transform: scale(1.15);
  color: #ffb400;
  /* hover 时金色 */
}

.favorite-btn.on {
  color: #ffb400;
  /* 已收藏 → 金色 */

  transform: scale(1.2);
}

.primary,
.ghost {
  height: 32px;
  padding: 0 12px;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid #e5e7eb;
  background: #fff;
}

.primary {
  background: #1e80ff;
  color: #fff;
  border-color: #1e80ff;
}

.primary:hover {
  background: #0b5ed7;
}

.ghost:hover {
  background: #f5f7fa;
}

.small {
  height: 28px;
  font-size: 12px;
}

/* 分页 */
.pager {
  display: flex;
  gap: 12px;
  justify-content: center;
  align-items: center;
  margin-top: 14px;
}

.muted {
  color: #888;
}

/* 抽屉 */
.drawer {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, .35);
  display: flex;
  justify-content: flex-end;
  z-index: 50;
}

.drawer-panel {
  width: min(720px, 96vw);
  height: 100%;
  background: #fff;
  display: flex;
  flex-direction: column;
}

.drawer-hd {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
}

.drawer-bd {
  padding: 16px;
  flex: 1;
  overflow: auto;
}

.drawer-bd .preview-cover img {
  width: 100%;
  border-radius: 8px;
  margin-top: 8px;
}

.drawer-bd .link-tip a {
  color: #1e80ff;
  text-decoration: none;
}

.drawer-bd .link-tip a:hover {
  text-decoration: underline;
}

.drawer-ft {
  padding: 12px 16px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 模态框（AI 摘要） */
.modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, .35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 60;
}

.modal-panel {
  width: min(720px, 96vw);
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 24px rgba(0, 0, 0, .12);
}

.modal-hd {
  padding: 14px 18px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-hd h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.modal-hd .icon {
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #666;
}

.modal-hd .icon:hover {
  color: #111;
}

.modal-bd {
  padding: 16px 20px;
  max-height: 60vh;
  overflow: auto;
}

.modal-ft {
  border-top: 1px solid #eee;
  padding: 12px 16px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 表单 */
.form label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
  font-size: 14px;
  color: #333;
}

.form input,
.form textarea,
.form select {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 14px;
  transition: border-color .15s, box-shadow .15s;
}

.form input:focus,
.form textarea:focus,
.form select:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, .15);
  outline: none;
}

.form textarea {
  resize: vertical;
  min-height: 60px;
}

/* 按钮 */
button.primary {
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 6px 14px;
  cursor: pointer;
}

button.primary:hover {
  background: #3a8ee6;
}

button.ghost {
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 6px 14px;
  cursor: pointer;
}

button.ghost:hover {
  background: #eee;
}

.viewer-wrap {
  display: flex;
  flex-direction: column;
  width: 90%;
  max-width: 960px;
  margin: 20px auto;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  animation: fadeIn .25s ease-out;
}

.viewer-hd {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  background: #f9fafb;
}

.viewer-hd .title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.viewer-hd .actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.viewer-hd .expires {
  font-size: 12px;
  color: #888;
}

.close-btn {
  border: none;
  background: transparent;
  font-size: 16px;
  cursor: pointer;
  color: #666;
  transition: color .2s;
}

.close-btn:hover {
  color: #000;
}

.link-btn,
.download-btn {
  display: inline-block;
  padding: 8px 14px;
  background: #409eff;
  color: #fff;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
  transition: background .2s;
}

.link-btn:hover,
.download-btn:hover {
  background: #337ecc;
}

.viewer-loading {
  height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 14px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
