import { useState } from 'react'

const EXAMPLE_REPO = 'https://github.com/jaydenchin06/git-repo-visualizer'

const EXAMPLE_CODE = `class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Not enough money")
        self.balance -= amount


def transfer(source, target, amount):
    source.withdraw(amount)
    target.deposit(amount)
`

// Lets the user either paste a GitHub link or paste code directly
export default function InputPanel({ loading, onAnalyzeRepo, onAnalyzeCode }) {
  const [mode, setMode] = useState('repo')
  const [url, setUrl] = useState('')
  const [code, setCode] = useState('')
  const [filename, setFilename] = useState('pasted_code.py')

  function handleSubmit(event) {
    event.preventDefault()
    if (!canSubmit) {
      return
    }
    if (mode === 'repo') {
      onAnalyzeRepo(url.trim())
    } else {
      onAnalyzeCode(code, filename.trim() || 'pasted_code.py')
    }
  }

  function fillExample() {
    if (mode === 'repo') {
      setUrl(EXAMPLE_REPO)
    } else {
      setCode(EXAMPLE_CODE)
      setFilename('bank.py')
    }
  }

  const canSubmit = !loading && (mode === 'repo' ? url.trim() : code.trim())

  return (
    <form className="input-panel" onSubmit={handleSubmit}>
      <div className="tabs" role="tablist">
        <button type="button" role="tab" aria-selected={mode === 'repo'}
          className={mode === 'repo' ? 'tab active' : 'tab'} onClick={() => setMode('repo')}>
          GitHub repo
        </button>
        <button type="button" role="tab" aria-selected={mode === 'code'}
          className={mode === 'code' ? 'tab active' : 'tab'} onClick={() => setMode('code')}>
          Paste code
        </button>
        <button type="button" className="link-button" onClick={fillExample}>
          Try an example
        </button>
      </div>

      {mode === 'repo' ? (
        <div className="input-row">
          <input
            type="text"
            className="text-input"
            placeholder="https://github.com/owner/repo"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            aria-label="GitHub repo link"
          />
          <button type="submit" className="primary-button" disabled={!canSubmit}>
            {loading ? 'Loading…' : 'Visualize'}
          </button>
        </div>
      ) : (
        <div className="paste-area">
          <textarea
            className="code-input"
            placeholder="Paste your Python code here"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            onKeyDown={(e) => {
              // Ctrl+Enter (Cmd+Enter on Mac) visualizes without reaching for the mouse
              if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                handleSubmit(e)
              }
            }}
            spellCheck={false}
            aria-label="Code to visualize"
          />
          <div className="input-row">
            <input
              type="text"
              className="text-input filename-input"
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              aria-label="File name"
            />
            <button type="submit" className="primary-button" disabled={!canSubmit}>
              {loading ? 'Loading…' : 'Visualize'}
            </button>
          </div>
        </div>
      )}
    </form>
  )
}
