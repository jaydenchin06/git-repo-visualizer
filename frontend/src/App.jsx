import { useEffect, useMemo, useState } from 'react'
import { analyzeCode, analyzeRepo, explainCode } from './api.js'
import InputPanel from './components/InputPanel.jsx'
import TreeView from './components/TreeView.jsx'
import DetailsPanel from './components/DetailsPanel.jsx'
import ResizeHandle, { DEFAULT_WIDTH, clampWidth } from './components/ResizeHandle.jsx'

// Remembers how wide you made the tree last time (localStorage can be blocked, so it's optional)
function loadSidebarWidth() {
  try {
    const saved = Number(localStorage.getItem('sidebarWidth'))
    return saved ? clampWidth(saved) : DEFAULT_WIDTH
  } catch {
    return DEFAULT_WIDTH
  }
}

// Maps each file path to its language, so classes/methods know what language they're in
function collectLanguages(node, languages = {}) {
  if (node.type === 'file') {
    languages[node.path] = node.language
  }
  node.children.forEach((child) => collectLanguages(child, languages))
  return languages
}

export default function App() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null) // { tree, files, skipped }
  const [selected, setSelected] = useState(null)
  // Explanations by node id: { loading, text, error }
  const [explanations, setExplanations] = useState({})
  // What's loaded (shown in the top bar), and whether the input box is open
  const [source, setSource] = useState('')
  const [showInput, setShowInput] = useState(true)
  const [sidebarWidth, setSidebarWidth] = useState(loadSidebarWidth)

  const languages = useMemo(() => (result ? collectLanguages(result.tree) : {}), [result])

  useEffect(() => {
    try {
      localStorage.setItem('sidebarWidth', sidebarWidth)
    } catch {
      // Not saving the width is fine
    }
  }, [sidebarWidth])

  async function load(request, label) {
    setLoading(true)
    setError(null)
    try {
      const data = await request()
      setResult(data)
      setSelected(data.tree)
      setExplanations({})
      setSource(label)
      setShowInput(false)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleExplain(node, code) {
    setExplanations((prev) => ({ ...prev, [node.id]: { loading: true } }))
    try {
      const data = await explainCode({ code, name: node.name, type: node.type, language: languages[node.path] })
      setExplanations((prev) => ({ ...prev, [node.id]: { text: data.explanation } }))
    } catch (e) {
      setExplanations((prev) => ({ ...prev, [node.id]: { error: e.message } }))
    }
  }

  return (
    // Once something is loaded the app fills the whole window, like an editor
    <div className={result ? 'app app-full' : 'app'}>
      <header className="app-header">
        <h1>Git Repo Visualizer</h1>
        {result ? (
          <>
            <span className="source" title={source}>{source}</span>
            <button type="button" className="secondary-button small-button" onClick={() => setShowInput(!showInput)}>
              {showInput ? 'Close' : 'Open another'}
            </button>
          </>
        ) : (
          <p className="muted">See any codebase as a tree of folders, files, classes and methods.</p>
        )}
      </header>

      {/* Hidden instead of removed so whatever you typed is still there when you reopen it */}
      <div hidden={!showInput}>
        <InputPanel
          loading={loading}
          onAnalyzeRepo={(url) => load(() => analyzeRepo(url), url.replace(/^https?:\/\/(www\.)?/, ''))}
          onAnalyzeCode={(code, filename) => load(() => analyzeCode(code, filename), `Pasted code · ${filename}`)}
        />
      </div>

      {error && <p className="error-banner" role="alert">{error}</p>}

      {result && (
        <main className="workspace" style={{ '--sidebar-width': `${sidebarWidth}px` }}>
          <aside className="sidebar">
            <TreeView tree={result.tree} selectedId={selected?.id} onSelect={setSelected} />
          </aside>
          <ResizeHandle width={sidebarWidth} onChange={setSidebarWidth} />
          <section className="main-panel">
            <DetailsPanel
              // Reset "Hide code" etc. whenever a different node is picked
              key={selected?.id}
              node={selected}
              files={result.files}
              language={selected ? languages[selected.path] : null}
              skipped={result.skipped}
              explanation={selected ? explanations[selected.id] : null}
              onExplain={handleExplain}
            />
          </section>
        </main>
      )}
    </div>
  )
}
