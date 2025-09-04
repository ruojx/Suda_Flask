<!-- src/views/chat/Chat.vue -->
<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'

/* =========== 状态 =========== */
// 讨论组（mock）
const rooms = ref([
  { id: 1, name: '秋招准备 · 算法/NLP', members: 26, unread: 3, topic: '面经与刷题规划' },
  { id: 2, name: '课程共建 · 深度学习', members: 18, unread: 0, topic: '大模型课程大纲' },
  { id: 3, name: '项目协作 · 教学系统', members: 12, unread: 7, topic: '前后端联调' }
])
const roomQuery = ref('')
const filteredRooms = computed(() =>
  rooms.value.filter(r => (r.name + (r.topic || '')).includes(roomQuery.value.trim()))
)
const currentRoom = ref(rooms.value[0] || null)

// 成员（mock）
const members = ref([
  { id: 1, name: '阿土',   role: '群主',   online: true,  avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=A' },
  { id: 2, name: '夏天',   role: '管理员', online: true, avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=X' },
  { id: 3, name: 'Jason', role: '成员',   online: false, avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=J' },
  { id: 4, name: '小白',   role: '成员',   online: true,  avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=B' }
])

// 消息（mock）
const messages = ref([
  { id: 1, user: '阿土', time: '10:20', avatar: members.value[0].avatar, content: '大家把<strong>算法</strong>面试题单贴一下，我汇总。' },
  { id: 2, user: '夏天', time: '10:22', avatar: members.value[1].avatar, content: '我整理了一个表格，等会儿发链接。' },
  { id: 3, user: '我',   time: '10:25', avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=ME', content: '我这边也做了个 <code>LeetCode</code> 标签分类。', mine: true }
])
const text = ref('')
const typing = ref(false)
const msgListEl = ref(null)

// AI 弹层
const ai = ref({ open: false, loading: false, title: '', html: '' })

/* =========== 生命周期 =========== */
onMounted(scrollToBottom)

/* =========== 行为 =========== */
function enterRoom(r) {
  if (!r || r.id === currentRoom.value?.id) return
  currentRoom.value = r
  // TODO: 拉取 r.id 的历史消息与成员
  messages.value = [{ id: Date.now(), user: '系统', time: '现在', avatar: '', content: `欢迎来到【${r.name}】` }]
  scrollToBottom()
}

function send() {
  const content = text.value.trim()
  if (!content) return
  messages.value.push({
    id: Date.now(),
    user: '我',
    time: new Date().toLocaleTimeString().slice(0,5),
    avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=ME',
    content: escapeHtml(content).replace(/\n/g, '<br/>'),
    mine: true
  })
  text.value = ''
  // TODO: WebSocket 发送到后端
  scrollToBottom()
}

function createRoom() {
  const id = rooms.value.length + 1
  rooms.value.unshift({ id, name: `新讨论组 ${id}`, members: 1, unread: 0, topic: '自由讨论' })
  enterRoom(rooms.value[0])
}

function aiSummary() {
  ai.value = { open: true, loading: true, title: 'AI 总结', html: '' }
  // TODO: POST /api/ai/chat/summary { roomId: currentRoom.value.id }
  setTimeout(() => {
    ai.value.loading = false
    ai.value.html = `
      <p><strong>要点：</strong></p>
      <ol>
        <li>确定秋招算法方向：题单 + 面经整合。</li>
        <li>资料表格由 @夏天 负责，今晚 22:00 前更新。</li>
        <li>下次讨论：周五 19:30，主题 <em>动态规划</em>。</li>
      </ol>`
  }, 600)
}

function aiCompare() {
  ai.value = { open: true, loading: true, title: 'AI 观点对比', html: '' }
  // TODO: POST /api/ai/chat/compare { roomId: currentRoom.value.id }
  setTimeout(() => {
    ai.value.loading = false
    ai.value.html = `
      <table class="cmp">
        <thead><tr><th>观点</th><th>支持</th><th>反对</th></tr></thead>
        <tbody>
          <tr><td>先刷题</td><td>短期提升快</td><td>系统性不足</td></tr>
          <tr><td>先打基础</td><td>长线收益稳</td><td>见效慢</td></tr>
        </tbody>
      </table>
      <p><strong>结论：</strong>并行：每日 2 题 + 每周 1 次专题。</p>`
  }, 700)
}

function exportChat() {
  // TODO: 导出 Markdown/PDF
  alert('导出记录（TODO）')
}

/* =========== 工具 =========== */
function scrollToBottom() {
  nextTick(() => {
    const el = msgListEl.value
    if (el) el.scrollTop = el.scrollHeight
  })
}
const sleep = ms => new Promise(r => setTimeout(r, ms))
function escapeHtml (s){
  return s.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))
}
</script>

<template>
  <div class="chat-page">
    <!-- 左：讨论组 -->
    <aside class="sidebar card">
      <header class="side-hd">
        <h3>讨论组</h3>
        <button class="ghost small" @click="createRoom">+ 新建</button>
      </header>

      <div class="side-search">
        <input v-model="roomQuery" placeholder="搜索讨论组…" />
      </div>

      <ul class="room-list">
        <li
          v-for="r in filteredRooms"
          :key="r.id"
          :class="['room', currentRoom?.id === r.id && 'active']"
          @click="enterRoom(r)"
        >
          <div class="title ellipsis">{{ r.name }}</div>
          <div class="meta">
            <span class="muted">{{ r.members }} 人</span>
            <span class="dot">·</span>
            <span class="muted">{{ r.unread }} 未读</span>
          </div>
        </li>
      </ul>
    </aside>

    <!-- 中：消息区 -->
    <section class="main card" v-if="currentRoom">
      <header class="main-hd">
        <div>
          <h3 class="room-name">{{ currentRoom.name }}</h3>
          <div class="muted small">主题：{{ currentRoom.topic || '自由讨论' }}</div>
        </div>
        <div class="tools">
          <button class="ghost" @click="aiSummary">AI 总结</button>
          <button class="ghost" @click="aiCompare">AI 观点对比</button>
          <button class="ghost" @click="exportChat">导出记录</button>
        </div>
      </header>

      <div class="msg-list" ref="msgListEl">
        <div v-for="m in messages" :key="m.id" :class="['msg', m.mine && 'mine']">
          <img v-if="m.avatar" class="avatar" :src="m.avatar" alt="avatar" />
          <div class="bubble">
            <div class="line">
              <span class="name" :class="{me: m.mine}">{{ m.user }}</span>
              <span class="time muted">{{ m.time }}</span>
            </div>
            <div class="content" v-html="m.content"></div>
          </div>
        </div>

        <div v-if="typing" class="typing muted">对方正在输入…</div>
      </div>

      <footer class="composer">
        <textarea
          v-model="text"
          rows="3"
          maxlength="1000"
          placeholder="发言，支持 @、粘贴图片/代码片段…"
          @keydown.enter.exact.prevent="send"
        />
        <div class="bar">
          <div class="left">
            <button class="icon" title="附件">📎</button>
            <button class="icon" title="表情">😊</button>
            <button class="icon" title="话题">#</button>
          </div>
          <div class="right">
            <span class="muted">{{ text.length }}/1000</span>
            <button class="primary" :disabled="!text.trim()" @click="send">发送</button>
          </div>
        </div>
      </footer>
    </section>

    <!-- 右：成员 -->
    <aside class="member card" v-if="currentRoom">
      <header class="side-hd">
        <h3>成员 ({{ members.length }})</h3>
        <button class="ghost small">邀请</button>
      </header>
      <ul class="member-list">
        <li v-for="u in members" :key="u.id" class="member-item">
          <img :src="u.avatar" class="avatar" alt />
          <div class="u">
            <div class="name ellipsis">{{ u.name }}</div>
            <div class="role muted small">{{ u.role || '成员' }}</div>
          </div>
          <span class="status" :class="u.online ? 'on' : 'off'"></span>
        </li>
      </ul>
    </aside>

    <!-- AI 弹层 -->
    <div v-if="ai.open" class="modal" @click.self="ai.open=false">
      <div class="modal-panel">
        <header class="modal-hd">
          <h4>{{ ai.title }}</h4>
          <button class="icon" @click="ai.open=false">✖</button>
        </header>
        <div class="modal-bd">
          <div v-if="ai.loading" class="muted">AI 正在生成……</div>
          <div v-else v-html="ai.html" class="ai-text"></div>
        </div>
        <footer class="modal-ft">
          <button class="ghost">保存到笔记</button>
          <button class="primary" @click="ai.open=false">完成</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-page {
  display: grid;
  grid-template-columns: 260px 1fr 260px;
  gap: 12px;
  padding: 12px 0 32px;
}
.card { background:#fff; border:1px solid #eef0f3; border-radius:10px; overflow:hidden; }
.muted { color:#7a7a7a; }
.small { font-size:12px; }
.dot { color:#c9c9c9; }

/* 左侧 */
.sidebar { display:flex; flex-direction:column; min-height: 70vh; }
.side-hd { display:flex; align-items:center; justify-content:space-between; padding:10px 12px; border-bottom:1px solid #f0f2f5; }
.side-search { padding:10px 12px; }
.side-search input{ width:100%; height:32px; border:1px solid #e5e7eb; border-radius:8px; padding:0 10px; }
.room-list { list-style:none; margin:0; padding: 6px; display:flex; flex-direction:column; gap:6px; }
.room { padding:8px; border-radius:8px; cursor:pointer; }
.room:hover { background:#f7f9fb; }
.room.active { background:#eaf2ff; }
.room .title { font-weight:600; }
.room .meta { font-size:12px; }

/* 中间 */
.main { display:flex; flex-direction:column; min-height: 70vh; }
.main-hd { padding:10px 12px; border-bottom:1px solid #f0f2f5; display:flex; align-items:center; justify-content:space-between; gap:10px; }
.tools { display:flex; gap:8px; }
.msg-list { flex:1; padding:12px; overflow:auto; background:#fcfdff; }
.msg { display:flex; gap:8px; margin-bottom:10px; max-width: 80%; }
.msg.mine { margin-left:auto; flex-direction: row-reverse; }
.msg .avatar { width:28px; height:28px; border-radius:8px; }
.bubble { background:#fff; border:1px solid #eef0f3; border-radius:10px; padding:8px 10px; }
.msg.mine .bubble{ background:#eaf2ff; border-color:#d6e6ff; }
.line { display:flex; gap:8px; align-items:center; margin-bottom:4px; }
.name { font-weight:600; }
.name.me { color:#1e80ff; }
.content :deep(code){ background:#f5f5f5; padding:0 4px; border-radius:4px; }
.typing { text-align:center; margin-top:6px; }

/* 输入区 */
.composer { border-top:1px solid #f0f2f5; padding:8px; display:flex; flex-direction:column; gap:8px; }
.composer textarea{
  width:100%; border:1px solid #e5e7eb; border-radius:8px; padding:8px; resize:vertical;
}
.bar { display:flex; align-items:center; justify-content:space-between; }
.left { display:flex; gap:6px; }
.icon { border:none; background:#fff; cursor:pointer; font-size:18px; }
.primary, .ghost {
  height:32px; padding:0 12px; border-radius:8px; cursor:pointer; border:1px solid #e5e7eb; background:#fff;
}
.primary { background:#1e80ff; color:#fff; border-color:#1e80ff; }
.primary:hover { background:#0b5ed7; }
.ghost:hover { background:#f5f7fa; }

/* 右侧 */
.member { min-height: 70vh; }
.member-list { list-style:none; margin:0; padding:8px; display:flex; flex-direction:column; gap:6px; }
.member-item { display:flex; align-items:center; gap:8px; padding:6px 8px; border-radius:8px; }
.member-item:hover{ background:#f7f9fb; }
.member .avatar { width:28px; height:28px; border-radius:8px; }
.u .name { font-weight:600; }
.status { width:8px; height:8px; border-radius:50%; margin-left:auto; }
.status.on { background:#16a34a; }
.status.off { background:#cbd5e1; }

/* 弹层（AI） */
.modal { position:fixed; inset:0; background:rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center; z-index:50; }
.modal-panel { width:min(720px,96vw); background:#fff; border-radius:10px; overflow:hidden; display:flex; flex-direction:column; }
.modal-hd, .modal-ft { padding:10px 12px; border-bottom:1px solid #f0f2f5; }
.modal-ft { border-bottom:none; border-top:1px solid #f0f2f5; display:flex; justify-content:flex-end; gap:8px; }
.modal-bd { padding:12px; max-height:60vh; overflow:auto; }
.ai-text table { width:100%; border-collapse: collapse; }
.ai-text th, .ai-text td { border:1px solid #eee; padding:6px; }

/* 响应式 */
@media (max-width: 1024px) {
  .chat-page { grid-template-columns: 220px 1fr; }
  .member { display:none; }
}
@media (max-width: 720px) {
  .chat-page { grid-template-columns: 1fr; }
  .sidebar { display:none; }
}
</style>
