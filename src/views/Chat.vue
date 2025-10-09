<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import {
  listGroupsApi, groupMembersApi, groupMessagesApi, createGroupApi, inviteMembersApi, searchUsersApi,
  listContactsApi, dmMessagesApi, startDmApi,
  sendMsgApi, readAckApi,
  renameGroupApi, dissolveGroupApi, deleteDmApi    // ← 新增
} from '@/api/chat'
import { useUserStore } from '@/stores/userStore'
const userStore = useUserStore()


/** ========== 修改群名（直接调用，无二次确认） ========== */
async function renameCurrentGroup() {
  if (!currentGroup.value?.id) return
  const name = window.prompt('请输入新的群名称：', currentGroup.value.name || '')
  if (!name || !name.trim()) return
  try {
    await renameGroupApi(currentGroup.value.id, name.trim())
    // 本地更新
    currentGroup.value.name = name.trim()
    const idx = groups.value.findIndex(g => g.id === currentGroup.value.id)
    if (idx >= 0) groups.value[idx].name = name.trim()
  } catch (e) {
    console.error('rename group error', e)
    window.alert('修改群名失败')
  }
}

/** ========== 解散群聊（直接调用，无二次确认） ========== */
async function dissolveCurrentGroup() {
  if (!currentGroup.value?.id) return
  try {
    await dissolveGroupApi(currentGroup.value.id)
    // 从列表移除，并清空当前群
    groups.value = groups.value.filter(g => g.id !== currentGroup.value.id)
    currentGroup.value = null
    // 切回 DM 或者保持 group 空状态
    if (mode.value === 'group') {
      if (groups.value.length) {
        await enterGroup(groups.value[0])
      } else {
        // 无群可进，清空群成员与消息
        groupMembers.value = []
      }
    }
  } catch (e) {
    console.error('dissolve group error', e)
    window.alert('解散失败')
  }
}

/** ========== 删除当前私聊（直接调用，无二次确认） ========== */
async function deleteCurrentDM() {
  if (!currentDM.value?.id) return
  const peerId = currentDM.value.id
  try {
    await deleteDmApi(peerId)
    // 从联系人列表移除
    contacts.value = contacts.value.filter(u => u.id !== peerId)
    // 清空当前 DM
    currentDM.value = null
    // 若还有联系人，自动打开第一个
    if (contacts.value.length) {
      await openDM(contacts.value[0])
    } else {
      // 没联系人则停留在 DM 空态
      dmMessageStore.value = {}
      dmLastMsgId.value = {}
    }
  } catch (e) {
    console.error('delete dm error', e)
    window.alert('删除私聊失败')
  }
}

/* ========== 邀请 ========== */
/* ========== 发起私信（搜索 -> 选择 -> 开始） ========== */
const addDm = ref({
  open: false,
  loading: false,
  kw: '',
  candidates: [],   // {id, username, name, avatar}
  selectedId: null  // 选中的 userId
})

function openAddDm() {
  addDm.value.open = true
  addDm.value.kw = ''
  addDm.value.candidates = []
  addDm.value.selectedId = null
}

async function searchDmCandidates() {
  const kw = addDm.value.kw.trim()
  if (!kw) return
  addDm.value.loading = true
  try {
    const res = await searchUsersApi(kw)
    const all = Array.isArray(res?.data) ? res.data : []
    addDm.value.candidates = all
      .map(u => ({
        id: u.id,
        username: u.username ?? '',
        name: u.name ?? u.username ?? '',
        avatar:
          u.avatar || u.avatarUrl ||
          `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(u.name || u.username || 'U')}`
      }))
      .filter(u => !!u.id && String(u.id) !== String(me.value.id))
  } catch (e) {
    console.error('search dm candidates error', e)
  } finally {
    addDm.value.loading = false
  }
}

function chooseDmTarget(id) {
  addDm.value.selectedId = id
}

