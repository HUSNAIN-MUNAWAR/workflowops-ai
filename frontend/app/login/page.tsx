'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { login } from '@/lib/api'
import { AutomationCanvas } from '@/components/AutomationCanvas'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('admin@example.com')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  async function submit(e: React.FormEvent) {
    e.preventDefault(); setLoading(true); setError('')
    try { await login(email, password); router.push('/dashboard') }
    catch (err: any) { setError(err.message || 'Login failed') }
    finally { setLoading(false) }
  }
  return <main className="min-h-screen px-4 py-5 sm:px-6 lg:px-8">
    <div className="surface-panel-strong mx-auto grid min-h-[calc(100vh-2.5rem)] max-w-[1680px] overflow-hidden rounded-[40px] border border-white/70 bg-[#081321] text-white shadow-[0_35px_120px_rgba(2,6,23,0.34)] xl:grid-cols-[0.9fr_1.1fr]">
      <section className="relative overflow-hidden px-6 py-8 sm:px-8 lg:px-10 lg:py-10">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.18),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(245,158,11,0.16),transparent_24%)]" />
        <div className="relative flex h-full flex-col">
          <div className="inline-flex w-max rounded-full border border-cyan-300/30 bg-cyan-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-cyan-100">Workspace access</div>
          <h1 className="font-display mt-8 text-4xl font-semibold tracking-tight sm:text-5xl">WorkflowOps AI Demo Login</h1>
          <p className="mt-5 max-w-xl text-base leading-7 text-slate-300">Sign in to the connected automation workspace and review the operational dashboards, approval queues, workflow runs, reliability views, and reporting surfaces backed by the demo API.</p>
          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            {[
              'Admin can operate and review every screen',
              'Reviewer can act on approval decisions',
              'Viewer can inspect the system without decision rights',
            ].map((item) => <div key={item} className="rounded-[24px] border border-white/10 bg-white/6 px-4 py-4 text-sm leading-6 text-slate-200 backdrop-blur-sm">{item}</div>)}
          </div>
          <div className="mt-8 hidden xl:block">
            <AutomationCanvas
              title="What happens after login"
              caption="The demo environment already contains seeded automation runs, approval states, reports, and reliability evidence so the workspace feels operational from the first screen."
            />
          </div>
        </div>
      </section>

      <section className="flex items-center border-t border-white/10 bg-white/5 px-6 py-8 backdrop-blur-sm xl:border-l xl:border-t-0 xl:px-10">
        <div className="surface-panel-strong w-full max-w-xl rounded-[34px] p-7 text-slate-950">
          <div className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Connected demo credentials</div>
          <form onSubmit={submit} className="mt-6 space-y-4">
            <div>
              <label className="text-sm font-semibold text-slate-700" htmlFor="email">Email</label>
              <input id="email" aria-label="Email" className="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm outline-none transition focus:border-cyan-300 focus:ring-4 focus:ring-cyan-100" value={email} onChange={e=>setEmail(e.target.value)} />
            </div>
            <div>
              <label className="text-sm font-semibold text-slate-700" htmlFor="password">Password</label>
              <input id="password" aria-label="Password" className="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm outline-none transition focus:border-cyan-300 focus:ring-4 focus:ring-cyan-100" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
            </div>
            {error ? <p className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{error}</p> : null}
            <button className="w-full rounded-2xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white shadow-[0_18px_40px_rgba(15,23,42,0.18)] transition hover:translate-y-[-1px]" disabled={loading}>{loading ? 'Signing in...' : 'Login'}</button>
          </form>
          <div className="mt-6 rounded-[24px] border border-slate-200 bg-slate-50 px-4 py-4 text-xs leading-6 text-slate-600">
            <p><span className="font-semibold text-slate-900">Admin:</span> admin@example.com / admin123</p>
            <p><span className="font-semibold text-slate-900">Reviewer:</span> reviewer@example.com / reviewer123</p>
            <p><span className="font-semibold text-slate-900">Viewer:</span> viewer@example.com / viewer123</p>
          </div>
        </div>
      </section>
    </div>
  </main>
}
