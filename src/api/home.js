import request from '@/utils/request'

/**
 * 首页API封装
 */

// 获取首页信息流
export function getFeedList(params) {
  return request({
    url: '/api/feed/list',
    method: 'get',
    params
  })
}

// 获取用户关注的话题
export function getUserFollows(userId) {
  return request({
    url: '/api/feed/follow',
    method: 'get',
    params: { userId }
  })
}

// 创建新帖子
export function createPost(data) {
  return request({
    url: '/api/feed/post',
    method: 'post',
    data
  })
}

// 创建新话题
export function createTopic(data) {
  return request({
    url: '/api/feed/topic',
    method: 'post',
    data
  })
}

// 获取帖子详情
export function getPostDetail(id) {
  return request({
    url: `/api/feed/post/${id}`,
    method: 'get'
  })
}

// 获取话题详情
export function getTopicDetail(id) {
  return request({
    url: `/api/feed/topic/${id}`,
    method: 'get'
  })
}

// 更新帖子
export function updatePost(id, data) {
  return request({
    url: `/api/feed/post/${id}`,
    method: 'put',
    data
  })
}

// 删除帖子
export function deletePost(id) {
  return request({
    url: `/api/feed/post/${id}`,
    method: 'delete'
  })
}

// 更新话题
export function updateTopic(id, data) {
  return request({
    url: `/api/feed/topic/${id}`,
    method: 'put',
    data
  })
}

// 删除话题
export function deleteTopic(id) {
  return request({
    url: `/api/feed/topic/${id}`,
    method: 'delete'
  })
}

// 点赞/取消点赞
export function updateLike(data) {
  return request({
    url: '/api/interaction/like',
    method: 'post',
    data
  })
}

// 收藏/取消收藏
export function updateCollect(data) {
  return request({
    url: '/api/interaction/collect',
    method: 'post',
    data
  })
}

// 更新关注状态 (新增函数)
export function updateFollow(data) {
  return request({
    url: '/api/interaction/follow',
    method: 'post',
    data
  })
}

// 发表评论
export function addComment(data) {
  return request({
    url: '/api/interaction/comment',
    method: 'post',
    data
  })
}

// 获取评论列表
export function getComments(entityType, entityId) {
  return request({
    url: `/api/interaction/comment/${entityType}/${entityId}`,
    method: 'get'
  })
}

// 删除评论
export function deleteComment(id) {
  return request({
    url: `/api/interaction/comment/${id}`,
    method: 'delete'
  })
}

// 获取用户信息
export function getUserInfo() {
  return request({
    url: '/api/user/info',
    method: 'get'
  })
}

// 获取用户发布的帖子
export function getUserPosts(userId) {
  return request({
    url: '/api/user/posts',
    method: 'get',
    params: { userId }
  })
}

// 获取用户创建的话题
export function getUserTopics(userId) {
  return request({
    url: '/api/user/topics',
    method: 'get',
    params: { userId }
  }) 
}
