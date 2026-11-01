// Small helpers for talking to the FastAPI backend.
// Every endpoint returns { status: "success", ... } or { status: "error", message }.

async function post(path, body) {
  let response
  try {
    response = await fetch(`/api${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  } catch {
    throw new Error("Can't reach the backend. Is uvicorn running?")
  }

  // The Vite proxy answers with 500/502/504 when the backend isn't running
  if ([500, 502, 504].includes(response.status)) {
    throw new Error("Can't reach the backend. Is uvicorn running?")
  }
  if (!response.ok) {
    throw new Error(`The backend returned an error (${response.status}).`)
  }

  const data = await response.json()
  if (data.status === 'error') {
    throw new Error(data.message)
  }
  return data
}

export function analyzeRepo(url) {
  return post('/analyze/repo', { url })
}

export function analyzeCode(code, filename) {
  return post('/analyze/code', { code, filename })
}

export function explainCode({ code, name, type, language }) {
  return post('/explain', { code, name, type, language })
}
