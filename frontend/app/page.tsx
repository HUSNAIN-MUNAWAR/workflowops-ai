import Link from 'next/link'

export default function LandingPage() {
  return <main className="min-h-screen bg-slate-950 text-white">
    <section className="mx-auto max-w-6xl px-6 py-24">
      <div className="inline-flex rounded-full border border-cyan-300/30 px-4 py-2 text-sm text-cyan-200">Governed AI workflow automation demo</div>
      <h1 className="mt-8 max-w-4xl text-6xl font-bold tracking-tight">Turn messy business inputs into safe, auditable, human-approved workflows.</h1>
      <p className="mt-6 max-w-3xl text-lg text-slate-300">WorkflowOps AI handles invoices, inboxes, RFPs, compliance evidence, and support escalations with approval gates, audit logs, replay, and reliability testing.</p>
      <div className="mt-10 flex gap-4">
        <Link href="/login" className="rounded-xl bg-white px-5 py-3 font-semibold text-slate-950">Demo login</Link>
        <Link href="/dashboard" className="rounded-xl border border-white/20 px-5 py-3 font-semibold">Open dashboard</Link>
      </div>
      <div className="mt-16 grid grid-cols-3 gap-4 text-sm text-slate-300">
        {['Human-in-the-loop approvals', 'Audit-ready report packs', 'workflow_evalbench reliability tests'].map(item => <div className="rounded-2xl border border-white/10 bg-white/5 p-5" key={item}>{item}</div>)}
      </div>
    </section>
  </main>
}