async function confirmAddDm() {
  const uid = addDm.value.selectedId
  if (!uid) return window.alert('请先选择一个用户')

  addDm.value.loading = true
  try {
    // 1) 幂等创建/获取 DM 会话
    await startDmApi(uid)

    // 2) 刷新联系人
    await loadContacts()

    // 3) 在联系人里找到刚选的用户；如没有则临时插入
    let peer = contacts.value.find(u => String(u.id) === String(uid))
    if (!peer) {
      const c = addDm.value.candidates.find(u => String(u.id) === String(uid))
      if (c) {
        peer = {
          id: c.id,
          name: c.name || c.username || `用户${c.id}`,
          role: '成员',
          online: false,
          avatar: c.avatar
        }
        if (!contacts.value.some(u => String(u.id) === String(peer.id))) {
          contacts.value.unshift(peer)
        }
      }
    }

    // 4) 进入会话
    if (peer) await openDM(peer)

    addDm.value.open = false
  } catch (e) {
    console.error('confirmAddDm error', e)
    window.alert('发起私信失败，请稍后重试')
  } finally {
    addDm.value.loading = false
  }
}

const invite = ref({
  open: false,
  loading: false,
  kw: '',
  candidates: [],     // 搜到的候选用户（含 username）
  selected: []        // ✅ 用数组而非 Set，避免非深度可追踪导致读取为空
})

// 打开邀请弹窗
function openInvite() {
  if (!currentGroup.value?.id) return
  invite.value.open = true
  invite.value.kw = ''
  invite.value.selected = []
  invite.value.candidates = []
}

// 搜索用户（通过用户名）
async function searchUsers() {
  const kw = invite.value.kw.trim()
  if (!kw) return
  invite.value.loading = true
  try {
    const res = await searchUsersApi(kw)
    const all = Array.isArray(res?.data) ? res.data : []

    // 统一候选字段，确保有 username 可选
    const normalized = all.map(u => ({
      id: u.id,
      username: u.username ?? u.name ?? '',   // ✅ 兜底，尽量提供 username
      name: u.name ?? u.username ?? '',
      avatar: u.avatar || u.avatarUrl || `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(u.name || u.username || 'U')}`
    })).filter(u => !!u.username)

    const inGroupNames = new Set((groupMembers.value || []).map(x => x.name)) // 群内展示名
    const meName = me.value.name

    // 过滤：不在群、不是自己
    invite.value.candidates = normalized.filter(
      u => !inGroupNames.has(u.username) && u.username !== meName
    )
  } catch (e) {
    console.error('搜索失败', e)
  } finally {
    invite.value.loading = false
  }
}

function toggleSelect(username) {
  const arr = invite.value.selected
  const i = arr.indexOf(username)
  if (i >= 0) arr.splice(i, 1)
  else arr.push(username)
}

async function doInvite() {
  const names = invite.value.selected.slice()
  if (!names.length) return window.alert('请选择要邀请的用户')

  invite.value.loading = true
  try {
    await inviteMembersApi(currentGroup.value.id, names)
    await loadGroupMembers(currentGroup.value.id)
    invite.value.open = false
  } catch (e) {
    console.error('邀请失败', e)
    window.alert('邀请失败，请稍后重试')
  } finally {
    invite.value.loading = false
  }
}

/* ========== 当前用户 ========== */
const me = computed(() => ({
  id: userStore.userId,
  name: userStore.userName,
  avatar: `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(userStore.userName || 'U')}`
}))

/* ========== 模式切换 ========== */
const mode = ref('group') // 'group' | 'dm'

/* ================== 群聊区 ================== */
const groups = ref([])
const groupQuery = ref('')
const filteredGroups = computed(() => {
  const kw = groupQuery.value.trim()
  return kw ? groups.value.filter(g => (g.name).includes(kw)) : groups.value
})
const currentGroup = ref(null)

const groupMembers = ref([])          // 当前群成员
const groupMessageStore = ref({})     // { [groupId]: Message[] }
const groupLastMsgId = ref({})        // { [groupId]: number } 用于增量拉取

const groupMessages = computed(() => groupMessageStore.value[currentGroup.value?.id] || [])

/* ================== 私聊区 ================== */
const contacts = ref([])
const dmQuery = ref('')
const filteredContacts = computed(() => {
  const kw = dmQuery.value.trim()
  return kw ? contacts.value.filter(u => (u.name + (u.role || '')).includes(kw)) : contacts.value
})
const currentDM = ref(null)

