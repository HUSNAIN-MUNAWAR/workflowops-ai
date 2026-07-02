'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Shell } from '@/components/Shell'
import { Card, ErrorState, StatusPill, RiskBadge } from '@/components/Cards'
import { apiFetch } from '@/lib/api'

export default function DashboardPage() {
  const [summary, setSummary] = useState<any>(null)
  const [runs, setRuns] = useState<any[]>([])
  const [error, setError] = useState('')
  useEffect(() => { Promise.all([apiFetch<any>('/dashboard/summary'), apiFetch<any[]>('/dashboard/recent-runs')]).then(([s,r]) => { setSummary(s); setRuns(r) }).catch(e => setError(e.message || 'Backend unavailable. Login first and start FastAPI on port 8000.')) }, [])
  return <Shell><div className="flex items-center justify-between"><div><h1 className="text-3xl font-bold text-slate-950">Operations Dashboard</h1><p className="text-slate-500">Live values from the database-backed FastAPI demo.</p></div><Link className="rounded-xl bg-slate-950 px-4 py-2 text-white" href="/login">Login</Link></div>
    {error ? <div className="mt-6"><ErrorState message={error}/></div> : null}
    {!summary && !error ? <p className="mt-6 text-slate-500">Loading dashboard...</p> : null}
    {summary ? <div className="mt-6 grid grid-cols-4 gap-4">
      <Card title="Workflow Runs" value={summary.total_workflow_runs}/><Card title="Pending Approvals" value={summary.pending_approvals}/><Card title="Failed Automations" value={summary.failed_automations}/><Card title="Avg Reliability" value={`${summary.average_reliability_score}%`}/>
      <Card title="Documents Processed" value={summary.documents_processed}/><Card title="SLA Breaches" value={summary.sla_breaches}/><Card title="Templates Used" value={Object.keys(summary.template_usage || {}).length}/><Card title="Mode" value="Demo" caption="Synthetic validation"/>
    </div> : null}
    <section className="mt-8 rounded-3xl bg-white p-6 shadow-sm"><h2 className="text-xl font-semibold">Latest Runs</h2><div className="mt-4 overflow-hidden rounded-2xl border"><table className="w-full text-sm"><thead className="bg-slate-50 text-left"><tr><th className="p-3">Template</th><th>Status</th><th>Risk</th><th>Current Step</th></tr></thead><tbody>{runs.map(r=><tr key={r.id} className="border-t"><td className="p-3 font-medium">{r.template_slug}</td><td><StatusPill status={r.status}/></td><td><RiskBadge score={r.risk_score}/></td><td>{r.current_step || '-'}</td></tr>)}</tbody></table></div></section>
  </Shell>
}
