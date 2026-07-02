'use client'

import { useEffect, useMemo, useState } from 'react'
import Link from 'next/link'
import { Shell } from '@/components/Shell'
import { Card, EmptyState, ErrorState, RiskBadge, StatusPill } from '@/components/Cards'
import { apiFetch } from '@/lib/api'

function titleize(value: string) {
  return value.replace(/_/g, ' ').replace(/\b\w/g, (match) => match.toUpperCase())
}

export default function TemplatesPage() {
  const [items, setItems] = useState<any[]>([])
  const [selectedId, setSelectedId] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    apiFetch<any[]>('/workflow-templates')
      .then((rows) => {
        setItems(rows)
        setSelectedId((current) => current || rows[0]?.id || '')
      })
      .catch((fetchError) => setError(fetchError.message || 'Could not load templates'))
  }, [])

  const selected = useMemo(
    () => items.find((item) => item.id === selectedId) || items[0] || null,
    [items, selectedId],
  )

  const metrics = useMemo(() => {
    const nodeCounts = items.map((item) => item.definition_json?.nodes?.length || 0)
    return {
      total: items.length,
      reviewGated: items.filter((item) => (item.definition_json?.nodes || []).some((node: any) => String(node.node_type).includes('approval'))).length,
      highestRisk: Math.max(0, ...items.map((item) => Number(item.risk_threshold || 0))),
      averageNodes: nodeCounts.length ? (nodeCounts.reduce((sum, value) => sum + value, 0) / nodeCounts.length).toFixed(1) : '0.0',
    }
  }, [items])

  const selectedNodes = selected?.definition_json?.nodes || []
  const selectedEdges = selected?.definition_json?.edges || []

  return <Shell>
    <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
      <div className="grid gap-8 xl:grid-cols-[1.05fr_0.95fr]">
        <div>
          <div className="inline-flex rounded-full border border-cyan-200 bg-cyan-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-cyan-700">Operational blueprint library</div>
          <h1 className="font-display mt-4 text-4xl font-semibold tracking-tight text-slate-950">Workflow Template Marketplace</h1>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-500">Each template is a reusable automation lane with explicit steps, human-review checkpoints, and risk thresholds that operators can understand without reading backend code.</p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/builder" className="rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-[0_20px_50px_rgba(15,23,42,0.2)] transition hover:translate-y-[-1px]">Open builder</Link>
            <Link href="/run-console" className="rounded-2xl border border-slate-200 bg-white/90 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-white">Launch a run</Link>
          </div>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Card title="Template families" value={metrics.total} caption="Reusable workflows currently available to the workspace." />
          <Card title="Review-gated" value={metrics.reviewGated} caption="Templates that include explicit human approval checkpoints." />
          <Card title="Average stages" value={metrics.averageNodes} caption="Average number of steps inside each automation design." />
          <Card title="Highest risk threshold" value={metrics.highestRisk} caption="Largest configured risk score before a template demands scrutiny." />
        </div>
      </div>
    </section>

    {error ? <div className="mt-6"><ErrorState message={error} /></div> : null}
    {!error && !items.length ? <div className="mt-8"><EmptyState title="No templates" caption="Run the seed script or backend startup seed to populate the template library." /></div> : null}

    <div className="mt-8 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <section className="space-y-4">
        {items.map((template) => {
          const isSelected = template.id === selected?.id
          const nodeCount = template.definition_json?.nodes?.length || 0
          return <button
            key={template.id}
            type="button"
            onClick={() => setSelectedId(template.id)}
            className={`surface-panel-strong block w-full rounded-[30px] p-5 text-left transition ${isSelected ? 'border-cyan-300 shadow-[0_34px_90px_rgba(8,145,178,0.18)]' : 'hover:translate-y-[-1px]'}`}
          >
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="max-w-2xl">
                <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-400">{template.slug}</p>
                <h2 className="font-display mt-3 text-2xl font-semibold tracking-tight text-slate-950">{template.name}</h2>
                <p className="mt-3 text-sm leading-7 text-slate-500">{template.description}</p>
              </div>
              <div className="flex flex-wrap gap-2 lg:justify-end">
                <StatusPill status={template.is_active ? 'active' : 'draft'} />
                <RiskBadge score={template.risk_threshold} />
              </div>
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              <div className="rounded-[22px] border border-slate-200 bg-white/90 px-4 py-4 shadow-sm">
                <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Version</p>
                <p className="font-display mt-2 text-xl font-semibold text-slate-950">{template.version}</p>
              </div>
              <div className="rounded-[22px] border border-slate-200 bg-white/90 px-4 py-4 shadow-sm">
                <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Workflow stages</p>
                <p className="font-display mt-2 text-xl font-semibold text-slate-950">{nodeCount}</p>
              </div>
              <div className="rounded-[22px] border border-slate-200 bg-white/90 px-4 py-4 shadow-sm">
                <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Dependencies</p>
                <p className="font-display mt-2 text-xl font-semibold text-slate-950">{template.definition_json?.edges?.length || 0}</p>
              </div>
            </div>
          </button>
        })}
      </section>

      <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
        {selected ? <>
          <div className="inline-flex rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Selected template</div>
          <h2 className="font-display mt-4 text-3xl font-semibold tracking-tight text-slate-950">{selected.name}</h2>
          <p className="mt-3 text-sm leading-7 text-slate-500">{selected.description}</p>
          <div className="mt-5 flex flex-wrap gap-2">
            <span className="rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-xs font-semibold text-slate-600">{selected.slug}</span>
            <StatusPill status={selected.is_active ? 'active' : 'draft'} />
            <RiskBadge score={selected.risk_threshold} />
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <div className="rounded-[24px] border border-slate-200 bg-white/90 p-4 shadow-sm">
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Execution graph</p>
              <p className="font-display mt-2 text-2xl font-semibold tracking-tight text-slate-950">{selectedNodes.length} nodes</p>
              <p className="mt-2 text-sm leading-6 text-slate-500">{selectedEdges.length} dependencies are persisted for orchestrated execution.</p>
            </div>
            <div className="rounded-[24px] border border-slate-200 bg-white/90 p-4 shadow-sm">
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Business posture</p>
              <p className="font-display mt-2 text-2xl font-semibold tracking-tight text-slate-950">{selected.risk_threshold}+ review</p>
              <p className="mt-2 text-sm leading-6 text-slate-500">Sensitive actions are routed to people once the risk threshold is reached.</p>
            </div>
          </div>

          <div className="mt-7">
            <div className="flex items-center justify-between gap-3">
              <h3 className="font-display text-2xl font-semibold tracking-tight text-slate-950">Execution stages</h3>
              <Link href="/builder" className="text-sm font-semibold text-cyan-700 transition hover:text-cyan-800">Refine in builder</Link>
            </div>
            <div className="mt-5 space-y-3">
              {selectedNodes.map((node: any, index: number) => <div key={node.node_id} className="rounded-[24px] border border-slate-200 bg-white/90 p-4 shadow-sm">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Stage {index + 1}</p>
                    <h4 className="font-display mt-2 text-xl font-semibold tracking-tight text-slate-950">{node.name || titleize(node.node_id)}</h4>
                    <p className="mt-2 text-sm leading-6 text-slate-500">{titleize(node.node_type)} with dependencies on {(node.depends_on || []).join(', ') || 'entry conditions only'}.</p>
                  </div>
                  <StatusPill status={node.node_type} />
                </div>
              </div>)}
            </div>
          </div>
        </> : <EmptyState title="No template selected" caption="Choose a template from the marketplace to inspect its automation stages." />}
      </section>
    </div>
  </Shell>
}
