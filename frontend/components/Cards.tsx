function humanize(text: string) {
  return text.replace(/_/g, ' ').replace(/\b\w/g, (match) => match.toUpperCase())
}

export function Card({ title, value, caption }: { title: string; value: string | number; caption?: string }) {
  return <div className="surface-panel rounded-[28px] p-5">
    <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">{title}</p>
    <p className="font-display mt-3 text-4xl font-semibold tracking-tight text-slate-950">{value}</p>
    {caption ? <p className="mt-3 max-w-[18rem] text-sm leading-6 text-slate-500">{caption}</p> : null}
  </div>
}

export function RiskBadge({ score, value }: { score?: number; value?: number }) {
  score = score ?? value ?? 0
  const label = score >= 70 ? 'High' : score >= 40 ? 'Medium' : 'Low'
  const cls = score >= 70 ? 'border-red-200 bg-red-50/90 text-red-700' : score >= 40 ? 'border-amber-200 bg-amber-50/90 text-amber-700' : 'border-emerald-200 bg-emerald-50/90 text-emerald-700'
  return <span className={`inline-flex items-center gap-1 rounded-full border px-3 py-1 text-xs font-semibold shadow-sm ${cls}`}>{label}<span className="opacity-75">{score}</span></span>
}

export function StatusPill({ status }: { status: string }) {
  const cls = status.includes('fail') || status === 'rejected' || status === 'blocked' || status === 'denied'
    ? 'border-red-200 bg-red-50/90 text-red-700'
    : status.includes('approval') || status === 'pending' || status === 'changes_requested' || status === 'requires_review' || status === 'warning'
      ? 'border-amber-200 bg-amber-50/90 text-amber-700'
      : status === 'completed' || status === 'approved' || status === 'passed' || status === 'active' || status === 'healthy' || status === 'ready' || status === 'published' || status === 'valid'
        ? 'border-emerald-200 bg-emerald-50/90 text-emerald-700'
        : 'border-slate-200 bg-slate-100/90 text-slate-700'
  return <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold shadow-sm ${cls}`}>{humanize(status)}</span>
}

export function EmptyState({ title, caption }: { title: string; caption: string }) {
  return <div className="surface-panel rounded-[30px] border-dashed p-8 text-center">
    <h3 className="font-display text-xl font-semibold text-slate-900">{title}</h3>
    <p className="mt-3 text-sm leading-6 text-slate-500">{caption}</p>
  </div>
}

export function ErrorState({ message }: { message: string }) {
  return <div className="rounded-[24px] border border-red-200 bg-red-50/90 p-4 text-sm leading-6 text-red-700 shadow-sm">{message}</div>
}
