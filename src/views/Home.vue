<template>
  <div class="home">
    <!-- 顶部标签和排序选项 -->
    <section class="tabs-container">
      <div class="tabs">
        <button
          v-for="t in tabs"
          :key="t.key"
          :class="['tab', currentTab === t.key && 'active']"
          @click="switchTab(t.key)"
        >
          {{ t.label }}
        </button>
      </div>
      <div class="sort-container">
        <div class="composer-actions">
          <button class="action-btn" @click="createNewPost">发帖子</button>
          <button class="action-btn" @click="createNewTopic">发话题</button>
        </div>
        <div v-if="currentTab!='recommend' && currentTab!='follow'" class="sort-options">
          <select v-model="currentSort" @change="fetchFeed">
            <option value="time">按时间排序</option>
            <option value="hot">按热度排序</option>
          </select>
        </div>
      </div>
    </section>

    <!-- 内容区域 -->
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else>
      <!-- 列表 -->
      <article 
        v-for="item in feed" 
        :key="`${item.type}-${item.id}`" 
        class="feed-item card"
        :class="{'topic-item': item.type === 'topic', 'post-item': item.type === 'post'}"
      >
        <!-- 帖子/话题 -->
        <div class="item-header">
          <h3 class="title">{{ item.title }}</h3>
          <span class="item-type">{{ item.type === 'post' ? '帖子' : '话题' }}</span>
        </div>
        <p class="summary">{{ item.summary }}</p>
        
        <!-- 互动展示 -->
        <div class="actions">
          <span>👁️ {{ item.viewCount || 0 }}</span>
          <span @click="toggleLike(item)">👍 {{ item.likeCount || 0 }}</span>

          <span v-if="item.type === 'post'" @click="toggleCollect(item)">⭐ {{ item.collectCount || 0 }}</span>
          <span v-else>📝 {{ item.postCount || 0 }}</span>

          <!-- 关注/取消关注按钮 -->
          <span v-if="item.type === 'topic'" @click="toggleFollow(item)">
            👀 {{ item.followCount || 0  }} {{ currentTab === 'follow' ? '取消关注' : '' }} 
          </span>
          <span v-else>💬 {{ item.commentCount || 0 }}</span>
        </div>

        <!-- 创建者信息 -->
        <div class="item-footer">
          <span class="author">{{ item.authorName || '匿名' }}</span>
          <span class="publish-time">{{ formatTime(item.createTime) }}</span>
        </div>
      </article>

      <!-- 分页器 -->
      <div class="pagination-container">
        <div class="pagination">
          <button 
            :disabled="currentPage === 1" 
            @click="changePage(currentPage - 1)"
            class="pagination-btn"
          >
            上一页
          </button>
          
          <span class="page-info">
            第 {{ currentPage }} 页，共 {{ totalPages }} 页
          </span>
          
          <button 
            :disabled="currentPage === totalPages" 
            @click="changePage(currentPage + 1)"
            class="pagination-btn"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 创建帖子/话题的模态框 -->
    <div v-if="showCreateModal" class="modal">
      <div class="modal-content">
        <h3>{{ modalTitle }}</h3>
        <input v-model="newItem.title" :placeholder="`请输入${modalTitle}标题`">
        <textarea v-model="newItem.content" :placeholder="`请输入${modalTitle}内容`" rows="5"></textarea>
        <div class="modal-actions">
          <button class="submit-btn" @click="submitNewItem">提交</button>
          <button class="cancel-btn" @click="showCreateModal = false">取消</button>
        </div>
      </div>
    </div>

    <!-- 错误弹窗 -->
    <div v-if="showErrorModal" class="error-modal" @click="closeErrorModal">
      <div class="error-modal-content" @click.stop>
        <h3>错误提示</h3>
        <p>{{ errorMessage }}</p>
        <button class="confirm-btn" @click="closeErrorModal">确定</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { 
  getFeedList, getUserFollows, createPost, createTopic, 
  updateLike, updateCollect, updateFollow
} from '@/api/home'
import { useUserStore } from '@/stores/userStore'

const userStore = useUserStore()

// 获取当前用户ID
const userId = userStore.userId

// 顶部标签
const tabs = [
  { key: 'follow', label: '关注' },
  { key: 'recommend', label: '推荐' },
  { key: 'post', label: '帖子' },
  { key: 'topic', label: '话题' }
]

const currentTab = ref('post')
const currentSort = ref('hot')

// 信息流数据
const feed = ref([])
const page = ref(1)
const pageSize = ref(5)
const loading = ref(true)
const totalPages = ref(1)
const currentPage = ref(1)

// 创建模态框
const showCreateModal = ref(false)
const modalTitle = ref('')
const newItem = reactive({
  type: '',
  title: '',
  content: ''
})

// 错误弹窗
const showErrorModal = ref(false)
const errorMessage = ref('')

onMounted(() => {
  fetchFeed()
})

// 切换标签
function switchTab(key) {
  currentTab.value = key
  page.value = 1
  currentPage.value = 1
  feed.value = []
  fetchFeed()
}

// 获取内容列表
async function fetchFeed() {
  loading.value = true
  try {
    let response
    if (currentTab.value === 'follow') {
        response = await getUserFollows(userId)// ⚠️ 这里的 userId 应该从登录态取
    } 
    else {
      response = await getFeedList({
        tab: currentTab.value,
        sort: currentSort.value,
        page: page.value,
        size: pageSize.value
      })
    }
    console.log('获取内容列表:', response)
    if (response.code === 1) {
      const data = response.data
      feed.value = data.list
      totalPages.value = data.pages
      currentPage.value = data.pageNum
    }
  } catch (error) {
    console.error('获取内容失败:', error)
  } finally {
    loading.value = false
  }
}

