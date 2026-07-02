'use client'

import { useEffect, useMemo, useState } from 'react'
import Link from 'next/link'
import { Shell } from '@/components/Shell'
import { AutomationCanvas } from '@/components/AutomationCanvas'
import { Card, ErrorState, RiskBadge, StatusPill } from '@/components/Cards'
import { apiFetch } from '@/lib/api'

export default function DashboardPage() {
  const [summary, setSummary] = useState<any>(null)
  const [runs, setRuns] = useState<any[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([
      apiFetch<any>('/dashboard/summary'),
      apiFetch<any[]>('/dashboard/recent-runs'),
    ])
      .then(([dashboardSummary, recentRuns]) => {
        setSummary(dashboardSummary)
        setRuns(recentRuns)
      })
      .catch((fetchError) => setError(fetchError.message || 'Backend unavailable. Login first and start FastAPI on port 8000.'))
  }, [])

  const templateUsage = useMemo(() => {
    if (!summary?.template_usage) return []
    return Object.entries(summary.template_usage as Record<string, number>).sort((a, b) => b[1] - a[1])
  }, [summary])

  return <Shell>
    <section className="overflow-hidden rounded-[36px] border border-[#0f2237] bg-[#081321] px-6 py-7 text-white shadow-[0_35px_120px_rgba(2,6,23,0.28)] sm:px-8 lg:px-9">
      <div className="pointer-events-none absolute" />
      <div className="grid gap-8 xl:grid-cols-[1.15fr_0.85fr]">
        <div>
          <div className="inline-flex rounded-full border border-cyan-300/25 bg-cyan-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-cyan-100">Connected operations command center</div>
          <h1 className="font-display mt-6 text-4xl font-semibold tracking-tight text-white sm:text-5xl">Operations Dashboard</h1>
          <p className="mt-4 max-w-3xl text-base leading-7 text-slate-300">Keep operational automation visible and understandable: how much work is running, which approvals need attention, how reliable the workflows are, and where teams should intervene next.</p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link href="/approvals" className="rounded-2xl bg-white px-5 py-3 text-sm font-semibold text-slate-950 shadow-lg transition hover:translate-y-[-1px]">Open approval queue</Link>
            <Link href="/templates" className="rounded-2xl border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10">Review workflow templates</Link>
            <Link href="/reliability" className="rounded-2xl border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10">Inspect reliability</Link>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {[
            ['Automation posture', `${summary ? Object.keys(summary.template_usage || {}).length : '—'} active lanes`, 'Template families currently running in the workspace'],
            ['Approval attention', `${summary?.pending_approvals ?? '—'} queued`, 'Human review stays in the loop for sensitive workflow actions'],
            ['Reliability coverage', `${summary?.average_reliability_score ?? '—'}% score`, 'Synthetic validation coverage for workflow safety and fallback behavior'],
            ['Evidence footprint', `${summary?.documents_processed ?? '—'} processed`, 'Documents, runs, and reports remain traceable through the operating cycle'],
          ].map(([title, value, caption]) => <div key={title} className="rounded-[28px] border border-white/10 bg-white/6 p-5 backdrop-blur-sm">
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-300">{title}</p>
            <p className="font-display mt-3 text-3xl font-semibold tracking-tight text-white">{value}</p>
            <p className="mt-3 text-sm leading-6 text-slate-300">{caption}</p>
          </div>)}
        </div>
      </div>
    </section>

    {error ? <div className="mt-6"><ErrorState message={error} /></div> : null}
    {!summary && !error ? <p className="mt-6 text-slate-500">Loading dashboard...</p> : null}

    {summary ? <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <Card title="Workflow Runs" value={summary.total_workflow_runs} caption="Persisted runs across all active automation lanes." />
      <Card title="Pending Approvals" value={summary.pending_approvals} caption="Items waiting on a person before any sensitive action proceeds." />
      <Card title="Failed Automations" value={summary.failed_automations} caption="Runs that require investigation or replay." />
      <Card title="Average Reliability" value={`${summary.average_reliability_score}%`} caption="Current safety and resilience posture for the test suite." />
      <Card title="Documents Processed" value={summary.documents_processed} caption="Business records ingested and classified into the system." />
      <Card title="SLA Breaches" value={summary.sla_breaches} caption="Exception volume currently tracked in the workspace." />
      <Card title="Templates Used" value={Object.keys(summary.template_usage || {}).length} caption="Workflow families represented in the seeded operating data." />
      <Card title="Workspace Mode" value="Connected demo" caption="Synthetic records backed by the live FastAPI application." />
    </div> : null}

    <div className="mt-8 grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">
      <AutomationCanvas
        pendingApprovals={summary?.pending_approvals}
        reliabilityScore={summary?.average_reliability_score}
        reportCount={templateUsage.length || 6}
        title="Business automation flow"
        caption="The workflow stays legible for non-technical operators: intake, extraction, policy, review, connector action, and evidence all appear as one operating chain."
      />

      <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
        <div className="inline-flex rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Automation demand</div>
        <h2 className="font-display mt-4 text-2xl font-semibold tracking-tight text-slate-950">Highest-usage workflow lanes</h2>
        <p className="mt-2 text-sm leading-6 text-slate-500">This panel gives business stakeholders a compact view of which automation patterns are most active in the environment.</p>
        <div className="mt-6 space-y-3">
          {templateUsage.length ? templateUsage.map(([slug, count]) => <div key={slug} className="rounded-[24px] border border-slate-200 bg-white/90 p-4 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="font-display text-lg font-semibold tracking-tight text-slate-950">{slug.replace(/_/g, ' ')}</p>
                <p className="mt-1 text-xs uppercase tracking-[0.22em] text-slate-400">Template usage volume</p>
              </div>
              <div className="rounded-full border border-cyan-200 bg-cyan-50 px-3 py-1 text-sm font-semibold text-cyan-700">{count}</div>
            </div>
          </div>) : <div className="rounded-[24px] border border-dashed border-slate-300 bg-white/80 p-6 text-sm text-slate-500">No template usage metrics available yet.</div>}
        </div>
      </section>
    </div>

    <section className="surface-panel-strong mt-8 rounded-[34px] p-6 lg:p-7">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="inline-flex rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Recent activity</div>
          <h2 className="font-display mt-4 text-2xl font-semibold tracking-tight text-slate-950">Latest Runs</h2>
          <p className="mt-2 text-sm leading-6 text-slate-500">Operators can immediately see which workflows are complete, which ones are waiting for review, and where the current step sits.</p>
        </div>
      </div>
      <div className="mt-6 overflow-hidden rounded-[28px] border border-slate-200 bg-white/85">
        <table className="w-full min-w-[720px] text-sm">
          <thead className="bg-slate-50/90 text-left">
            <tr>
              <th className="px-4 py-4 font-semibold text-slate-500">Template</th>
              <th className="px-4 py-4 font-semibold text-slate-500">Status</th>
              <th className="px-4 py-4 font-semibold text-slate-500">Risk</th>
              <th className="px-4 py-4 font-semibold text-slate-500">Current Step</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => <tr key={run.id} className="border-t border-slate-100">
              <td className="px-4 py-4">
                <p className="font-display text-lg font-semibold tracking-tight text-slate-950">{run.template_slug}</p>
              </td>
              <td className="px-4 py-4"><StatusPill status={run.status} /></td>
              <td className="px-4 py-4"><RiskBadge score={run.risk_score} /></td>
              <td className="px-4 py-4 text-slate-500">{run.current_step || '-'}</td>
            </tr>)}
          </tbody>
        </table>
      </div>
    </section>
  </Shell>
}
