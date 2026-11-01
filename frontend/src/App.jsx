import { useMemo, useState } from 'react'
import { analyzeCode, analyzeRepo, explainCode } from './api.js'
import InputPanel from './components/InputPanel.jsx'
import TreeView from './components/TreeView.jsx'
import DetailsPanel from './components/DetailsPanel.jsx'

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

  const languages = useMemo(() => (result ? collectLanguages(result.tree) : {}), [result])

  async function load(request) {
    setLoading(true)
    setError(null)
    try {
      const data = await request()
      setResult(data)
      setSelected(data.tree)
      setExplanations({})
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
    <div className="app">
      <header className="app-header">
        <h1>Git Repo Visualizer</h1>
        <p className="muted">See any codebase as a tree of folders, files, classes and methods.</p>
      </header>

      <InputPanel
        loading={loading}
        onAnalyzeRepo={(url) => load(() => analyzeRepo(url))}
        onAnalyzeCode={(code, filename) => load(() => analyzeCode(code, filename))}
      />

      {error && <p className="error-banner" role="alert">{error}</p>}

      {result && (
        <main className="workspace">
          <aside className="sidebar">
            <TreeView tree={result.tree} selectedId={selected?.id} onSelect={setSelected} />
          </aside>
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
