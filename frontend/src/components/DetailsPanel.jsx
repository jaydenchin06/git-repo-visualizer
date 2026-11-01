import { useState } from 'react'
import Markdown from 'react-markdown'
import CodeView from './CodeView.jsx'
import { TypeBadge } from './TreeView.jsx'

const TYPE_NAMES = { folder: 'Folder', file: 'File', class: 'Class', function: 'Function', method: 'Method' }

// Cuts the selected node's code out of its file
function getCode(node, files) {
  const content = files[node.path] ?? ''
  if (node.type === 'file') {
    return { code: content, firstLine: 1 }
  }
  const lines = content.split('\n')
  return {
    code: lines.slice(node.line_start - 1, node.line_end).join('\n'),
    firstLine: node.line_start,
  }
}

// Counts everything inside a folder, e.g. { file: 4, class: 2, function: 3, method: 5 }
function countTypes(node, counts = {}) {
  for (const child of node.children) {
    counts[child.type] = (counts[child.type] || 0) + 1
    countTypes(child, counts)
  }
  return counts
}

function FolderSummary({ node, skipped }) {
  const counts = countTypes(node)
  const stats = [
    ['folder', 'Folders'],
    ['file', 'Files'],
    ['class', 'Classes'],
    ['function', 'Functions'],
    ['method', 'Methods'],
  ]
  return (
    <>
      <div className="stats">
        {stats.map(([type, label]) => (
          <div className="stat" key={type}>
            <span className="stat-value">{counts[type] || 0}</span>
            <span className="stat-label">{label}</span>
          </div>
        ))}
      </div>
      {node.path === '' && skipped > 0 && (
        <p className="muted">{skipped} file{skipped === 1 ? ' was' : 's were'} left out (images, binaries or very large files).</p>
      )}
      <p className="muted">Pick a file, class or function on the left to see its code.</p>
    </>
  )
}

export default function DetailsPanel({ node, files, language, skipped, explanation, onExplain }) {
  const [showCode, setShowCode] = useState(true)

  if (!node) {
    return (
      <div className="details empty-state">
        <p>Pick something from the tree to see its code.</p>
      </div>
    )
  }

  const isFolder = node.type === 'folder'
  const { code, firstLine } = isFolder ? {} : getCode(node, files)

  return (
    <div className="details">
      <header className="details-header">
        <div className="details-title">
          <TypeBadge type={node.type} />
          <h2>{node.name}</h2>
          <span className="type-name">{TYPE_NAMES[node.type]}</span>
        </div>
        <p className="details-meta">
          {node.path || 'Top level'}
          {node.line_start && ` · lines ${node.line_start}–${node.line_end}`}
          {node.type === 'file' && ` · ${node.line_count} lines`}
          {language && !isFolder && ` · ${language}`}
        </p>
      </header>

      {node.error && <p className="error-banner">{node.error}</p>}

      {isFolder ? (
        <FolderSummary node={node} skipped={skipped} />
      ) : (
        <>
          <div className="actions">
            <button type="button" className="secondary-button" onClick={() => setShowCode(!showCode)}>
              {showCode ? 'Hide code' : 'View code'}
            </button>
            <button
              type="button"
              className="primary-button"
              onClick={() => onExplain(node, code)}
              disabled={explanation?.loading}
            >
              {explanation?.loading ? 'Thinking…' : explanation?.text ? 'Explain again' : 'Explain with AI'}
            </button>
          </div>

          {explanation?.error && <p className="error-banner">{explanation.error}</p>}
          {explanation?.text && (
            <section className="explanation" aria-label="AI explanation">
              <h3>AI explanation</h3>
              <Markdown>{explanation.text}</Markdown>
            </section>
          )}

          {showCode && <CodeView code={code} firstLine={firstLine} language={language} />}
        </>
      )}
    </div>
  )
}
