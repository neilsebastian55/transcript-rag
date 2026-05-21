const BASE = '/api'

async function req(path, options = {}) {
  const res = await fetch(BASE + path, options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  health: () => req('/health'),

  uploadFile: (file) => {
    const form = new FormData()
    form.append('file', file)
    return req('/transcripts/upload', { method: 'POST', body: form })
  },

  loadYoutube: (url) =>
    req('/transcripts/youtube', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    }),

  loadText: (text, source) =>
    req('/transcripts/text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, source }),
    }),

  query: (question, collectionId, history = [], topK = 3) =>
    req('/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        collection_id: collectionId,
        top_k: topK,
        history,
      }),
    }),

  feedback: (queryId, rating, collectionId) =>
    req('/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query_id: queryId, rating, collection_id: collectionId }),
    }),

  listCollections: () => req('/collections'),

  deleteCollection: (id) => req(`/collections/${id}`, { method: 'DELETE' }),
}
