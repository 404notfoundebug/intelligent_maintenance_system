import { getToken } from '../utils/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export function buildFileViewUrl(path) {
  return `${API_BASE_URL}/api/files/view?path=${encodeURIComponent(path)}`
}

export async function fetchFileBlob(path) {
  const token = getToken()
  const response = await fetch(buildFileViewUrl(path), {
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  })

  if (!response.ok) {
    let message = '文件预览失败'
    try {
      const data = await response.json()
      message = data?.message || data?.detail || message
    } catch (error) {
      message = response.statusText || message
    }
    throw new Error(message)
  }

  return response.blob()
}
