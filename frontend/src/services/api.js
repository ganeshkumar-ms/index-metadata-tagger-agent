import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || ''

export async function tagContent({ file, text, conversationHistory = [] }) {
  const formData = new FormData()
  if (file) {
    formData.append('file', file)
  }
  if (text) {
    formData.append('text', text)
  }
  formData.append('conversation_history', JSON.stringify(conversationHistory))

  const response = await axios.post(`${API_BASE}/api/tag`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  })

  return response.data
}

export function toViewerDoc(meta) {
  if (!meta) return null
  const abs = u => (u ? (u.startsWith('http') ? u : `${API_BASE}${u}`) : null)

  const viewUrl = abs(meta.view_url || meta.viewUrl)
  const downloadUrl = abs(meta.url || meta.downloadUrl)

  return {
    name: meta.filename || meta.name || 'Document',
    viewUrl: viewUrl,
    downloadUrl: downloadUrl,
    preview: meta.preview || '',
    rawMeta: meta
  }
}
