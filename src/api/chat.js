// src/api/chat.js
import request from '@/utils/request'

// ===== 群聊 =====
export const listGroupsApi = () => request.get('/chat/groups') // 列出我加入的群
export const groupMembersApi = (groupId) => request.get(`/chat/group/${groupId}/members`)
export const groupMessagesApi = (groupId, params = {}) =>
  request.get(`/chat/group/${groupId}/messages`, { params })      // 支持 { sinceId, limit }

// 新建群（插入）
export const createGroupApi = (groupName) => request.post(`/chat/group/${groupName}`);
// ===== 私聊 =====
export const listContactsApi = () => request.get('/chat/contacts')         // 联系人列表（可含最近会话）
export const dmMessagesApi = (peerUserId, params = {}) =>
  request.get(`/chat/dm/${peerUserId}/messages`, { params })                // { sinceId, limit }

// 修改群名
export function renameGroupApi(groupId, name) {
  return request.put(`/chat/group/${groupId}/${name}`)
}

// 解散群聊
export function dissolveGroupApi(groupId) {
  return request.delete(`/chat/group/${groupId}`)
}

// 删除私聊（退出 DM）
export function deleteDmApi(peerUserId) {
  return request.delete(`/chat/dm/${peerUserId}`)
}

// ===== 群成员管理 =====
// 搜索用户（通过用户名模糊搜索）
export function searchUsersApi(kw) {
  return request.get('/chat/search', { params: { kw } })
}

// 邀请成员（按用户名）
export function inviteMembersApi(groupId, userNames) {
  return request.post(`/chat/group/${groupId}/invite`, { userNames })
}

// 可选：发起私聊（确保有会话）——如果后端已有自动建会话可不调
export const startDmApi = (peerUserId) => request.post('/chat/dm/start', { peerUserId })

// ===== 发送消息（插入） =====
export const sendMsgApi = (data) => request.post('/chat/send', data)
// data: { type:'group'|'dm', groupId? , toUserId? , kind:'text'|'image'|'file'|'system', content, fileUrl?, fileName?, fileSize? }

// ===== 已读回执（可选） =====
export const readAckApi = (data) => request.post('/chat/read', data)
// data: { type:'group'|'dm', groupId? , peerUserId?, lastReadMsgId }
