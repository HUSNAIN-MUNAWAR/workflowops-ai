type AutomationCanvasProps = {
  title?: string
  caption?: string
  pendingApprovals?: number
  reliabilityScore?: number
  reportCount?: number
}

const desktopNodes = [
  { title: 'Ingest', subtitle: 'Email, invoice, PDF, or ticket intake', tone: 'sky', x: '4%', y: '10%' },
  { title: 'Extract', subtitle: 'Classification, OCR, and field capture', tone: 'emerald', x: '28%', y: '10%' },
  { title: 'Policy Engine', subtitle: 'Risk, budget, role, and action checks', tone: 'amber', x: '52%', y: '10%' },
  { title: 'Human Review', subtitle: 'Approval gates for sensitive actions', tone: 'rose', x: '73%', y: '34%' },
  { title: 'Connector Action', subtitle: 'Safe local connector execution', tone: 'violet', x: '76%', y: '10%' },
  { title: 'Audit and Reports', subtitle: 'Timeline, exports, and evidence trail', tone: 'slate', x: '44%', y: '60%' },
] as const

const toneClasses: Record<string, string> = {
  sky: 'border-sky-200 bg-sky-50/90 text-sky-900',
  emerald: 'border-emerald-200 bg-emerald-50/90 text-emerald-900',
  amber: 'border-amber-200 bg-amber-50/90 text-amber-900',
  rose: 'border-rose-200 bg-rose-50/90 text-rose-900',
  violet: 'border-violet-200 bg-violet-50/90 text-violet-900',
  slate: 'border-slate-200 bg-slate-50/90 text-slate-900',
}

function DesktopLine({ style }: { style: React.CSSProperties }) {
  return <div className="absolute rounded-full bg-gradient-to-r from-sky-300 via-cyan-300 to-amber-300 opacity-80 shadow-[0_0_24px_rgba(34,211,238,0.28)]" style={style} />
}

export function AutomationCanvas({
  title = 'Automation control map',
  caption = 'A client-facing view of how intake, policy, approvals, execution, and reporting are connected.',
  pendingApprovals = 2,
  reliabilityScore = 92,
  reportCount = 6,
}: AutomationCanvasProps) {
  return <div className="surface-panel-strong overflow-hidden rounded-[34px] p-6 lg:p-7">
    <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <div className="inline-flex rounded-full border border-slate-200 bg-white/80 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Automation Map</div>
        <h2 className="font-display mt-4 text-2xl font-semibold tracking-tight text-slate-950">{title}</h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">{caption}</p>
      </div>
      <div className="grid grid-cols-3 gap-3 text-left">
        <div className="rounded-2xl border border-slate-200 bg-white/85 px-4 py-3 shadow-sm">
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">Approvals</p>
          <p className="font-display mt-2 text-2xl font-semibold text-slate-950">{pendingApprovals}</p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white/85 px-4 py-3 shadow-sm">
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">Reliability</p>
          <p className="font-display mt-2 text-2xl font-semibold text-slate-950">{reliabilityScore}%</p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white/85 px-4 py-3 shadow-sm">
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">Reports</p>
          <p className="font-display mt-2 text-2xl font-semibold text-slate-950">{reportCount}</p>
        </div>
      </div>
    </div>

    <div className="relative mt-6 overflow-hidden rounded-[28px] border border-slate-200 bg-[linear-gradient(180deg,rgba(255,255,255,0.94),rgba(241,245,249,0.92))] p-5">
      <div className="pointer-events-none absolute inset-0 opacity-40" style={{ backgroundImage: 'linear-gradient(rgba(148,163,184,0.2) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.2) 1px, transparent 1px)', backgroundSize: '44px 44px' }} />

      <div className="hidden h-[420px] xl:block">
        <DesktopLine style={{ left: '18.5%', top: '22%', width: '10%', height: '2px' }} />
        <DesktopLine style={{ left: '42.5%', top: '22%', width: '10%', height: '2px' }} />
        <DesktopLine style={{ left: '66.5%', top: '22%', width: '10%', height: '2px' }} />
        <DesktopLine style={{ left: '63%', top: '24%', width: '2px', height: '18%' }} />
        <DesktopLine style={{ left: '63%', top: '42%', width: '15%', height: '2px' }} />
        <DesktopLine style={{ left: '56%', top: '47%', width: '2px', height: '18%' }} />
        <DesktopLine style={{ left: '56%', top: '65%', width: '21%', height: '2px' }} />

        {desktopNodes.map((node) => <div key={node.title} className={`absolute w-[220px] rounded-[24px] border p-4 shadow-[0_20px_50px_rgba(15,23,42,0.08)] ${toneClasses[node.tone]}`} style={{ left: node.x, top: node.y }}>
          <div className="inline-flex rounded-full border border-current/20 bg-white/55 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.22em] opacity-80">Stage</div>
          <h3 className="font-display mt-3 text-lg font-semibold tracking-tight">{node.title}</h3>
          <p className="mt-2 text-sm leading-6 opacity-80">{node.subtitle}</p>
          {node.title === 'Human Review' ? <div className="mt-4 inline-flex rounded-full border border-current/20 bg-white/65 px-3 py-1 text-xs font-semibold">{pendingApprovals} queued decisions</div> : null}
          {node.title === 'Audit and Reports' ? <div className="mt-4 inline-flex rounded-full border border-current/20 bg-white/65 px-3 py-1 text-xs font-semibold">{reportCount} exports tracked</div> : null}
          {node.title === 'Connector Action' ? <div className="mt-4 inline-flex rounded-full border border-current/20 bg-white/65 px-3 py-1 text-xs font-semibold">Dry-run and execute lanes</div> : null}
        </div>)}
      </div>

      <div className="space-y-4 xl:hidden">
        {desktopNodes.map((node, index) => <div key={node.title}>
          <div className={`rounded-[24px] border p-4 ${toneClasses[node.tone]}`}>
            <h3 className="font-display text-lg font-semibold tracking-tight">{node.title}</h3>
            <p className="mt-2 text-sm leading-6 opacity-80">{node.subtitle}</p>
          </div>
          {index < desktopNodes.length - 1 ? <div className="flex justify-center py-2 text-slate-400">↓</div> : null}
        </div>)}
      </div>
    </div>
  </div>
}
