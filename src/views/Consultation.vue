<!-- src/views/consult/Consultation.vue -->
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

/* ========== 顶部搜索 / 筛选状态 ========== */
const q = ref('')
const cate = ref('all')
const sortBy = ref('recommend') // recommend | rating | priceAsc | priceDesc | orders
const priceMin = ref('')
const priceMax = ref('')
const onlyOnline = ref(false) // 仅在线
const tabs = [
  { key: 'experts', label: '专家' },
  { key: 'questions', label: '付费问答' },
  { key: 'orders', label: '我的咨询' }
]
const currentTab = ref('experts')

/* ========== 数据（mock） ========== */
const CATES = [
  { label: '全部', value: 'all' },
  { label: '算法/AI', value: 'ai' },
  { label: '前端', value: 'fe' },
  { label: '后端', value: 'be' },
  { label: '求职/简历', value: 'career' },
  { label: '论文/竞赛', value: 'paper' }
]

const experts = ref([])     // 专家列表
const questions = ref([])   // 付费问答（广场）
const myOrders = ref([])    // 我的订单

onMounted(() => {
  loadMock()
})

function loadMock () {
  experts.value = Array.from({ length: 12 }).map((_, i) => ({
    id: i + 1,
    name: pick(['阿土','小白','Jason','夏天','木北','Leo','Echo','青柠']),
    title: pick(['资深算法工程师','前端 Tech Lead','后端架构师','NLP 研究员','高校讲师','数据科学家']),
    avatar: `https://api.dicebear.com/7.x/initials/svg?seed=${i+1}`,
    rateType: pick(['hour','case']), // 按小时/按次
    price: pick([99, 129, 199, 299, 399, 499]),
    rating: +(Math.random()*1.5 + 3.5).toFixed(1), // 3.5~5.0
    orders: Math.floor(Math.random()*300),
    online: Math.random() > 0.4,
    cate: pick(['ai','fe','be','career','paper']),
    tags: sample(['大模型','面试','系统设计','论文润色','性能优化','简历修改','项目指导','代码评审'], 3),
    intro: pick([
      '5 年 AI/LLM 实战，熟悉提示工程与Agent落地。',
      '大型前端项目经验，擅长工程化与性能优化。',
      '微服务/分布式/缓存/限流，线上可观测与稳定性保障。',
      'NLP/信息抽取/文本分类，科研与比赛指导。',
      '校企项目导师，课程与毕业设计辅导。'
    ])
  }))

  questions.value = Array.from({ length: 8 }).map((_, i) => ({
    id: i + 1,
    title: pick([
      '帮我优化简历的项目描述（算法岗）',
      '大模型应用如何设计上下文记忆？',
      'Vue3 + Spring Boot 权限设计怎么做？',
      '如何准备算法面试的刷题路径？',
      '论文审稿意见的回应要点有哪些？'
    ]),
    price: pick([19, 29, 39, 49, 59]),
    asker: pick(['二狗','小七','Alice','Tom']),
    expert: pick(['阿土','Jason','夏天']),
    status: pick(['开放','已解决']),
    tags: sample(['AI','前端','后端','面试','论文'], 2)
  }))

  myOrders.value = [
    { id: 101, expert: '阿土', topic: 'LLM 提示工程', time: '2025-08-01 20:00', price: 199, status: '已完成' },
    { id: 102, expert: 'Jason', topic: 'Vue3 性能优化', time: '2025-08-12 19:30', price: 299, status: '待进行' }
  ]
}

/* ========== 计算筛选 ========== */
const filteredExperts = computed(() => {
  let arr = experts.value.slice()
  if (q.value) {
    const key = q.value.toLowerCase()
    arr = arr.filter(e =>
      (e.name + e.title + e.intro + e.tags.join(' ')).toLowerCase().includes(key)
    )
  }
  if (cate.value !== 'all') arr = arr.filter(e => e.cate === cate.value)
  if (onlyOnline.value) arr = arr.filter(e => e.online)
  if (priceMin.value) arr = arr.filter(e => e.price >= +priceMin.value)
  if (priceMax.value) arr = arr.filter(e => e.price <= +priceMax.value)

  switch (sortBy.value) {
    case 'rating': arr.sort((a,b)=> b.rating - a.rating); break
    case 'priceAsc': arr.sort((a,b)=> a.price - b.price); break
    case 'priceDesc': arr.sort((a,b)=> b.price - a.price); break
    case 'orders': arr.sort((a,b)=> b.orders - a.orders); break
    default: // recommend
      arr.sort((a,b)=> (b.online - a.online) || (b.rating - a.rating))
  }
  return arr
})

