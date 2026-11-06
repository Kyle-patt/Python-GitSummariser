import { useState } from 'react'

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(true)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  if (!isOpen) return null

  function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (!email.trim() || !password.trim()) {
      setError('Please fill in all required fields.')
      return
    }

    if (!isLogin && !name.trim()) {
      setError('Please enter your full name.')
      return
    }

    const userData = {
      name: isLogin ? email.split('@')[0] : name.trim(),
      email: email.trim(),
    }

    onAuthSuccess(userData, 'mock-jwt-token')
    onClose()
  }

  function handleModeChange(loginMode) {
    setIsLogin(loginMode)
    setError('')
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="w-full max-w-sm rounded-2xl border border-slate-800 bg-[#0e1420] p-6 shadow-2xl">
        <div className="flex items-center justify-between pb-3">
          <h2 className="text-base font-semibold text-slate-100">
            {isLogin ? 'Welcome back' : 'Create an account'}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 text-sm leading-none"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <p className="text-xs text-slate-400 mb-4">
          {isLogin
            ? 'Sign in to access your saved summaries and history.'
            : 'Get started to save and analyze repositories.'}
        </p>

        <div className="grid grid-cols-2 rounded-lg bg-slate-950 p-1 mb-5 border border-slate-800/80">
          <button
            type="button"
            onClick={() => handleModeChange(true)}
            className={`rounded-md py-1.5 text-xs font-medium transition ${
              isLogin ? 'bg-slate-800 text-slate-100 shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => handleModeChange(false)}
            className={`rounded-md py-1.5 text-xs font-medium transition ${
              !isLogin ? 'bg-slate-800 text-slate-100 shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Register
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-500/10 border border-red-500/20 p-2.5 text-xs text-red-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          {!isLogin && (
            <div>
              <label className="block text-[11px] font-medium text-slate-400 mb-1">
                Full Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Jane Doe"
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-100 placeholder:text-slate-600 outline-none focus:border-cyan-500 transition"
              />
            </div>
          )}

          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-1">
              Email address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-100 placeholder:text-slate-600 outline-none focus:border-cyan-500 transition"
            />
          </div>

          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-100 placeholder:text-slate-600 outline-none focus:border-cyan-500 transition"
            />
          </div>

          <button
            type="submit"
            className="w-full rounded-lg bg-cyan-400 py-2.5 text-xs font-semibold text-slate-950 hover:bg-cyan-300 transition mt-2"
          >
            {isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>
      </div>
    </div>
  )
}
