'use client'

import { useEffect, useMemo, useState } from 'react'
import { Shell } from '@/components/Shell'
import { Card, ErrorState, EmptyState, RiskBadge, StatusPill } from '@/components/Cards'
import { apiFetch } from '@/lib/api'

export default function Approvals() {
  const [items, setItems] = useState<any[]>([])
  const [error, setError] = useState('')

  const load = () => apiFetch<any[]>('/approvals').then(setItems).catch((fetchError) => setError(fetchError.message || 'Could not load approvals'))
  useEffect(() => { load() }, [])

  async function decide(id: string, action: string) {
    setError('')
    try {
      await apiFetch(`/approvals/${id}/${action}`, { method: 'POST', body: JSON.stringify({ reason: `${action} from connected frontend demo` }) })
      await load()
    } catch (decisionError: any) {
      setError(decisionError.message || 'Decision failed')
    }
  }

  const counts = useMemo(() => ({
    pending: items.filter((item) => item.status === 'pending').length,
    approved: items.filter((item) => item.status === 'approved').length,
    changes: items.filter((item) => item.status === 'changes_requested').length,
    highestRisk: Math.max(0, ...items.map((item) => Number(item.risk_score || 0))),
  }), [items])

  return <Shell>
    <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
      <div className="grid gap-8 xl:grid-cols-[1.05fr_0.95fr]">
        <div>
          <div className="inline-flex rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-amber-700">Human-in-the-loop review</div>
          <h1 className="font-display mt-4 text-4xl font-semibold tracking-tight text-slate-950">Approval Queue</h1>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-500">This is the business-facing decision lane: reviewers can approve, reject, or request changes without losing sight of risk, reason, or operational impact.</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Card title="Pending decisions" value={counts.pending} caption="Requests waiting on a reviewer before execution can continue." />
          <Card title="Approved items" value={counts.approved} caption="Requests already cleared and allowed to proceed." />
          <Card title="Changes requested" value={counts.changes} caption="Requests sent back for more context or corrective action." />
          <Card title="Highest risk in queue" value={counts.highestRisk} caption="The largest current risk score visible to the reviewer team." />
        </div>
      </div>
    </section>

    {error ? <div className="mt-6"><ErrorState message={error} /></div> : null}

    <div className="mt-8 grid gap-6 xl:grid-cols-[1.28fr_0.72fr]">
      <section>
        {!items.length && !error ? <EmptyState title="No approvals" caption="Start a high-risk workflow to create an approval request." /> : null}
        <div className="space-y-4">
          {items.map((approval) => <div key={approval.id} className="surface-panel-strong rounded-[32px] p-5 lg:p-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="max-w-2xl">
                <div className="inline-flex rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Approval request</div>
                <h2 className="font-display mt-4 text-2xl font-semibold tracking-tight text-slate-950">{approval.title}</h2>
                <p className="mt-3 text-sm leading-7 text-slate-500">{approval.reason}</p>
                {approval.payload?.amount ? <p className="mt-4 text-sm font-medium text-slate-600">Amount in context: ${approval.payload.amount}</p> : null}
              </div>
              <div className="flex flex-wrap gap-2 lg:justify-end">
                <StatusPill status={approval.status} />
                <RiskBadge score={approval.risk_score} />
              </div>
            </div>

            {approval.status === 'pending' ? <div className="mt-5 flex flex-wrap gap-3">
              <button onClick={() => decide(approval.id, 'approve')} className="rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white shadow-[0_18px_40px_rgba(5,150,105,0.18)] transition hover:translate-y-[-1px]">Approve</button>
              <button onClick={() => decide(approval.id, 'reject')} className="rounded-2xl bg-red-600 px-4 py-3 text-sm font-semibold text-white shadow-[0_18px_40px_rgba(220,38,38,0.18)] transition hover:translate-y-[-1px]">Reject</button>
              <button onClick={() => decide(approval.id, 'request-changes')} className="rounded-2xl bg-amber-500 px-4 py-3 text-sm font-semibold text-white shadow-[0_18px_40px_rgba(245,158,11,0.18)] transition hover:translate-y-[-1px]">Request Changes</button>
            </div> : null}
          </div>)}
        </div>
      </section>

      <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
        <div className="inline-flex rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Reviewer guidance</div>
        <h2 className="font-display mt-4 text-2xl font-semibold tracking-tight text-slate-950">Decision checklist</h2>
        <div className="mt-6 space-y-4">
          {[
            'Confirm the business reason for the action is stated clearly and matches the request payload.',
            'Use the risk score as a prioritization input, not a substitute for human judgment.',
            'Request changes when context is missing instead of approving on assumption.',
            'Keep the queue moving by resolving low-risk items quickly and escalating the rest.',
          ].map((item) => <div key={item} className="rounded-[24px] border border-slate-200 bg-white/90 px-4 py-4 text-sm leading-6 text-slate-600 shadow-sm">{item}</div>)}
        </div>
      </section>
    </div>
  </Shell>
}