/* ========== 动作 ========== */
function doSearch() { /* 已实时筛选，这里可打点日志 */ }
function resetFilters () {
  q.value=''; cate.value='all'; sortBy.value='recommend'; priceMin.value=''; priceMax.value=''; onlyOnline.value=false
}

function viewExpert (e) { router.push(`/expert/${e.id}`) }
function dmExpert (e) { router.push({ path: '/chat', query: { to: e.id } }) }

const bookDialog = ref({ open:false, expert:null, form:{ topic:'', date:'', time:'', remark:'' } })
function book (e) {
  bookDialog.value = { open: true, expert: e, form: { topic: '', date: '', time: '', remark: '' } }
}
function submitBooking () {
  const { expert, form } = bookDialog.value
  if (!form.topic || !form.date || !form.time) return alert('请填写主题、日期与时间')
  // TODO: POST /api/consult/book { expertId, ...form }
  alert(`已提交预约给「${expert.name}」\n主题：${form.topic}\n时间：${form.date} ${form.time}`)
  bookDialog.value.open = false
}

function askPaid () {
  // TODO: 跳转到发起付费问答页面
  router.push('/question/pay')
}

/* AI 快速分诊（占位） */
const ai = ref({ open:false, loading:false, text:'' })
async function aiTriage () {
  ai.value = { open:true, loading:true, text:'' }
  // TODO: POST /api/ai/consult/triage { q }
  await sleep(600)
  ai.value.loading = false
  ai.value.text = `
    <p><strong>AI 初步判断：</strong></p>
    <ol>
      <li>推荐方向：<em>${cateLabel(cate.value)}</em> 专家；</li>
      <li>建议准备材料：相关代码/日志/题目链接；</li>
      <li>预计耗时：30~60 分钟（按问题复杂度）。</li>
    </ol>
    <p>你可以直接预约评分 4.8+ 的专家以加快解决。</p>
  `
}

/* ========== 工具 ========== */
function cateLabel(v){ return (CATES.find(c=>c.value===v)?.label) || '全部' }
const sleep = (ms)=> new Promise(r=>setTimeout(r, ms))
function sample(arr, n){ return arr.slice().sort(()=>0.5-Math.random()).slice(0,n) }
function pick(arr){ return arr[Math.floor(Math.random()*arr.length)] }
function format(n){ if(n>=10000) return (n/10000).toFixed(1)+'万'; if(n>=1000) return (n/1000).toFixed(1)+'k'; return n }
</script>