// 分页
function changePage(newPage) {
  if (newPage >= 1 && newPage <= totalPages.value) {
    page.value = newPage
    currentPage.value = newPage
    fetchFeed()
  }
}

// 格式化时间
function formatTime(time) {
  const now = new Date()
  const publishTime = new Date(time)
  const diff = now - publishTime
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今天发布'
  if (days === 1) return '昨天发布'
  if (days < 7) return `${days}天前发布`
  return publishTime.toLocaleDateString()
}

// 点赞
async function toggleLike(item) {
  try {
    const response = await updateLike({
      userId: userId,
      entityType: item.type === 'post' ? 1 : 2,
      entityId: item.id
    })
    console.log('点赞:', response)
    if (response.code === 1) {
      fetchFeed();
    }
  } catch (error) {
    errorMessage.value = '点赞失败: ' + error.message
    showErrorModal.value = true
  }
}

// 收藏
async function toggleCollect(item) {
  try {
    const response = await updateCollect({
      userId: userId,
      entityId: item.id
    })
    console.log('收藏:', response)
    if (response.code === 1) {
      // item.collectCount += response.data.collected ? 1 : -1;
      fetchFeed();
    }
  } catch (error) {
    errorMessage.value = '收藏失败: ' + error.message
    showErrorModal.value = true
  }
}

// 关注/取消关注
async function toggleFollow(item) {
  try {
    const response = await updateFollow({
      userId: userId,
      entityId: item.id
    })
    console.log('关注:', response);
    if (response.code === 1) {
      if (currentTab.value === 'follow') {
        // feed.value = feed.value.filter(f => f.id !== item.id);
        fetchFeed();
      }
    }
  } catch (error) {
    errorMessage.value = '关注失败: ' + error.message
    showErrorModal.value = true
  }
}

// 打开创建模态框
function openCreateModal(type) {
  modalTitle.value = type === 'post' ? '帖子' : '话题'
  newItem.type = type
  newItem.title = ''
  newItem.content = ''
  showCreateModal.value = true
}

// 提交新帖子/话题
async function submitNewItem() {
  if (!newItem.title.trim() || !newItem.content.trim()) return
  try {
    const api = newItem.type === 'post' ? createPost : createTopic
    const response = await api({
      title: newItem.title,
      content: newItem.content
    })
    if (response.code === 200) {
      showCreateModal.value = false
      fetchFeed()
    }
  } catch (error) {
    errorMessage.value = '创建失败: ' + error.message
    showErrorModal.value = true
  }
}

// 发布功能
const createNewPost = () => openCreateModal('post')
const createNewTopic = () => openCreateModal('topic')

// 关闭错误弹窗
function closeErrorModal() {
  showErrorModal.value = false
  errorMessage.value = ''
}
</script>

<style scoped>
.home {
  padding: 16px 0 40px;
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

.sort-container{
  display: flex;
}

.composer-actions {
  margin-right: 10px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* 美化按钮样式 */
.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: bold;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.tabs-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.tabs {
  display: flex;
  gap: 12px;
}

.tab {
  padding: 8px 16px;
  border: none;
  background: #f0f0f0;
  border-radius: 20px;
  cursor: pointer;
  color: #666;
  transition: all 0.3s ease;
}

.tab.active {
  background: #1e80ff;
  color: white;
  font-weight: bold;
}

.sort-options select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
}

.feed-item {
  position: relative;
}

.feed-item.topic-item {
  border-left: 4px solid #ffa116;
}

.feed-item.post-item {
  border-left: 4px solid #1e80ff;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.item-type {
  font-size: 12px;
  color: #8590a6;
  background: #f6f6f6;
  padding: 2px 6px;
  border-radius: 3px;
}

.title {
  margin: 0;
  font-size: 16px;
}

.summary {
  margin: 8px 0;
  color: #262626;
  line-height: 1.6;
}

.actions {
  display: flex;
  gap: 12px;
  font-size: 14px;
  color: #8590a6;
  margin-bottom: 8px;
}

.actions span {
  cursor: pointer;
}

.actions span:hover {
  color: #1e80ff;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #8590a6;
}

.author {
  font-weight: bold;
}

.comments-section {
  margin-top: 16px;
  border-top: 1px solid #eee;
  padding-top: 16px;
}

.comment-input {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.comment-input input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.comment {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment:last-child {
  border-bottom: none;
}

.comment-author {
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 4px;
}

.comment-content {
  font-size: 14px;
  margin-bottom: 4px;
}

.comment-time {
  font-size: 12px;
  color: #8590a6;
}

.load-more {
  text-align: center;
  margin-top: 16px;
}

.muted {
  color: #999;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #8590a6;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
}

.modal-content h3 {
  margin-top: 0;
}

.modal-content input,
.modal-content textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 16px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.submit-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background: #1e80ff;
  color: white;
  cursor: pointer;
}

.cancel-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #f0f0f0;
  cursor: pointer;
}

/* 分页器样式 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 15px;
}

.pagination-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #1e80ff;
  color: white;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}

/* 错误弹窗样式 */
.error-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.error-modal-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
  text-align: center;
}

.error-modal-content h3 {
  margin-top: 0;
  color: #e74c3c;
}

.confirm-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background: #e74c3c;
  color: white;
  cursor: pointer;
  margin-top: 15px;
}
</style>