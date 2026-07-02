import { StatusPill } from './Cards'

export function WorkflowTimeline({ steps }: { steps: Array<{ node_id: string; node_type: string; status: string; duration_ms?: number; error_message?: string | null }> }) {
  if (!steps.length) return <div className="text-sm text-slate-500">No timeline steps yet.</div>
  return <div className="relative space-y-3 before:absolute before:bottom-5 before:left-[15px] before:top-5 before:w-px before:bg-gradient-to-b before:from-cyan-300 before:via-slate-200 before:to-transparent">
    {steps.map((step, idx) => <div key={`${step.node_id}-${idx}`} className="relative ml-8 rounded-[24px] border border-slate-200 bg-white/92 p-4 shadow-sm">
      <div className="absolute -left-8 top-5 h-4 w-4 rounded-full border-4 border-cyan-100 bg-cyan-500 shadow-sm" />
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="font-display text-lg font-semibold tracking-tight text-slate-900">{step.node_id}</p>
          <p className="mt-1 text-xs uppercase tracking-[0.22em] text-slate-400">{step.node_type}</p>
          <p className="mt-3 text-sm text-slate-500">Execution time: {step.duration_ms ?? 0} ms</p>
        </div>
        <StatusPill status={step.status} />
      </div>
      {step.error_message ? <p className="mt-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{step.error_message}</p> : null}
    </div>)}
  </div>
}