const dmMessageStore = ref({})        // { [peerUserId]: Message[] }
const dmLastMsgId = ref({})           // { [peerUserId]: number }

const dmMessages = computed(() => dmMessageStore.value[currentDM.value?.id] || [])

/* ================== 输入/AI/滚动/轮询 ================== */
const text = ref('')
const typing = ref(false)
const msgListEl = ref(null)
const ai = ref({ open: false, loading: false, title: '', html: '' })

let pullTimer = null // 轮询定时器

/* ================== 生命周期 ================== */
onMounted(async () => {
  await Promise.all([loadGroups(), loadContacts()])
  setupPulling()
  scrollToBottom()
})

onBeforeUnmount(() => {
  if (pullTimer) clearInterval(pullTimer)
})

/* ================== 加载数据（API） ================== */
async function loadGroups() {
  const res = await listGroupsApi()
  groups.value = normalizeGroups(res?.data || [])
  if (!currentGroup.value && groups.value.length) {
    currentGroup.value = groups.value[0]
    await Promise.all([
      loadGroupMessages(currentGroup.value.id),
      loadGroupMembers(currentGroup.value.id)
    ])
    sendReadAck({ type: 'group', groupId: currentGroup.value.id })
  }
}

async function loadGroupMembers(groupId) {
  const res = await groupMembersApi(groupId)
  groupMembers.value = normalizeUsers(res?.data || [])
}

async function loadGroupMessages(groupId, { sinceId } = {}) {
  const res = await groupMessagesApi(groupId, sinceId ? { sinceId } : {})
  const list = normalizeMessages(res?.data || [], me.value.id)
  if (!groupMessageStore.value[groupId]) groupMessageStore.value[groupId] = []
  groupMessageStore.value[groupId] = sinceId
    ? [...groupMessageStore.value[groupId], ...list]
    : list
  groupLastMsgId.value[groupId] = getMaxId(groupMessageStore.value[groupId])
}

async function loadContacts() {
  const res = await listContactsApi()
  contacts.value = normalizeUsers(res.data || [])
  if (!currentDM.value && contacts.value.length) {
    currentDM.value = contacts.value[0]
    await loadDMMessages(currentDM.value.id)
    sendReadAck({ type: 'dm', peerUserId: currentDM.value.id })
  }
}

async function loadDMMessages(peerUserId, { sinceId } = {}) {
  const res = await dmMessagesApi(peerUserId, sinceId ? { sinceId } : {})
  const list = normalizeMessages(res?.data || [], me.value.id)
  if (!dmMessageStore.value[peerUserId]) dmMessageStore.value[peerUserId] = []
  dmMessageStore.value[peerUserId] = sinceId
    ? [...dmMessageStore.value[peerUserId], ...list]
    : list
  dmLastMsgId.value[peerUserId] = getMaxId(dmMessageStore.value[peerUserId])
}

/* ================== 交互 ================== */
async function enterGroup(g) {
  if (!g || currentGroup.value?.id === g.id) return
  currentGroup.value = g
  mode.value = 'group'
  await Promise.all([loadGroupMessages(g.id), loadGroupMembers(g.id)])
  sendReadAck({ type: 'group', groupId: g.id })
  scrollToBottom()
}

async function openDM(u) {
  if (!u) return
  try { await startDmApi(u.id) } catch (_) { }
  currentDM.value = u
  mode.value = 'dm'
  await loadDMMessages(u.id)
  sendReadAck({ type: 'dm', peerUserId: u.id })
  scrollToBottom()
}

/** —— 统一的 tab 切换：只在需要时拉数据 —— **/
async function switchToDM() {
  mode.value = 'dm'
  if (!contacts.value.length) await loadContacts()
  if (!currentDM.value && contacts.value.length) await openDM(contacts.value[0])
}
async function switchToGroup() {
  mode.value = 'group'
  if (!groups.value.length) await loadGroups()
  if (!currentGroup.value && groups.value.length) await enterGroup(groups.value[0])
}

