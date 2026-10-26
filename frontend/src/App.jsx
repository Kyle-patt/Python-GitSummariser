
import { useState } from 'react'
import './App.css'

const API_URL = 'http://127.0.0.1:8000'

function App() {
  const [repositoryUrl, setRepositoryUrl] = useState('')
  const [repository, setRepository] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function analyzeRepository(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setRepository(null)

    try {
      const response = await fetch(`${API_URL}/api/repository/info`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repository_url: repositoryUrl.trim() }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Could not retrieve repository information.')
      }

      setRepository(data)
    } catch (err) {
      setError(
        err instanceof TypeError
          ? 'Could not connect to the backend. Check that FastAPI is running.'
          : err.message,
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-5 py-12 text-slate-100">
      <section className="mx-auto max-w-3xl">
        <header className="mb-12 text-center">
          <p className="mb-3 text-sm font-semibold uppercase tracking-[0.3em] text-cyan-400">
            Developer toolkit
          </p>
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            Git<span className="text-cyan-400">Summarizer</span>
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-slate-400">
            Explore a GitHub repository and get its essential information in one place.
          </p>
        </header>

        <form
          onSubmit={analyzeRepository}
          className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-2xl sm:p-7"
        >
          <label htmlFor="repositoryUrl" className="mb-2 block text-sm font-medium">
            GitHub repository URL
          </label>

          <div className="flex flex-col gap-3 sm:flex-row">
            <input
              id="repositoryUrl"
              type="url"
              required
              maxLength={500}
              placeholder="https://github.com/owner/repository"
              value={repositoryUrl}
              onChange={(event) => setRepositoryUrl(event.target.value)}
              className="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
            />

            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-cyan-400 px-6 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? 'Loading...' : 'Analyze Repository'}
            </button>
          </div>

          <p className="mt-3 text-xs text-slate-500">
            Start with a publicly accessible GitHub repository.
          </p>
        </form>

        {error && (
          <div role="alert" className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">
            {error}
          </div>
        )}

        {repository && (
          <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-sm text-cyan-400">Repository details</p>
                <h2 className="mt-2 text-2xl font-bold">{repository.full_name}</h2>
              </div>

              <a
                href={repository.html_url}
                target="_blank"
                rel="noreferrer"
                className="text-sm text-cyan-400 underline underline-offset-4"
              >
                View on GitHub ↗
              </a>
            </div>

            <p className="mt-4 leading-7 text-slate-300">
              {repository.description || 'No description provided.'}
            </p>

            <div className="mt-7 grid grid-cols-2 gap-4 sm:grid-cols-4">
              {[
                ['Stars', repository.stars.toLocaleString()],
                ['Forks', repository.forks.toLocaleString()],
                ['Language', repository.language || 'Not specified'],
                ['Open issues', repository.open_issues.toLocaleString()],
              ].map(([label, value]) => (
                <div key={label} className="rounded-xl bg-slate-800/70 p-4">
                  <p className="text-xs text-slate-400">{label}</p>
                  <p className="mt-2 break-words text-lg font-semibold">{value}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        <footer className="mt-12 text-center text-xs text-slate-600">
          GitSummarizer · Built with React and FastAPI
        </footer>
      </section>
    </main>
  )
}

export default App
