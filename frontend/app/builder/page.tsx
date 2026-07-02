'use client'

import { useMemo, useState } from 'react'
import { Shell } from '@/components/Shell'
import { Card, ErrorState, StatusPill } from '@/components/Cards'
import { apiFetch } from '@/lib/api'

const sample = {
  nodes: [
    { node_id: 'ingest', node_type: 'ingest_document', name: 'Capture request', depends_on: [] },
    { node_id: 'classify', node_type: 'classify_document', name: 'Classify request type', depends_on: ['ingest'] },
    { node_id: 'extract', node_type: 'extract_fields', name: 'Extract key business fields', depends_on: ['classify'] },
    { node_id: 'policy', node_type: 'policy_check', name: 'Apply governance rules', depends_on: ['extract'] },
    { node_id: 'approval', node_type: 'request_approval', name: 'Route to approver', config: { amount_threshold: 1500 }, depends_on: ['policy'] },
    { node_id: 'connector', node_type: 'connector_action', name: 'Export to destination system', depends_on: ['approval'] },
  ],
  edges: [
    { from: 'ingest', to: 'classify' },
    { from: 'classify', to: 'extract' },
    { from: 'extract', to: 'policy' },
    { from: 'policy', to: 'approval' },
    { from: 'approval', to: 'connector' },
  ],
}

function titleize(value: string) {
  return value.replace(/_/g, ' ').replace(/\b\w/g, (match) => match.toUpperCase())
}

export default function Page() {
  const [text, setText] = useState(JSON.stringify(sample, null, 2))
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const parsed = useMemo(() => {
    try {
      return JSON.parse(text)
    } catch {
      return null
    }
  }, [text])

  const nodes = parsed?.nodes || []
  const edges = parsed?.edges || []
  const approvalNodes = nodes.filter((node: any) => String(node.node_type).includes('approval')).length
  const parseError = parsed ? '' : 'Definition JSON is not valid yet.'

  async function validate() {
    setError('')
    try {
      if (!parsed) {
        setError('Definition JSON is not valid yet.')
        return
      }
      setResult(await apiFetch('/workflow-builder/validate', { method: 'POST', body: JSON.stringify({ definition_json: parsed }) }))
    } catch (validationError: any) {
      setError(validationError.message || 'Validation failed')
    }
  }

  return <Shell>
    <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
      <div className="grid gap-8 xl:grid-cols-[1.05fr_0.95fr]">
        <div>
          <div className="inline-flex rounded-full border border-violet-200 bg-violet-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-violet-700">Design and validation</div>
          <h1 className="font-display mt-4 text-4xl font-semibold tracking-tight text-slate-950">Workflow Builder</h1>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-500">The builder gives technical and non-technical reviewers a shared view of the automation logic: the JSON definition on one side and a readable operational sequence on the other.</p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button onClick={validate} className="rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-[0_20px_50px_rgba(15,23,42,0.2)] transition hover:translate-y-[-1px]">Validate DAG</button>
            <div className="rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 text-sm text-slate-600">Validate persisted graph structure before publication or cloning.</div>
          </div>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Card title="Nodes" value={nodes.length} caption="Discrete automation stages defined in the current JSON." />
          <Card title="Dependencies" value={edges.length} caption="Directed edges that enforce execution order." />
          <Card title="Approval gates" value={approvalNodes} caption="Explicit human checkpoints embedded into the design." />
          <Card title="Validation state" value={result ? (result.valid ? 'Valid' : 'Needs work') : 'Draft'} caption="Live status of the design as checked by the backend validator." />
        </div>
      </div>
    </section>

    {error ? <div className="mt-6"><ErrorState message={error} /></div> : null}

    <div className="mt-8 grid gap-6 xl:grid-cols-[1fr_0.95fr]">
      <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="font-display text-2xl font-semibold tracking-tight text-slate-950">Definition JSON</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">Use a persisted DAG definition with node IDs, types, dependencies, and optional configuration.</p>
          </div>
          <StatusPill status={result ? (result.valid ? 'valid' : 'failed') : (parseError ? 'warning' : 'draft')} />
        </div>
        <textarea
          className="mt-5 h-[580px] w-full rounded-[28px] border border-slate-200 bg-slate-950 p-5 font-mono text-xs leading-6 text-slate-100 shadow-inner outline-none transition focus:border-cyan-400"
          value={text}
          onChange={(event) => setText(event.target.value)}
        />
      </section>

      <section className="space-y-6">
        <div className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
          <h2 className="font-display text-2xl font-semibold tracking-tight text-slate-950">Flow preview</h2>
          <p className="mt-2 text-sm leading-6 text-slate-500">A human-readable view of the current node order, dependency chain, and control points.</p>
          <div className="mt-6 space-y-3">
            {nodes.map((node: any, index: number) => <div key={node.node_id} className="rounded-[24px] border border-slate-200 bg-white/90 p-4 shadow-sm">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Stage {index + 1}</p>
                  <h3 className="font-display mt-2 text-xl font-semibold tracking-tight text-slate-950">{node.name || titleize(node.node_id)}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-500">Depends on {(node.depends_on || []).join(', ') || 'entry conditions only'}.</p>
                </div>
                <StatusPill status={node.node_type} />
              </div>
            </div>)}
          </div>
        </div>

        <div className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
          <div className="flex items-center justify-between gap-3">
            <h2 className="font-display text-2xl font-semibold tracking-tight text-slate-950">Validation result</h2>
            {result ? <StatusPill status={result.valid ? 'passed' : 'failed'} /> : null}
          </div>
          <div className="mt-5 rounded-[28px] border border-slate-200 bg-slate-950 p-5 text-xs leading-6 text-slate-100">
            <pre className="overflow-auto whitespace-pre-wrap">{JSON.stringify(result || { valid: false, note: 'Run validation to receive backend feedback.' }, null, 2)}</pre>
          </div>
        </div>
      </section>
    </div>
  </Shell>
}
