import { useMemo } from 'react'
import hljs from 'highlight.js/lib/common'
import scala from 'highlight.js/lib/languages/scala'

// The common bundle covers most languages the backend parses, but not Scala
hljs.registerLanguage('scala', scala)

// Highlighting very large files makes the page freeze, so skip it past this size
const MAX_HIGHLIGHT_CHARS = 200000

function escapeHtml(text) {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function highlight(code, language) {
  if (language && hljs.getLanguage(language) && code.length <= MAX_HIGHLIGHT_CHARS) {
    return hljs.highlight(code, { language }).value
  }
  return escapeHtml(code)
}

// Shows code with line numbers that match the real file (firstLine is where it starts)
export default function CodeView({ code, firstLine, language }) {
  const html = useMemo(() => highlight(code, language), [code, language])
  const lineNumbers = useMemo(() => {
    const count = code.split('\n').length
    return Array.from({ length: count }, (_, i) => firstLine + i).join('\n')
  }, [code, firstLine])

  return (
    <div className="code-view">
      <pre className="gutter" aria-hidden="true">{lineNumbers}</pre>
      <pre className="code">
        <code className="hljs" dangerouslySetInnerHTML={{ __html: html }} />
      </pre>
    </div>
  )
}
