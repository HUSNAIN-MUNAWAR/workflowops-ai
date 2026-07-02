'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navGroups = [
  {
    label: 'Operate',
    items: [
      ['Dashboard', '/dashboard'],
      ['Approvals', '/approvals'],
      ['Run Console', '/run-console'],
      ['Reports', '/reports'],
    ],
  },
  {
    label: 'Design',
    items: [
      ['Templates', '/templates'],
      ['Builder', '/builder'],
      ['Documents', '/documents'],
      ['Connectors', '/connectors'],
    ],
  },
  {
    label: 'Govern',
    items: [
      ['Policies', '/policies'],
      ['Reliability', '/reliability'],
      ['Audit Logs', '/audit-logs'],
      ['Settings', '/settings'],
    ],
  },
]

function isActive(pathname: string, href: string) {
  if (href === '/') return pathname === href
  return pathname === href || pathname.startsWith(`${href}/`)
}

export function Shell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const currentLabel = navGroups.flatMap((group) => group.items).find(([, href]) => isActive(pathname, href))?.[0] ?? 'Workspace'

  return <div className="min-h-screen">
    <div className="mx-auto flex min-h-screen w-full max-w-[1720px] flex-col lg:flex-row">
      <aside className="relative overflow-hidden border-b border-white/60 bg-[#081321] px-4 py-5 text-white shadow-[0_35px_100px_rgba(2,6,23,0.34)] lg:min-h-screen lg:w-[320px] lg:border-b-0 lg:border-r lg:px-5 lg:py-6">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.2),transparent_34%),radial-gradient(circle_at_bottom_right,rgba(245,158,11,0.16),transparent_30%)]" />
        <div className="relative">
          <div className="rounded-[28px] border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
            <Link href="/" className="font-display text-3xl font-semibold tracking-tight">WorkflowOps AI</Link>
            <p className="mt-3 text-sm leading-6 text-slate-300">Automation operations workspace for intake, approvals, execution controls, and evidence-ready reporting.</p>
            <div className="mt-5 grid grid-cols-2 gap-3 text-xs">
              <div className="rounded-2xl border border-white/10 bg-white/5 px-3 py-3">
                <p className="font-semibold uppercase tracking-[0.2em] text-cyan-200">Mode</p>
                <p className="mt-2 text-slate-200">Connected demo</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-3 py-3">
                <p className="font-semibold uppercase tracking-[0.2em] text-amber-200">Guardrails</p>
                <p className="mt-2 text-slate-200">Policy and approvals</p>
              </div>
            </div>
          </div>

          <nav className="mt-6 space-y-6">
            {navGroups.map((group) => <div key={group.label}>
              <p className="px-3 text-[11px] font-semibold uppercase tracking-[0.28em] text-slate-400">{group.label}</p>
              <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-1">
                {group.items.map(([label, href]) => {
                  const active = isActive(pathname, href)
                  return <Link
                    key={href}
                    href={href}
                    className={`group flex items-center justify-between rounded-2xl px-4 py-3 text-sm font-medium transition ${active ? 'bg-white text-slate-950 shadow-[0_16px_40px_rgba(255,255,255,0.14)]' : 'border border-transparent bg-white/5 text-slate-200 hover:border-white/10 hover:bg-white/10 hover:text-white'}`}
                  >
                    <span>{label}</span>
                    <span className={`text-xs ${active ? 'text-slate-500' : 'text-slate-500 group-hover:text-slate-300'}`}>Open</span>
                  </Link>
                })}
              </div>
            </div>)}
          </nav>

          <div className="mt-6 rounded-[26px] border border-white/10 bg-[#0d1a2a] px-4 py-4 text-sm text-slate-300">
            <p className="font-semibold text-white">Current focus</p>
            <p className="mt-2 leading-6">{currentLabel} surface in the connected automation workspace.</p>
          </div>
        </div>
      </aside>

      <div className="min-w-0 flex-1">
        <header className="sticky top-0 z-20 border-b border-white/70 bg-white/70 backdrop-blur-xl">
          <div className="flex flex-col gap-4 px-4 py-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-10">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-slate-400">Operations workspace</p>
              <p className="font-display mt-2 text-2xl font-semibold tracking-tight text-slate-950">{currentLabel}</p>
            </div>
            <div className="flex flex-wrap gap-2 text-xs font-semibold">
              <span className="rounded-full border border-slate-200 bg-white/85 px-3 py-2 text-slate-600 shadow-sm">Synthetic operating data</span>
              <span className="rounded-full border border-cyan-200 bg-cyan-50/85 px-3 py-2 text-cyan-700 shadow-sm">Live API-backed screens</span>
              <span className="rounded-full border border-amber-200 bg-amber-50/85 px-3 py-2 text-amber-700 shadow-sm">Human approval checkpoints</span>
            </div>
          </div>
        </header>

        <main className="px-4 py-6 sm:px-6 lg:px-10 lg:py-10">
          {children}
        </main>
      </div>
    </div>
  </div>
}