// 新建群（插入）
async function createGroup () {
  const name = window.prompt('请输入群名称：')?.trim()
  if (!name) return

  try {
    const res = await createGroupApi(name)
    const gid = res?.data?.id
    // 只刷新一次列表，避免重复/脏数据
    await loadGroups()

    if (gid) {
      const fresh = groups.value.find(x => x.id === gid)
      if (fresh) {
        await enterGroup(fresh)
      }
    }
  } catch (e) {
    console.error('createGroup error', e)
    window.alert('新建群失败，请稍后重试')
  }
}

/* ================== 发送消息（插入） ================== */
async function send() {
  const content = text.value.trim()
  if (!content) return
  text.value = '' // ✅ 清空输入框先

  try {
    if (mode.value === 'group') {
      if (!currentGroup.value) return
      const gid = currentGroup.value.id

      await sendMsgApi({
        type: 'group',
        groupId: gid,
        senderId: me.value.id,
        kind: 'text',
        content
      })

      await loadGroupMessages(gid, { sinceId: groupLastMsgId.value[gid] || 0 })
      sendReadAck({ type: 'group', groupId: gid })
      scrollToBottom()

    } else {
      if (!currentDM.value) return
      const pid = currentDM.value.id

      await sendMsgApi({
        type: 'dm',
        toUserId: pid,
        senderId: me.value.id,
        kind: 'text',
        content
      })

      await loadDMMessages(pid, { sinceId: dmLastMsgId.value[pid] || 0 })
      sendReadAck({ type: 'dm', peerUserId: pid })
      scrollToBottom()
    }

  } catch (e) {
    console.error('send error', e)
  }
}

/* ================== 轻量轮询增量拉新 ================== */
function setupPulling() {
  if (pullTimer) clearInterval(pullTimer)
  pullTimer = setInterval(async () => {
    try {
      if (mode.value === 'group' && currentGroup.value?.id) {
        const gid = currentGroup.value.id
        await loadGroupMessages(gid, { sinceId: groupLastMsgId.value[gid] || 0 })
      } else if (mode.value === 'dm' && currentDM.value?.id) {
        const pid = currentDM.value.id
        await loadDMMessages(pid, { sinceId: dmLastMsgId.value[pid] || 0 })
      }
    } catch (e) {
      // 静默
    }
  }, 300000)
}

/** —— 关键修复：watch 仅重建轮询，不再重复拉接口 —— **/
watch(mode, () => {
  setupPulling()
})

/* ================== 已读回执（可选） ================== */
async function sendReadAck(payload) {
  try {
    if (payload.type === 'group' && currentGroup.value?.id) {
      const list = groupMessageStore.value[currentGroup.value.id] || []
      payload.lastReadMsgId = getMaxId(list)
    } else if (payload.type === 'dm' && currentDM.value?.id) {
      const list = dmMessageStore.value[currentDM.value.id] || []
      payload.lastReadMsgId = getMaxId(list)
    }
    await readAckApi(payload)
  } catch (_) { }
}

/* ================== AI（占位） ================== */
function aiSummary() {
  ai.value = { open: true, loading: true, title: 'AI 总结', html: '' }
  setTimeout(() => {
    ai.value.loading = false
    ai.value.html = `
      <p><strong>${mode.value === 'group' ? '群聊' : '私聊'}要点：</strong></p>
      <ol>
        <li>对象：${mode.value === 'group' ? currentGroup.value?.name : currentDM.value?.name}</li>
        <li>你可以在后端实现 /chat/ai/summary 接口联动。</li>
      </ol>`
  }, 600)
}

/* ================== 工具 ================== */
function scrollToBottom() {
  nextTick(() => {
    const el = msgListEl.value
    if (el) el.scrollTop = el.scrollHeight
  })
}
function escapeHtml(s) {
  return s.replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]))
}
function getMaxId(list) {
  return list.reduce((max, it) => Math.max(max, Number(it.id || 0)), 0)
}

