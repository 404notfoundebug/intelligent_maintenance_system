import request from './request'

export function getKnowledgeFiles(params) {
  return request.get('/api/knowledge/files', { params })
}

export function getKnowledgeFileDetail(id) {
  return request.get(`/api/knowledge/files/${id}`)
}

export function getKnowledgeChunks(id, params) {
  return request.get(`/api/knowledge/files/${id}/chunks`, { params })
}

export function uploadKnowledgeFile(formData) {
  return request.post('/api/knowledge/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function deleteKnowledgeFile(id) {
  return request.delete(`/api/knowledge/files/${id}`)
}

export function searchKnowledge(data) {
  return request.post('/api/search', data)
}
