export default function Navbar({ user, onOpenAuth, onLogout }) {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-20">
      <div className="mx-auto flex max-w-3xl items-center justify-between px-5 py-3.5">
        <a href="/" className="text-base font-bold tracking-tight text-slate-100">
          Git<span className="text-cyan-400">Summarizer</span>
        </a>

        <div>
          {user ? (
            <div className="flex items-center gap-4">
              <span className="text-xs text-slate-300">
                {user.name || user.email}
              </span>
              <button
                type="button"
                onClick={onLogout}
                className="text-xs text-slate-400 hover:text-slate-200 transition"
              >
                Sign out
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={onOpenAuth}
              className="rounded-lg bg-cyan-400 px-3.5 py-1.5 text-xs font-semibold text-slate-950 hover:bg-cyan-300 transition"
            >
              Sign in
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
