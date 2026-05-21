import { X, FileText } from 'lucide-react'
import styles from './CollectionBadge.module.css'

export default function CollectionBadge({ collection, onReset }) {
  const { source, word_count, chunk_count } = collection

  return (
    <div className={styles.badge}>
      <div className={styles.header}>
        <FileText size={13} />
        <span className={styles.source} title={source}>{source}</span>
        <button className={styles.close} onClick={onReset} title="Remove">
          <X size={12} />
        </button>
      </div>
      <div className={styles.stats}>
        <span>{word_count?.toLocaleString()} words</span>
        <span>·</span>
        <span>{chunk_count} chunks</span>
      </div>
    </div>
  )
}
