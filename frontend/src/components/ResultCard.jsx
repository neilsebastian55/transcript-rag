import { useState } from 'react'
import { ThumbsUp, ThumbsDown, ChevronDown, ChevronUp, Loader, Database } from 'lucide-react'
import styles from './ResultCard.module.css'

export default function ResultCard({ result, onFeedback }) {
  const [showChunks, setShowChunks] = useState(false)
  const [feedback, setFeedback] = useState(null)

  const handleFeedback = (rating) => {
    if (feedback) return
    setFeedback(rating)
    onFeedback(result.id, rating)
  }

  if (result.pending) {
    return (
      <div className={styles.card}>
        <div className={styles.question}>{result.question}</div>
        <div className={styles.loading}>
          <Loader size={14} className={styles.spin} />
          <span>Retrieving and synthesizing…</span>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.card}>
      <div className={styles.question}>{result.question}</div>
      <div className={styles.answer}>{result.answer}</div>

      {result.usage && (
        <div className={styles.usage}>
          {result.usage.input_tokens + result.usage.output_tokens} tokens
        </div>
      )}

      <div className={styles.footer}>
        <button
          className={styles.chunksToggle}
          onClick={() => setShowChunks(!showChunks)}
        >
          <Database size={12} />
          {result.chunks?.length} chunks retrieved
          {showChunks ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </button>

        <div className={styles.feedbackGroup}>
          <span className={styles.feedbackLabel}>retrieval quality:</span>
          <button
            className={`${styles.fbBtn} ${feedback === 'good' ? styles.fbGood : ''}`}
            onClick={() => handleFeedback('good')}
            title="Relevant"
          >
            <ThumbsUp size={12} />
          </button>
          <button
            className={`${styles.fbBtn} ${feedback === 'bad' ? styles.fbBad : ''}`}
            onClick={() => handleFeedback('bad')}
            title="Off-target"
          >
            <ThumbsDown size={12} />
          </button>
        </div>
      </div>

      {showChunks && result.chunks && (
        <div className={styles.chunks}>
          {result.chunks.map((chunk, i) => (
            <div key={i} className={styles.chunk}>
              <div className={styles.chunkMeta}>
                <span className={styles.chunkIndex}>chunk {chunk.index + 1}</span>
                <div className={styles.relevanceBar}>
                  <div
                    className={styles.relevanceFill}
                    style={{ width: `${Math.round(chunk.relevance * 100)}%` }}
                  />
                </div>
                <span className={styles.relevancePct}>{Math.round(chunk.relevance * 100)}%</span>
              </div>
              <p className={styles.chunkText}>{chunk.text.slice(0, 300)}{chunk.text.length > 300 ? '…' : ''}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