<template>
  <div class="consult-page">
    <!-- 工具栏：搜索/筛选/排序 -->
    <section class="toolbar card">
      <div class="row">
        <input class="search" v-model.trim="q" type="search" placeholder="搜索专家、技能、关键词…" @keyup.enter="doSearch" />
        <button class="ghost" @click="aiTriage">AI 快速分诊</button>
      </div>

      <div class="row wrap">
        <div class="group">
          <span class="label">分类：</span>
          <button
            v-for="c in CATES"
            :key="c.value"
            :class="['chip', cate===c.value && 'on']"
            @click="cate=c.value"
          >{{ c.label }}</button>
        </div>

        <div class="group">
          <span class="label">价格：</span>
          <input class="price" v-model="priceMin" type="number" min="0" placeholder="最低" />
          <span class="sep">—</span>
          <input class="price" v-model="priceMax" type="number" min="0" placeholder="最高" />
        </div>

        <div class="group">
          <span class="label">排序：</span>
          <select v-model="sortBy">
            <option value="recommend">综合推荐</option>
            <option value="rating">评分优先</option>
            <option value="priceAsc">价格从低到高</option>
            <option value="priceDesc">价格从高到低</option>
            <option value="orders">成单最多</option>
          </select>
        </div>

        <label class="group">
          <input type="checkbox" v-model="onlyOnline" />
          <span>仅显示在线</span>
        </label>

        <button class="ghost" @click="resetFilters">重置</button>
      </div>

      <!-- 顶部 Tab -->
      <div class="tabs">
        <button
          v-for="t in tabs"
          :key="t.key"
          :class="['tab', currentTab===t.key && 'active']"
          @click="currentTab=t.key"
        >{{ t.label }}</button>
      </div>
    </section>

    <!-- 内容区域 -->
    <section v-if="currentTab==='experts'" class="grid">
      <article v-for="e in filteredExperts" :key="e.id" class="expert card">
        <header class="head">
          <img class="avatar" :src="e.avatar" alt="avatar" />
          <div class="meta">
            <div class="name">
              <router-link :to="`/expert/${e.id}`">{{ e.name }}</router-link>
              <span class="title">{{ e.title }}</span>
            </div>
            <div class="row2">
              <span class="tag" v-for="t in e.tags" :key="t">#{{ t }}</span>
            </div>
            <div class="row3">
              <span class="rating">⭐ {{ e.rating }}</span>
              <span class="dot">·</span>
              <span class="orders">成交 {{ format(e.orders) }}</span>
              <span class="dot">·</span>
              <span class="cate">{{ cateLabel(e.cate) }}</span>
              <span v-if="e.online" class="online">● 在线</span>
            </div>
          </div>
        </header>

        <p class="intro">{{ e.intro }}</p>

        <footer class="foot">
          <div class="price">
            <strong>¥{{ e.price }}</strong>
            <span class="unit">{{ e.rateType === 'hour' ? '/小时' : '/次' }}</span>
          </div>
          <div class="ops">
            <button class="ghost" @click="dmExpert(e)">私信</button>
            <button class="primary" @click="book(e)">预约咨询</button>
            <button class="ghost" @click="viewExpert(e)">详情</button>
          </div>
        </footer>
      </article>
    </section>

    <section v-else-if="currentTab==='questions'" class="qa">
      <div class="qa-hd">
        <button class="primary" @click="askPaid">发起付费问答</button>
      </div>
      <article v-for="qItem in questions" :key="qItem.id" class="qa-item card">
        <h3 class="qa-title">{{ qItem.title }}</h3>
        <div class="qa-meta">
          <span class="muted">提问者：{{ qItem.asker }}</span>
          <span class="dot">·</span>
          <span class="muted">指派专家：{{ qItem.expert }}</span>
          <span class="dot">·</span>
          <span class="muted">价格 ¥{{ qItem.price }}</span>
          <span class="dot">·</span>
          <span class="status" :class="qItem.status==='已解决' && 'done'">{{ qItem.status }}</span>
        </div>
        <div class="qa-tags">
          <span v-for="t in qItem.tags" :key="t" class="tag">#{{ t }}</span>
        </div>
        <div class="qa-ops">
          <button class="ghost">查看详情</button>
          <button class="primary">我也要问</button>
        </div>
      </article>
    </section>

    <section v-else class="orders">
      <article v-for="o in myOrders" :key="o.id" class="order card">
        <div class="o-left">
          <h4 class="o-title">{{ o.topic }}</h4>
          <div class="o-meta">
            <span>专家：{{ o.expert }}</span>
            <span class="dot">·</span>
            <span class="muted">{{ o.time }}</span>
          </div>
        </div>
        <div class="o-right">
          <span class="o-price">¥{{ o.price }}</span>
          <span class="o-status" :class="o.status==='待进行' && 'todo'">{{ o.status }}</span>
          <button class="ghost">进入会话</button>
        </div>
      </article>
    </section>

    <!-- 预约弹层 -->
    <div v-if="bookDialog.open" class="modal" @click.self="bookDialog.open=false">
      <div class="modal-panel">
        <header class="modal-hd">
          <h4>预约咨询 · {{ bookDialog.expert?.name }}</h4>
          <button class="icon" @click="bookDialog.open=false">✖</button>
        </header>
        <div class="modal-bd form">
          <label>
            主题
            <input v-model.trim="bookDialog.form.topic" placeholder="例如：优化简历/代码评审/刷题路径" />
          </label>
          <label class="row2">
            <span>日期</span>
            <input v-model="bookDialog.form.date" type="date" />
            <span>时间</span>
            <input v-model="bookDialog.form.time" type="time" />
          </label>
          <label>
            备注
            <textarea v-model.trim="bookDialog.form.remark" rows="3" placeholder="补充背景、资料链接等"></textarea>
          </label>
          <div class="note muted">提交后专家将确认时间并与您联系。</div>
        </div>
        <footer class="modal-ft">
          <button class="ghost" @click="bookDialog.open=false">取消</button>
          <button class="primary" @click="submitBooking">提交预约</button>
        </footer>
      </div>
    </div>

    <!-- AI 分诊弹层 -->
    <div v-if="ai.open" class="modal" @click.self="ai.open=false">
      <div class="modal-panel">
        <header class="modal-hd">
          <h4>AI 快速分诊结果</h4>
          <button class="icon" @click="ai.open=false">✖</button>
        </header>
        <div class="modal-bd">
          <div v-if="ai.loading" class="muted">AI 正在分析你的需求…</div>
          <div v-else v-html="ai.text"></div>
        </div>
        <footer class="modal-ft">
          <button class="primary" @click="ai.open=false">好的</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<style scoped>
.consult-page { padding: 16px 0 40px; }

