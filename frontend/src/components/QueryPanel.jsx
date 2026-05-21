import { useState } from 'react'
import { Search, MessageSquare } from 'lucide-react'
import ResultCard from './ResultCard'
import styles from './QueryPanel.module.css'

const SUGGESTIONS = [
  'What are the main topics covered?',
  'What pain points or problems were mentioned?',
  'Summarize the key recommendations',
  'What questions were asked during the interview?',
  'What conclusions were reached?',
]

const ZZZ_SUGGESTIONS = [
  'What are her best team compositions?',
  'Which W-engine is best without her signature?',
  'What are the pros and cons of pulling?',
  'Explain her skill priority and combos',
  'What stats should I aim for?',
]

function detectSuggestions(source) {
  if (!source) return SUGGESTIONS
  const s = source.toLowerCase()
  if (s.includes('zenless') || s.includes('promeia') || s.includes('zzz')) {
    return ZZZ_SUGGESTIONS
  }
  return SUGGESTIONS
}

export default function QueryPanel({ collection, results, loading, error, onQuery, onFeedback, historyLength }) {
  const [question, setQuestion] = useState('')

  const submit = () => {
    const q = question.trim()
    if (!q || loading) return
    onQuery(q)
    setQuestion('')
  }

  const suggestions = detectSuggestions(collection?.source)

  return (
    <div className={styles.panel}>
      <div className={styles.inputRow}>
        <Search size={16} className={styles.searchIcon} />
        <input
          className={styles.input}
          placeholder={collection ? 'Ask anything about the transcript…' : 'Load a transcript first…'}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submit()}
          disabled={!collection || loading}
        />
        <button
          className={styles.submitBtn}
          onClick={submit}
          disabled={!collection || loading || !question.trim()}
        >
          Ask
        </button>
      </div>

      {collection && historyLength > 0 && (
        <div className={styles.contextNote}>
          <MessageSquare size={11} />
          {historyLength} turn{historyLength !== 1 ? 's' : ''} of context
        </div>
      )}

      {error && <div className={styles.error}>{error}</div>}

      {collection && results.length === 0 && !loading && (
        <div className={styles.suggestions}>
          <div className={styles.suggestionsLabel}>try asking</div>
          <div className={styles.chips}>
            {suggestions.map((s) => (
              <button
                key={s}
                className={styles.chip}
                onClick={() => { setQuestion(s); }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {!collection && (
        <div className={styles.emptyState}>
          <Search size={32} strokeWidth={1} />
          <p>Load a transcript from the sidebar to get started</p>
        </div>
      )}

      <div className={styles.results}>
        {results.map((result) => (
          <ResultCard
            key={result.id}
            result={result}
            onFeedback={onFeedback}
          />
        ))}
      </div>
    </div>
  )
}