/* ======= 规范化 ======= */
function normalizeGroups(arr) { return arr.map(normalizeGroup).filter(Boolean) }
function normalizeGroup(g) {
  if (!g) return null
  return {
    id: g.id,
    name: g.name || g.groupName || '未命名群',
    topic: g.topic || '',
    members: g.members ?? g.memberCount ?? 0,
    unread: g.unread ?? 0
  }
}
function normalizeUsers(arr) {
  return arr.map(u => ({
    id: u.id,
    name: u.name || u.username || `用户${u.id}`,
    role: u.role || '成员',
    online: !!u.online,
    avatar: u.avatar || u.avatarUrl || `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(u.name || u.username || 'U')}`
  }))
}
function normalizeMessages(arr, myId) {
  return arr.map(m => {
    const timeStr = fmtTime(m.createTime || m.create_time || m.time)
    return {
      id: m.id,
      user: m.senderName || m.user || m.username || (m.senderId ? `用户${m.senderId}` : '系统'),
      time: timeStr,
      avatar: m.avatar || m.senderAvatar || null,
      content: escapeHtml(String(m.content || '')).replace(/\n/g, '<br/>'),
      mine: m.senderId ? (m.senderId === myId) : !!m.mine
    }
  })
}
function fmtTime(t) {
  if (!t) return ''
  try {
    const d = typeof t === 'string' && t.includes('T') ? new Date(t) : new Date(String(t).replace(/-/g, '/'))
    const hh = String(d.getHours()).padStart(2, '0')
    const mm = String(d.getMinutes()).padStart(2, '0')
    return `${hh}:${mm}`
  } catch { return '' }
}
</script>

