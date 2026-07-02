'use client'

import { useEffect, useMemo, useState } from 'react'
import { Shell } from '@/components/Shell'
import { Card, EmptyState, ErrorState, RiskBadge, StatusPill } from '@/components/Cards'
import { WorkflowTimeline } from '@/components/WorkflowTimeline'
import { apiFetch } from '@/lib/api'

const presets: Record<string, { label: string; text: string; actionType: string }> = {
  invoice_approval: {
    label: 'Invoice Approval',
    actionType: 'payment_export',
    text: 'Invoice Number: INV-UI-1\nVendor: Acme Supplies\nTotal: USD 7200\nDue Date: 2026-08-15\nPayment export requested',
  },
  email_to_task: {
    label: 'Email to Task',
    actionType: 'internal',
    text: 'Subject: Security questionnaire follow-up\nRequester: Northwind Power\nNeed a task for the security team to finish the customer response before Friday.',
  },
  rfp_response: {
    label: 'RFP Response',
    actionType: 'internal',
    text: 'Prepare a proposal compliance matrix for a public-sector procurement with mandatory controls, pricing sheet, and security review.',
  },
  support_escalation: {
    label: 'Support Escalation',
    actionType: 'internal',
    text: 'Enterprise customer reports an outage affecting order routing, demands executive visibility, and needs incident follow-up within 30 minutes.',
  },
}

export default function RunConsole() {
  const [template, setTemplate] = useState('invoice_approval')
  const [text, setText] = useState(presets.invoice_approval.text)
  const [run, setRun] = useState<any>(null)
  const [steps, setSteps] = useState<any[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setText(presets[template].text)
  }, [template])

  async function start() {
    setLoading(true)
    setError('')
    try {
      const createdRun = await apiFetch<any>('/workflow-runs', {
        method: 'POST',
        body: JSON.stringify({
          template_slug: template,
          input_payload: { text, action_type: presets[template].actionType },
          simulation_mode: false,
        }),
      })
      setRun(createdRun)
      setSteps(await apiFetch<any[]>(`/workflow-runs/${createdRun.id}/timeline`))
    } catch (runError: any) {
      setError(runError.message || 'Failed')
    } finally {
      setLoading(false)
    }
  }

  const runSummary = useMemo(() => ({
    currentStep: run?.current_step || 'Awaiting execution',
    score: run?.risk_score ?? 0,
    timelineCount: steps.length,
  }), [run, steps])

  return <Shell>
    <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
      <div className="grid gap-8 xl:grid-cols-[1.05fr_0.95fr]">
        <div>
          <div className="inline-flex rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-sky-700">Live orchestration</div>
          <h1 className="font-display mt-4 text-4xl font-semibold tracking-tight text-slate-950">Run Console</h1>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-500">The run console is the operator surface for launching a real workflow, inspecting risk posture, and following each persisted step through the automation timeline.</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Card title="Selected template" value={presets[template].label} caption="Workflow family currently configured for launch." />
          <Card title="Action type" value={presets[template].actionType} caption="Connector intent sent with the current input payload." />
          <Card title="Risk score" value={run ? runSummary.score : '—'} caption="Risk score emitted by the most recent workflow run." />
          <Card title="Timeline events" value={run ? runSummary.timelineCount : '—'} caption="Persisted steps currently available for the selected run." />
        </div>
      </div>
    </section>

    {error ? <div className="mt-6"><ErrorState message={error} /></div> : null}

    <div className="mt-8 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
      <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
        <label className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">Template</label>
        <select className="mt-3 w-full rounded-[22px] border border-slate-200 bg-white/90 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-cyan-400" value={template} onChange={(event) => setTemplate(event.target.value)}>
          {Object.entries(presets).map(([value, preset]) => <option key={value} value={value}>{preset.label}</option>)}
        </select>

        <label className="mt-6 block text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">Input text</label>
        <textarea className="mt-3 h-[360px] w-full rounded-[28px] border border-slate-200 bg-white/90 p-5 font-mono text-sm leading-6 text-slate-700 outline-none transition focus:border-cyan-400" value={text} onChange={(event) => setText(event.target.value)} />

        <button onClick={start} className="mt-5 rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-[0_20px_50px_rgba(15,23,42,0.2)] transition hover:translate-y-[-1px]">{loading ? 'Running...' : 'Start Workflow'}</button>
      </section>

      <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
        <h2 className="font-display text-2xl font-semibold tracking-tight text-slate-950">Run output</h2>
        {run ? <div className="mt-5">
          <div className="flex flex-wrap gap-2">
            <StatusPill status={run.status} />
            <RiskBadge score={run.risk_score} />
            <span className="rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-xs font-semibold text-slate-600">{run.current_step || 'Awaiting timeline'}</span>
          </div>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <div className="rounded-[24px] border border-slate-200 bg-white/90 p-4 shadow-sm">
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Run ID</p>
              <p className="mt-2 break-all text-sm font-medium text-slate-700">{run.id}</p>
            </div>
            <div className="rounded-[24px] border border-slate-200 bg-white/90 p-4 shadow-sm">
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Current step</p>
              <p className="font-display mt-2 text-xl font-semibold tracking-tight text-slate-950">{runSummary.currentStep}</p>
            </div>
          </div>
          <div className="mt-7">
            <WorkflowTimeline steps={steps} />
          </div>
        </div> : <div className="mt-5"><EmptyState title="No run yet" caption="Launch a workflow to create persisted run records and timeline steps." /></div>}
      </section>
    </div>
  </Shell>
}
