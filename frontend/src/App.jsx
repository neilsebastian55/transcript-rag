import { useState, useRef, useCallback } from 'react'
import { api } from './api'
import LoadPanel from './components/LoadPanel'
import QueryPanel from './components/QueryPanel'
import CollectionBadge from './components/CollectionBadge'
import styles from './App.module.css'

export default function App() {
  const [collection, setCollection] = useState(null)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const bottomRef = useRef(null)

  const handleLoad = useCallback((col) => {
    setCollection(col)
    setResults([])
    setHistory([])
    setError(null)
  }, [])

  const handleQuery = useCallback(async (question) => {
    if (!collection) return
    setLoading(true)
    setError(null)

    const optimisticId = `pending-${Date.now()}`
    setResults(prev => [{ id: optimisticId, question, pending: true }, ...prev])

    try {
      const result = await api.query(question, collection.collection_id, history)
      setHistory(prev => [
        ...prev,
        { role: 'user', content: question },
        { role: 'assistant', content: result.answer },
      ])
      setResults(prev => prev.map(r =>
        r.id === optimisticId ? { ...result, question, id: result.query_id } : r
      ))
    } catch (e) {
      setError(e.message)
      setResults(prev => prev.filter(r => r.id !== optimisticId))
    } finally {
      setLoading(false)
    }
  }, [collection, history])

  const handleFeedback = useCallback(async (queryId, rating) => {
    if (!collection) return
    await api.feedback(queryId, rating, collection.collection_id)
  }, [collection])

  const handleReset = useCallback(() => {
    setCollection(null)
    setResults([])
    setHistory([])
    setError(null)
  }, [])

  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar}>
        <div className={styles.logo}>
          <span className={styles.logoMark}>▲</span>
          <span className={styles.logoText}>transcript<br />intelligence</span>
        </div>

        {collection && (
          <CollectionBadge collection={collection} onReset={handleReset} />
        )}

        <LoadPanel onLoad={handleLoad} hasCollection={!!collection} />

        <div className={styles.footer}>
          <p>Built for Great Question</p>
          <p>RAG · ChromaDB · Claude</p>
        </div>
      </aside>

      <main className={styles.main}>
        <QueryPanel
          collection={collection}
          results={results}
          loading={loading}
          error={error}
          onQuery={handleQuery}
          onFeedback={handleFeedback}
          historyLength={history.length / 2}
        />
        <div ref={bottomRef} />
      </main>
    </div>
  )
}