<template>
  <div class="chat-root">
    <!-- 发起私信 弹层 -->
    <div v-if="addDm.open" class="modal" @click.self="addDm.open = false">
      <div class="modal-panel">
        <header class="modal-hd">
          <h4>发起私信</h4>
        </header>
        <div class="modal-bd">
          <div style="display:flex; gap:8px; margin-bottom:10px">
            <input v-model="addDm.kw" placeholder="输入用户名或昵称…"
              style="flex:1; height:32px; border:1px solid #ccc; border-radius:8px; padding:0 10px;"
              @keyup.enter="searchDmCandidates" />
            <button class="ghost" @click="searchDmCandidates" :disabled="addDm.loading">搜索</button>
          </div>

          <div v-if="addDm.loading" class="muted">加载中…</div>

          <ul v-else class="contact-list" style="max-height:40vh; overflow:auto">
            <li v-for="u in addDm.candidates" :key="u.id" class="contact" @click="chooseDmTarget(u.id)"
              :style="{ background: String(addDm.selectedId) === String(u.id) ? '#f5f7ff' : '' }">
              <img :src="u.avatar" class="avatar" />
              <div class="c">
                <div class="name ellipsis">{{ u.name }}</div>
                <div class="muted small">@{{ u.username || '—' }}</div>
              </div>
              <input type="radio" name="dmTarget" :checked="String(addDm.selectedId) === String(u.id)"
                @change="chooseDmTarget(u.id)" style="margin-left:auto" />
            </li>
            <li v-if="!addDm.candidates.length" class="muted small" style="padding:8px 0">
              暂无匹配的用户
            </li>
          </ul>
        </div>
        <footer class="modal-ft">
          <button class="ghost" @click="addDm.open = false">取消</button>
          <button class="primary" :disabled="addDm.loading || !addDm.selectedId" @click="confirmAddDm">
            开始私信
          </button>
        </footer>
      </div>
    </div>

    <!-- 邀请弹层 -->
    <div v-if="invite.open" class="modal" @click.self="invite.open = false">
      <div class="modal-panel">
        <header class="modal-hd">
          <h4>邀请成员到群：{{ currentGroup?.name }}</h4>
        </header>
        <div class="modal-bd">
          <div style="display:flex; gap:8px; margin-bottom:10px">
            <input v-model="invite.kw" placeholder="输入用户名搜索…"
              style="flex:1; height:32px; border:1px solid #ccc; border-radius:8px; padding:0 10px;"
              @keyup.enter="searchUsers" />
            <button class="ghost" @click="searchUsers" :disabled="invite.loading">搜索</button>
          </div>

          <div v-if="invite.loading" class="muted">加载中…</div>

          <ul v-else class="contact-list" style="max-height:40vh; overflow:auto">
            <li v-for="u in invite.candidates" :key="u.username" class="contact">
              <img :src="u.avatar" class="avatar" />
              <div class="c">
                <div class="name ellipsis">{{ u.username }}</div>
                <div class="muted small">昵称：{{ u.name }}</div>
              </div>
              <label style="margin-left:auto; display:flex; align-items:center; gap:6px; cursor:pointer">
                <input type="checkbox" :checked="invite.selected.includes(u.username)"
                  @change="toggleSelect(u.username)" />
                选择
              </label>
            </li>
            <li v-if="!invite.candidates.length" class="muted small" style="padding:8px 0">
              暂无匹配的用户
            </li>
          </ul>
        </div>
        <footer class="modal-ft">
          <button class="ghost" @click="invite.open = false">取消</button>
          <button class="primary" :disabled="invite.loading || !invite.selected.length" @click="doInvite">邀请</button>
        </footer>
      </div>
    </div>

    <div class="chat-page">
      <!-- 左：侧栏 -->
      <aside class="sidebar card">
        <header class="side-hd">
          <h3>消息</h3>
          <div class="tabs">
            <button :class="['tab', mode === 'dm' && 'active']" @click="switchToDM">私聊</button>
            <button :class="['tab', mode === 'group' && 'active']" @click="switchToGroup">群组</button>
          </div>
        </header>

        <!-- 群组列表 -->
        <template v-if="mode === 'group'">
          <div class="side-search">
            <input v-model="groupQuery" placeholder="搜索群组…" />
          </div>
          <ul class="room-list">
            <li v-for="g in filteredGroups" :key="g.id" :class="['room', currentGroup?.id === g.id && 'active']"
              @click="enterGroup(g)">
              <div class="title ellipsis">{{ g.name }}</div>
              <div class="meta">
                <span class="muted">{{ g.members }} 人</span>
                <span class="dot">·</span>
                <span class="muted">{{ g.unread }} 未读</span>
              </div>
            </li>
          </ul>
          <button class="ghost small" @click="createGroup">新建</button>

        </template>

        <!-- 私聊联系人列表 -->
        <template v-else>
          <div class="side-search">
            <input v-model="dmQuery" placeholder="搜索联系人…" />
          </div>
          <ul class="contact-list">
            <li v-for="u in filteredContacts" :key="u.id" :class="['contact', currentDM?.id === u.id && 'active']"
              @click="openDM(u)">
              <img :src="u.avatar" class="avatar" alt />
              <div class="c">
                <div class="name ellipsis">{{ u.name }}</div>
                <div class="muted small">{{ u.role || '成员' }}</div>
              </div>
              <span class="status" :class="u.online ? 'on' : 'off'"></span>
            </li>
          </ul>
          <button class="ghost small" @click="openAddDm">添加新用户</button>
          <div v-if="!filteredContacts.length" class="muted small" style="padding:12px">
            暂无联系人。请先与他人建立私信会话，或改造为“从全量用户发起私聊”。
          </div>
        </template>
      </aside>

      <!-- 中：消息区 -->
      <section class="main card">
        <header class="main-hd">
          <div>
            <h3 class="room-name" v-if="mode === 'group'">{{ currentGroup?.name || '未选择群组' }}</h3>
            <h3 class="room-name" v-else>
              <span>{{ currentDM?.name || '未选择联系人' }}</span>
              <span class="badge">私聊</span>
            </h3>
            <div class="muted small" v-if="mode === 'group'">主题：{{ currentGroup?.topic || '自由讨论' }}</div>
            <div class="muted small" v-else>
              对方状态：
              <span :class="['status', currentDM?.online ? 'on' : 'off']"></span>
              {{ currentDM?.online ? '在线' : '离线' }}
            </div>
          </div>
          <div class="tools">
            <button class="ghost" @click="aiSummary">AI总结</button>
          </div>
        </header>

        <div class="msg-list" ref="msgListEl">
          <template v-if="mode === 'group'">
            <div v-for="m in groupMessages" :key="m.id" :class="['msg', m.mine && 'mine']">
              <img v-if="m.avatar" class="avatar" :src="m.avatar" alt="avatar" />
              <div class="bubble">
                <div class="line">
                  <span class="name" :class="{ me: m.mine }">{{ m.user }}</span>
                  <span class="time muted">{{ m.time }}</span>
                </div>
                <div class="content" v-html="m.content"></div>
              </div>
            </div>
          </template>

          <template v-else>
            <div v-for="m in dmMessages" :key="m.id" :class="['msg', m.mine && 'mine']">
              <img v-if="m.avatar" class="avatar" :src="m.avatar" alt="avatar" />
              <div class="bubble">
                <div class="line">
                  <span class="name" :class="{ me: m.mine }">{{ m.user }}</span>
                  <span class="time muted">{{ m.time }}</span>
                </div>
                <div class="content" v-html="m.content"></div>
              </div>
            </div>
          </template>

          <div v-if="typing" class="typing muted">对方正在输入…</div>
        </div>

        <footer class="composer">
          <textarea v-model="text" rows="3" maxlength="1000"
            :placeholder="mode === 'group' ? '在群里发言，支持上传文件/代码片段…' : '发送私信…'" @keydown.enter.exact.prevent="send" />
          <div class="bar">
            <div class="left">
              <button class="icon" title="附件">📎</button>
            </div>
            <div class="right">
              <span class="muted">{{ text.length }}/1000</span>
              <button class="primary" :disabled="!text.trim()" @click="send">发送</button>
            </div>
          </div>
        </footer>
      </section>

      <!-- 右：信息栏 -->
      <aside class="member card">
        <header class="side-hd">
          <template v-if="mode === 'group'">
            <h3>成员 ({{ groupMembers.length }})</h3>
            <button class="ghost small" @click="openInvite">邀请</button>
            <button class="ghost small" @click="renameCurrentGroup">改名</button>
            <button class="ghost small" @click="dissolveCurrentGroup">解散</button>
          </template>
          <template v-else>
            <h3>资料</h3>
            <button class="ghost" @click="deleteCurrentDM">删除私聊</button>
          </template>
        </header>

        <template v-if="mode === 'group'">
          <ul class="member-list">
            <li v-for="u in groupMembers" :key="u.id" class="member-item">
              <img :src="u.avatar" class="avatar" alt />
              <div class="u">
                <div class="name ellipsis">{{ u.name }}</div>
                <div class="role muted small">{{ u.role || '成员' }}</div>
              </div>
              <span class="status" :class="u.online ? 'on' : 'off'"></span>
            </li>
          </ul>
        </template>

        <template v-else>
          <div class="dm-card" v-if="currentDM">
            <img :src="currentDM.avatar" class="avatar-lg" alt />
            <div class="dm-name">{{ currentDM.name }}</div>
            <div class="dm-role muted small">{{ currentDM.role || '成员' }}</div>
            <div class="dm-status">
              <span class="status" :class="currentDM.online ? 'on' : 'off'"></span>
              {{ currentDM?.online ? '在线' : '离线' }}
            </div>
          </div>
          <div class="muted small" v-else style="padding:12px">暂无联系人，或尚未选择联系人。</div>
        </template>
      </aside>
    </div>

    <!-- AI 弹层 -->
    <div v-if="ai.open" class="modal" @click.self="ai.open = false">
      <div class="modal-panel">
        <header class="modal-hd">
          <h4>{{ ai.title }}</h4>
        </header>
        <div class="modal-bd">
          <div v-if="ai.loading" class="muted">AI 正在生成……</div>
          <div v-else v-html="ai.html" class="ai-text"></div>
        </div>
        <footer class="modal-ft">
          <button class="ghost" @click="ai.open = false">关闭</button>
        </footer>
      </div>
    </div>
  </div>
