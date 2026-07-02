'use client'

import { useEffect, useMemo, useState } from 'react'
import { Shell } from '@/components/Shell'
import { Card, EmptyState, ErrorState, RiskBadge, StatusPill } from '@/components/Cards'
import { apiFetch } from '@/lib/api'

function titleize(value: string) {
  return value.replace(/_/g, ' ').replace(/\b\w/g, (match) => match.toUpperCase())
}

export default function Reliability() {
  const [runs, setRuns] = useState<any[]>([])
  const [detail, setDetail] = useState<any>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function openRun(id: string) {
    setDetail(await apiFetch(`/reliability-tests/${id}`))
  }

  async function load(initialSelection = true) {
    try {
      const rows = await apiFetch<any[]>('/reliability-tests')
      setRuns(rows)
      if (initialSelection && rows[0]) await openRun(rows[0].id)
    } catch (fetchError: any) {
      setError(fetchError.message || 'Could not load reliability runs')
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function start() {
    setLoading(true)
    setError('')
    try {
      const run = await apiFetch<any>('/reliability-tests/run', { method: 'POST', body: JSON.stringify({ template_slug: 'invoice_approval' }) })
      await load(false)
      await openRun(run.id)
    } catch (runError: any) {
      setError(runError.message || 'Run failed')
    } finally {
      setLoading(false)
    }
  }

  const metrics = useMemo(() => {
    const reliabilityScores = runs.map((run) => Number(run.reliability_score || 0))
    const safetyScores = runs.map((run) => Number(run.safety_score || 0))
    return {
      total: runs.length,
      averageReliability: reliabilityScores.length ? Math.round(reliabilityScores.reduce((sum, value) => sum + value, 0) / reliabilityScores.length) : 0,
      averageSafety: safetyScores.length ? Math.round(safetyScores.reduce((sum, value) => sum + value, 0) / safetyScores.length) : 0,
      openFailures: runs.reduce((sum, run) => sum + Number(run.failed_cases || 0), 0),
    }
  }, [runs])

  return <Shell>
    <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
      <div className="grid gap-8 xl:grid-cols-[1.05fr_0.95fr]">
        <div>
          <div className="inline-flex rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-emerald-700">Reliability and safeguards</div>
          <h1 className="font-display mt-4 text-4xl font-semibold tracking-tight text-slate-950">Workflow EvalBench</h1>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-500">The reliability workspace makes synthetic stress testing understandable for operators: which workflow was tested, how it behaved, where it failed, and what mitigation should happen next.</p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button onClick={start} className="rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-[0_20px_50px_rgba(15,23,42,0.2)] transition hover:translate-y-[-1px]">{loading ? 'Running...' : 'Run Reliability Tests'}</button>
            <div className="rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 text-sm text-slate-600">Synthetic adversarial scenarios with replay logs and report generation.</div>
          </div>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Card title="Recorded runs" value={metrics.total} caption="Reliability sessions already persisted in the demo environment." />
          <Card title="Average reliability" value={`${metrics.averageReliability}%`} caption="Average resilience score across the available run history." />
          <Card title="Average safety" value={`${metrics.averageSafety}%`} caption="Average safeguard score across simulated scenarios." />
          <Card title="Failed cases" value={metrics.openFailures} caption="Total number of scenario failures found across the current history." />
        </div>
      </div>
    </section>

    {error ? <div className="mt-6"><ErrorState message={error} /></div> : null}

    <div className="mt-8 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
      <section className="space-y-4">
        {!runs.length && !error ? <EmptyState title="No reliability runs yet" caption="Start a test run to populate scenario results, replay evidence, and generated reports." /> : null}
        {runs.map((run) => {
          const isSelected = detail?.run?.id === run.id
          return <button
            key={run.id}
            type="button"
            onClick={() => openRun(run.id)}
            className={`surface-panel-strong block w-full rounded-[30px] p-5 text-left transition ${isSelected ? 'border-emerald-300 shadow-[0_34px_90px_rgba(5,150,105,0.18)]' : 'hover:translate-y-[-1px]'}`}
          >
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="font-mono text-xs text-slate-400">{run.workflow_template_slug}</p>
                <h2 className="font-display mt-2 text-2xl font-semibold tracking-tight text-slate-950">{titleize(run.workflow_template_slug)}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-500">Synthetic benchmark run with persisted case evidence and downloadable report formats.</p>
              </div>
              <StatusPill status={run.status} />
            </div>
            <div className="mt-5 flex flex-wrap items-center gap-3">
              <RiskBadge score={run.reliability_score} />
              <span className="rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-xs font-semibold text-slate-600">Safety {run.safety_score}</span>
              <span className="rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-xs font-semibold text-slate-600">{run.failed_cases} failed cases</span>
            </div>
          </button>
        })}
      </section>

      <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
        {detail?.run ? <>
          <div className="inline-flex rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Selected reliability run</div>
          <h2 className="font-display mt-4 text-3xl font-semibold tracking-tight text-slate-950">{titleize(detail.run.workflow_template_slug)}</h2>
          <div className="mt-5 flex flex-wrap gap-2">
            <StatusPill status={detail.run.status} />
            <RiskBadge score={detail.run.reliability_score} />
            <span className="rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-xs font-semibold text-slate-600">Safety {detail.run.safety_score}</span>
            <span className="rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-xs font-semibold text-slate-600">{detail.cases?.length || 0} scenarios</span>
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            <div className="rounded-[24px] border border-slate-200 bg-white/90 p-4 shadow-sm">
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Run posture</p>
              <p className="font-display mt-2 text-2xl font-semibold tracking-tight text-slate-950">{detail.run.reliability_score}%</p>
              <p className="mt-2 text-sm leading-6 text-slate-500">Reliability score for the chosen workflow lane.</p>
            </div>
            <div className="rounded-[24px] border border-slate-200 bg-white/90 p-4 shadow-sm">
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Risk findings</p>
              <p className="font-display mt-2 text-2xl font-semibold tracking-tight text-slate-950">{detail.run.failed_cases}</p>
              <p className="mt-2 text-sm leading-6 text-slate-500">Scenarios that need fallback logic, controls, or operator review.</p>
            </div>
            <div className="rounded-[24px] border border-slate-200 bg-white/90 p-4 shadow-sm">
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Passing scenarios</p>
              <p className="font-display mt-2 text-2xl font-semibold tracking-tight text-slate-950">{detail.cases?.filter((testCase: any) => testCase.passed).length || 0}</p>
              <p className="mt-2 text-sm leading-6 text-slate-500">Scenarios that completed with the expected safeguards and fallback behavior.</p>
            </div>
          </div>

          <div className="mt-7">
            <h3 className="font-display text-2xl font-semibold tracking-tight text-slate-950">Case results</h3>
            <div className="mt-5 space-y-3">
              {detail.cases?.map((testCase: any) => <div key={testCase.id} className="rounded-[24px] border border-slate-200 bg-white/90 p-4 shadow-sm">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h4 className="font-display text-xl font-semibold tracking-tight text-slate-950">{testCase.test_name}</h4>
                    <p className="mt-2 text-sm leading-6 text-slate-500">{testCase.scenario_type} scenario with {testCase.severity} severity.</p>
                  </div>
                  <StatusPill status={testCase.passed ? 'passed' : 'failed'} />
                </div>
                <p className="mt-4 rounded-[20px] border border-slate-200 bg-slate-50/80 px-4 py-3 text-sm leading-6 text-slate-600">{testCase.mitigation_recommendation}</p>
              </div>)}
            </div>
          </div>
        </> : <EmptyState title="No run selected" caption="Choose a reliability run from the list to inspect the scenario outcomes." />}
      </section>
    </div>
  </Shell>
}
