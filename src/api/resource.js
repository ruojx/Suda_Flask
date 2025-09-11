import request from "@/utils/request";

export const listApi = (data) => request.post('/resource/list', data)

export const previewApi = (id) => request.post(`/resource/preview/${id}`)

export const downloadApi = (id) => request.post(`/resource/download/${id}`)

export const likeApi = (id) => request.post(`/resource/like/${id}`)

export const unlikeApi = (id) => request.post(`/resource/unlike/${id}`)

export const favoriteApi = (id) => request.post(`/resource/favorite/${id}`)

export const unfavoriteApi = (id) => request.post(`/resource/unfavorite/${id}`)

export const aiSummaryApi = (data) => request.post('/resource/ai/summary', data)

export const aiPlanApi = (data) => request.post('/resource/ai/plan', data)

export const createFileApi = (formData) => request.post('/resource/createFile', formData)

export const createLinkApi = (data) => request.post('/resource/createLink', data)

export const tagListApi = (data) => request.post('/resource/tags', data)