export function Card({ title, value, caption }: { title: string; value: string | number; caption?: string }) {
  return <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
    <p className="text-sm text-slate-500">{title}</p>
    <p className="mt-2 text-3xl font-semibold text-slate-950">{value}</p>
    {caption ? <p className="mt-2 text-xs text-slate-500">{caption}</p> : null}
  </div>
}

export function RiskBadge({ score, value }: { score?: number; value?: number }) {
  score = score ?? value ?? 0
  const label = score >= 70 ? 'High' : score >= 40 ? 'Medium' : 'Low'
  const cls = score >= 70 ? 'bg-red-50 text-red-700 ring-red-200' : score >= 40 ? 'bg-amber-50 text-amber-700 ring-amber-200' : 'bg-emerald-50 text-emerald-700 ring-emerald-200'
  return <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${cls}`}>{label} {score}</span>
}

export function StatusPill({ status }: { status: string }) {
  const cls = status.includes('fail') || status === 'rejected' ? 'bg-red-50 text-red-700' : status.includes('approval') || status === 'pending' ? 'bg-amber-50 text-amber-700' : status === 'completed' || status === 'approved' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-700'
  return <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${cls}`}>{status}</span>
}

export function EmptyState({ title, caption }: { title: string; caption: string }) {
  return <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
    <h3 className="font-semibold text-slate-900">{title}</h3>
    <p className="mt-2 text-sm text-slate-500">{caption}</p>
  </div>
}

export function ErrorState({ message }: { message: string }) {
  return <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{message}</div>
}