/* 卡片与通用 */
.card { background:#fff; border:1px solid #eef0f3; border-radius:10px; box-shadow:0 2px 10px rgba(0,0,0,.02); }
.muted { color:#7a7a7a; }
.dot { color:#bcbcbc; margin: 0 6px; }
.primary, .ghost {
  height: 32px; padding: 0 12px; border-radius: 8px; cursor: pointer; border:1px solid #e5e7eb; background:#fff;
}
.primary { background: #1e80ff; color:#fff; border-color:#1e80ff; }
.primary:hover { background:#0b5ed7; }
.ghost:hover { background:#f5f7fa; }
.tag { display:inline-block; background:#f5f7fa; color:#555; padding:2px 8px; border-radius:999px; font-size:12px; }

/* 工具栏 */
.toolbar { padding: 12px; margin-bottom: 12px; display:flex; flex-direction:column; gap:10px; }
.row { display:flex; gap: 10px; align-items:center; }
.row.wrap { flex-wrap: wrap; }
.search { width: 420px; max-width: 60vw; height: 36px; border:1px solid #e5e7eb; border-radius: 8px; padding: 0 10px; }
.group { display:flex; align-items:center; gap: 8px; }
.label { color:#666; }
.price { width: 96px; height: 32px; border:1px solid #e5e7eb; border-radius:8px; padding:0 8px; }
.sep { color:#bbb; }
.chip { border:1px solid #e5e7eb; background:#fff; padding:4px 10px; border-radius:999px; cursor:pointer; font-size: 13px; color:#555; }
.chip.on { background:#eaf2ff; color:#1e80ff; border-color:#cfe3ff; }
.tabs { display:flex; gap:12px; border-top:1px dashed #eee; padding-top:10px; }
.tab { border:none; background:none; padding:6px 10px; color:#666; cursor:pointer; }
.tab.active { color:#1e80ff; border-bottom:2px solid #1e80ff; font-weight:600; }

/* 专家网格 */
.grid {
  display:grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 12px;
}
.expert { grid-column: span 6; padding: 12px; display:flex; flex-direction:column; gap:8px; }
@media (max-width: 900px) { .expert { grid-column: span 12; } }
.head { display:flex; gap: 10px; }
.avatar { width:56px; height:56px; border-radius:14px; }
.meta { flex:1; }
.name { display:flex; align-items:baseline; gap:8px; }
.name a { font-weight:700; color:#111; text-decoration:none; }
.title { color:#666; font-size: 13px; }
.row2 { display:flex; gap:6px; flex-wrap: wrap; margin-top:4px; }
.row3 { display:flex; gap:8px; align-items:center; color:#777; font-size:13px; margin-top:4px; }
.online { color:#16a34a; margin-left: 8px; }
.intro { color:#444; margin: 4px 2px 4px; }
.foot { display:flex; justify-content:space-between; align-items:center; margin-top: 4px; }
.price strong { font-size:18px; }
.unit { color:#666; margin-left:2px; }

/* 付费问答 */
.qa-hd { display:flex; justify-content:flex-end; margin-bottom: 10px; }
.qa-item { padding: 12px; margin-bottom: 10px; }
.qa-title { margin: 0 0 6px; font-size: 16px; }
.qa-meta { font-size: 13px; color:#666; margin-bottom: 6px; }
.qa-tags { display:flex; gap:6px; flex-wrap: wrap; margin-bottom: 8px; }
.qa-ops { display:flex; gap: 8px; justify-content:flex-end; }
.status { color:#f59e0b; }
.status.done { color:#16a34a; }

/* 订单 */
.order { padding: 12px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; }
.o-title { margin:0 0 4px; }
.o-meta { color:#666; font-size:13px; }
.o-right { display:flex; align-items:center; gap:10px; }
.o-price { font-weight:700; }
.o-status.todo { color:#f59e0b; }

/* 弹层（预约/AI） */
.modal { position: fixed; inset: 0; background: rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center; z-index:50; }
.modal-panel { width:min(680px, 96vw); background:#fff; border-radius:10px; overflow:hidden; display:flex; flex-direction:column; }
.modal-hd, .modal-ft { padding: 10px 12px; border-bottom: 1px solid #f0f2f5; }
.modal-ft { border-bottom: none; border-top: 1px solid #f0f2f5; display:flex; justify-content:flex-end; gap:10px; }
.modal-bd { padding: 12px; max-height: 60vh; overflow:auto; }
.icon { border:none; background:#fff; cursor:pointer; }
.form label { display:flex; flex-direction:column; gap:6px; margin-bottom:10px; }
.form input, .form textarea { border:1px solid #e5e7eb; border-radius:8px; padding:8px; }
.note { font-size:12px; }
</style>
