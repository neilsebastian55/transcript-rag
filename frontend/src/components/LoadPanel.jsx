import { useState, useRef, useCallback } from 'react'
import { Upload, Youtube, FileText, Loader } from 'lucide-react'
import { api } from '../api'
import styles from './LoadPanel.module.css'

const TABS = [
  { id: 'file', label: 'File', icon: Upload },
  { id: 'youtube', label: 'YouTube', icon: Youtube },
  { id: 'paste', label: 'Paste', icon: FileText },
]

export default function LoadPanel({ onLoad, hasCollection }) {
  const [tab, setTab] = useState('file')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [ytUrl, setYtUrl] = useState('')
  const [pasteText, setPasteText] = useState('')
  const fileRef = useRef(null)

  const load = useCallback(async (fn) => {
    setLoading(true)
    setError(null)
    try {
      const result = await fn()
      onLoad(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [onLoad])

  const handleFile = (file) => {
    if (!file) return
    load(() => api.uploadFile(file))
  }

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }, [])

  const handleYoutube = () => {
    if (!ytUrl.trim()) return
    load(() => api.loadYoutube(ytUrl.trim()))
  }

  const handlePaste = () => {
    if (!pasteText.trim()) return
    load(() => api.loadText(pasteText.trim(), 'pasted transcript'))
  }

  return (
    <div className={styles.panel}>
      <div className={styles.sectionLabel}>
        {hasCollection ? '+ load another' : 'load transcript'}
      </div>

      <div className={styles.tabs}>
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={`${styles.tab} ${tab === id ? styles.tabActive : ''}`}
            onClick={() => setTab(id)}
          >
            <Icon size={13} />
            {label}
          </button>
        ))}
      </div>

      {tab === 'file' && (
        <div
          className={`${styles.dropzone} ${dragging ? styles.dragging : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileRef.current?.click()}
        >
          <input
            ref={fileRef}
            type="file"
            accept=".txt,.md,.vtt,.srt"
            style={{ display: 'none' }}
            onChange={(e) => handleFile(e.target.files[0])}
          />
          {loading ? (
            <Loader size={18} className={styles.spin} />
          ) : (
            <Upload size={18} />
          )}
          <span>{loading ? 'Loading…' : 'Drop .txt / .vtt / .srt'}</span>
        </div>
      )}

      {tab === 'youtube' && (
        <div className={styles.inputGroup}>
          <input
            className={styles.input}
            placeholder="https://youtube.com/watch?v=..."
            value={ytUrl}
            onChange={(e) => setYtUrl(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleYoutube()}
          />
          <button
            className={styles.btn}
            onClick={handleYoutube}
            disabled={loading || !ytUrl.trim()}
          >
            {loading ? <Loader size={13} className={styles.spin} /> : 'Load'}
          </button>
        </div>
      )}

      {tab === 'paste' && (
        <div className={styles.inputGroup}>
          <textarea
            className={styles.textarea}
            placeholder="Paste transcript text here..."
            value={pasteText}
            onChange={(e) => setPasteText(e.target.value)}
            rows={6}
          />
          <button
            className={styles.btn}
            onClick={handlePaste}
            disabled={loading || pasteText.trim().length < 50}
          >
            {loading ? <Loader size={13} className={styles.spin} /> : 'Load'}
          </button>
        </div>
      )}

      {error && <div className={styles.error}>{error}</div>}
    </div>
  )
}
