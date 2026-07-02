import { StatusPill } from './Cards'

export function WorkflowTimeline({ steps }: { steps: Array<{ node_id: string; node_type: string; status: string; duration_ms?: number; error_message?: string | null }> }) {
  if (!steps.length) return <div className="text-sm text-slate-500">No timeline steps yet.</div>
  return <div className="space-y-3">
    {steps.map((step, idx) => <div key={`${step.node_id}-${idx}`} className="rounded-2xl border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between">
        <div><p className="font-semibold text-slate-900">{step.node_id}</p><p className="text-xs text-slate-500">{step.node_type} · {step.duration_ms ?? 0} ms</p></div>
        <StatusPill status={step.status} />
      </div>
      {step.error_message ? <p className="mt-2 text-sm text-red-600">{step.error_message}</p> : null}
    </div>)}
  </div>
}
