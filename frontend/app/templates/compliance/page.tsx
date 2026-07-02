import { Shell } from '@/components/Shell'
import { RiskBadge } from '@/components/Cards'

const steps = ['Input ingestion', 'Classification', 'Extraction', 'Validation', 'Risk score', 'Approval gate', 'Execution/export', 'Audit report']

export default function TemplatePage() {
  return <Shell>
    <h1 className="text-3xl font-bold">Compliance Evidence Automation</h1>
    <p className="mt-2 text-slate-600">Template demo with workflow graph, extracted fields, task list, approval step, risk score, and output report.</p>
    <div className="mt-8 grid grid-cols-3 gap-6">
      <section className="col-span-2 rounded-2xl bg-white p-6 shadow-soft border border-slate-200">
        <h2 className="text-xl font-semibold">Workflow graph</h2>
        <div className="mt-5 flex flex-wrap gap-3">{steps.map(s => <span key={s} className="rounded-xl border bg-slate-50 px-3 py-2 text-sm">{s}</span>)}</div>
      </section>
      <aside className="rounded-2xl bg-white p-6 shadow-soft border border-slate-200">
        <h2 className="text-xl font-semibold">Risk score</h2>
        <p className="mt-4"><RiskBadge value={76} /></p>
        <button className="mt-6 rounded-xl bg-slate-950 px-4 py-2 text-white">Download sample report</button>
      </aside>
    </div>
    <div className="mt-6 grid grid-cols-3 gap-6">
      <div className="rounded-2xl bg-white p-6 shadow-soft border border-slate-200"><h3 className="font-semibold">Extracted fields</h3><pre className="mt-3 text-xs">{JSON.stringify({ vendor: 'Acme Supplies', amount: 1200, status: 'needs_review' }, null, 2)}</pre></div>
      <div className="rounded-2xl bg-white p-6 shadow-soft border border-slate-200"><h3 className="font-semibold">Task list</h3><p className="mt-3 text-sm">Reviewer task, exception task, report export task.</p></div>
      <div className="rounded-2xl bg-white p-6 shadow-soft border border-slate-200"><h3 className="font-semibold">Failure replay</h3><p className="mt-3 text-sm">Replay viewer shows deterministic node events and guard decisions.</p></div>
    </div>
  </Shell>
}
