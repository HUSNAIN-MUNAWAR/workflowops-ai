'use client'

import { useEffect, useState } from 'react'
import { Shell } from '@/components/Shell'
import { apiFetch } from '@/lib/api'
import { Card, ErrorState, StatusPill } from '@/components/Cards'

export default function Page() {
  const [policy, setPolicy] = useState<any>(null)
  const [decision, setDecision] = useState<any>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    apiFetch('/policies/default').then(setPolicy).catch((fetchError: any) => setError(fetchError.message || 'Login/backend required'))
  }, [])

  async function evalPolicy() {
    setError('')
    try {
      setDecision(await apiFetch('/policies/evaluate', {
        method: 'POST',
        body: JSON.stringify({ action: 'workflow_node', payload: { amount: 5000, risk_score: 72, confidence: 0.62 } }),
      }))
    } catch (evaluationError: any) {
      setError(evaluationError.message || 'Policy evaluation failed')
    }
  }

  return <Shell>
    <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
      <div className="grid gap-8 xl:grid-cols-[1.05fr_0.95fr]">
        <div>
          <div className="inline-flex rounded-full border border-rose-200 bg-rose-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-rose-700">Governance controls</div>
          <h1 className="font-display mt-4 text-4xl font-semibold tracking-tight text-slate-950">Tenant Policy Engine</h1>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-500">The policy engine expresses when automation is allowed, when it must pause for review, and when it should be blocked before risk becomes a production issue.</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Card title="Invoice threshold" value={policy?.invoice_approval_threshold ?? '—'} caption="Amount above which invoice actions require additional scrutiny." />
          <Card title="Risk threshold" value={policy?.risk_review_threshold ?? '—'} caption="Risk score that routes execution to human review." />
          <Card title="Policy mode" value="Audited" caption="Denied and approval-triggered decisions are recorded for traceability." />
          <Card title="Evaluation" value={decision ? 'Captured' : 'Ready'} caption="Run a sample decision to inspect the recommendation payload." />
        </div>
      </div>
    </section>

    {error ? <div className="mt-6"><ErrorState message={error} /></div> : null}

    {policy ? <div className="mt-8 grid gap-6 xl:grid-cols-[0.92fr_1.08fr]">
      <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
        <h2 className="font-display text-2xl font-semibold tracking-tight text-slate-950">Default policy</h2>
        <div className="mt-5 space-y-3">
          <div className="rounded-[24px] border border-slate-200 bg-white/90 p-4 shadow-sm">
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Invoice approval threshold</p>
            <p className="font-display mt-2 text-2xl font-semibold tracking-tight text-slate-950">{policy.invoice_approval_threshold}</p>
          </div>
          <div className="rounded-[24px] border border-slate-200 bg-white/90 p-4 shadow-sm">
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Risk review threshold</p>
            <p className="font-display mt-2 text-2xl font-semibold tracking-tight text-slate-950">{policy.risk_review_threshold}</p>
          </div>
          <div className="rounded-[24px] border border-slate-200 bg-white/90 p-4 text-sm leading-6 text-slate-600 shadow-sm">Only administrators can update the policy. Denied attempts and high-risk decisions are written to the audit trail.</div>
        </div>
      </section>

      <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 className="font-display text-2xl font-semibold tracking-tight text-slate-950">Evaluate sample decision</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">Simulate a high-risk workflow action and inspect the recommended control path.</p>
          </div>
          <button onClick={evalPolicy} className="rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-[0_20px_50px_rgba(15,23,42,0.2)] transition hover:translate-y-[-1px]">Evaluate high-risk invoice</button>
        </div>
        {decision ? <div className="mt-6">
          <div className="flex flex-wrap gap-2">
            <StatusPill status={decision.recommended_action} />
            <span className="rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-xs font-semibold text-slate-600">Risk {decision.risk_score ?? 72}</span>
          </div>
          <div className="mt-5 rounded-[28px] border border-slate-200 bg-slate-950 p-5 text-xs leading-6 text-slate-100">
            <pre className="overflow-auto whitespace-pre-wrap">{JSON.stringify(decision, null, 2)}</pre>
          </div>
        </div> : null}
      </section>
    </div> : <p className="mt-6 text-slate-500">Loading...</p>}
  </Shell>
}
