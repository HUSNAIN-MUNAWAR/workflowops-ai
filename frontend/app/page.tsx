import Link from 'next/link'
import { AutomationCanvas } from '@/components/AutomationCanvas'

export default function LandingPage() {
  return <main className="min-h-screen px-4 py-5 sm:px-6 lg:px-8">
    <section className="surface-panel-strong mx-auto max-w-[1680px] overflow-hidden rounded-[40px] border border-white/70 bg-[#081321] text-white shadow-[0_35px_120px_rgba(2,6,23,0.34)]">
      <div className="relative px-6 py-8 sm:px-8 lg:px-10 lg:py-10">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.18),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(245,158,11,0.16),transparent_24%)]" />
        <div className="relative">
          <div className="flex flex-col gap-10 xl:grid xl:grid-cols-[1.05fr_0.95fr]">
            <div className="max-w-3xl">
              <div className="inline-flex rounded-full border border-cyan-300/30 bg-cyan-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-cyan-100">Governed automation workspace</div>
              <h1 className="font-display mt-8 text-5xl font-semibold tracking-tight text-white sm:text-6xl">Operational automation that non-technical teams can trust and actually use.</h1>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">WorkflowOps AI brings intake, policy decisions, approvals, connector controls, reports, and audit evidence into one clear operating surface for finance, compliance, procurement, and service teams.</p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link href="/login" className="rounded-2xl bg-white px-5 py-3 text-sm font-semibold text-slate-950 shadow-lg transition hover:translate-y-[-1px]">Open demo workspace</Link>
                <Link href="/dashboard" className="rounded-2xl border border-white/15 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10">View operations dashboard</Link>
              </div>
              <div className="mt-10 grid gap-4 sm:grid-cols-3">
                {[
                  ['6 workflow templates', 'Finance, support, compliance, RFP, inbox, and reliability flows'],
                  ['Approval checkpoints', 'Human review stays visible for sensitive workflow actions'],
                  ['Evidence outputs', 'Reports, audit logs, metrics, and run timelines remain traceable'],
                ].map(([title, caption]) => <div key={title} className="rounded-[26px] border border-white/10 bg-white/6 p-5 backdrop-blur-sm">
                  <p className="font-display text-xl font-semibold text-white">{title}</p>
                  <p className="mt-3 text-sm leading-6 text-slate-300">{caption}</p>
                </div>)}
              </div>
            </div>

            <div className="rounded-[34px] border border-white/10 bg-white/7 p-3 backdrop-blur-sm">
              <AutomationCanvas
                title="Business-friendly automation flow"
                caption="The interface keeps the workflow understandable: what came in, what was extracted, what policy decided, who approved it, what connector touched it, and which report proves it."
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
}
