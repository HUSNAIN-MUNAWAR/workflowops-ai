'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { login } from '@/lib/api'

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
  return <main className="min-h-screen bg-slate-950 p-8 text-white">
    <div className="mx-auto mt-24 max-w-md rounded-3xl bg-white p-8 text-slate-950 shadow-2xl">
      <h1 className="text-2xl font-bold">WorkflowOps AI Demo Login</h1>
      <p className="mt-2 text-sm text-slate-500">Use seeded synthetic credentials. No paid API key is required.</p>
      <form onSubmit={submit} className="mt-6 space-y-4">
        <input aria-label="Email" className="w-full rounded-xl border p-3" value={email} onChange={e=>setEmail(e.target.value)} />
        <input aria-label="Password" className="w-full rounded-xl border p-3" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        {error ? <p className="text-sm text-red-600">{error}</p> : null}
        <button className="w-full rounded-xl bg-slate-950 px-4 py-3 font-semibold text-white" disabled={loading}>{loading ? 'Signing in...' : 'Login'}</button>
      </form>
      <div className="mt-5 text-xs text-slate-500">admin@example.com/admin123 · reviewer@example.com/reviewer123 · viewer@example.com/viewer123</div>
    </div>
  </main>
}