</template>


<style scoped>
/* 同你原样式，未改动 */
.chat-page {
  display: grid;
  grid-template-columns: 260px 1fr 260px;
  gap: 12px;
  padding: 12px 0 32px;
}

.card {
  background: #fff;
  border: 1px solid #eef0f3;
  border-radius: 10px;
  overflow: hidden;
}

.muted {
  color: #7a7a7a;

}

.small {
  font-size: 12px;
}

.dot {
  color: #c9c9c9;
}

.sidebar {
  display: flex;
  flex-direction: column;
  min-height: 70vh;
}

.side-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid #f0f2f5;
}

.tabs {
  display: flex;
  gap: 8px;
}

.tab {
  height: 28px;
  padding: 0 10px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #fff;
  cursor: pointer;
}

.tab.active {
  background: #eaf2ff;
  border-color: #d6e6ff;
}

.side-search {
  padding: 10px 12px;
  width: 85%;
}

.side-search input {
  width: 100%;
  height: 32px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 0 10px;
}

.room-list {
  list-style: none;
  margin: 0;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.room {
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
}

.room:hover {
  background: #f7f9fb;
}

.room.active {
  background: #eaf2ff;
}

.room .title {
  font-weight: 600;
}

.room .meta {
  font-size: 12px;
}

.contact-list {
  list-style: none;
  margin: 0;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.contact {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 8px;
  cursor: pointer;
}

.contact:hover {
  background: #f7f9fb;
}

.contact.active {
  background: #eaf2ff;
}

.contact .avatar {
  width: 28px;
  height: 28px;
  border-radius: 8px;
}

.contact .c .name {
  font-weight: 600;
}

.side-ft {
  padding: 8px 12px;
  border-top: 1px solid #f0f2f5;
}

.main {
  display: flex;
  flex-direction: column;
  min-height: 70vh;
  height: 60%;
}

.main-hd {
  padding: 10px 12px;
  border-bottom: 1px solid #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.tools {
  display: flex;
  gap: 8px;
}

.msg-list {
  flex: 1;
  padding: 12px;
  overflow: auto;
  background: #fcfdff;
}

.msg {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  max-width: 80%;
}

.msg.mine {
  margin-left: auto;
  flex-direction: row-reverse;
}

.msg .avatar {
  width: 28px;
  height: 28px;
  border-radius: 8px;
}

.bubble {
  background: #fff;
  border: 1px solid #eef0f3;
  border-radius: 10px;
  padding: 8px 10px;
}

.msg.mine .bubble {
  background: #eaf2ff;
  border-color: #d6e6ff;
}

.line {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 4px;
}

.name {
  font-weight: 600;
}

.name.me {
  color: #1e80ff;
}

.content :deep(code) {
  background: #f5f5f5;
  padding: 0 4px;
  border-radius: 4px;
}

.typing {
  text-align: center;
  margin-top: 6px;
}

.badge {
  margin-left: 8px;
  padding: 2px 6px;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  font-size: 12px;
}

.composer {
  border-top: 1px solid #f0f2f5;
  padding: 8px;
  display: flex;
  width: 95%;

  flex-direction: column;
  gap: 8px;
}

.composer textarea {
  width: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px;
  resize: vertical;
}

.bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.left {
  display: flex;
  gap: 6px;
}

.icon {
  border: none;
  background: #fff;
  cursor: pointer;
  font-size: 18px;
}

.primary,
.ghost {
  height: 32px;
  padding: 0 12px;
  border-radius: 8px;
  margin: 0px 2px;
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

.member {
  min-height: 70vh;
}

.member-list {
  list-style: none;
  margin: 0;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 8px;
}

.member-item:hover {
  background: #f7f9fb;
}

.member .avatar {
  width: 28px;
  height: 28px;
  border-radius: 8px;
}

.u .name {
  font-weight: 600;
}

.status {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-left: auto;
}

.status.on {
  background: #16a34a;
}

.status.off {
  background: #cbd5e1;
}

.dm-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
}

.avatar-lg {
  width: 64px;
  height: 64px;
  border-radius: 20px;
}

.dm-name {
  font-weight: 700;
}

.modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, .35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal-panel {
  width: min(720px, 96vw);
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-hd,
.modal-ft {
  padding: 10px 12px;
  border-bottom: 1px solid #f0f2f5;
}

.modal-ft {
  border-bottom: none;
  border-top: 1px solid #f0f2f5;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.modal-bd {
  padding: 12px;
  max-height: 60vh;
  overflow: auto;
}

.ai-text table {
  width: 100%;
  border-collapse: collapse;
}

.ai-text th,
.ai-text td {
  border: 1px solid #eee;
  padding: 6px;
}

@media (max-width:1024px) {
  .chat-page {
    grid-template-columns: 220px 1fr;
  }

  .member {
    display: none;
  }
}

@media (max-width:720px) {
  .chat-page {
    grid-template-columns: 1fr;
  }

  .sidebar {
    display: none;
  }
}
</style>