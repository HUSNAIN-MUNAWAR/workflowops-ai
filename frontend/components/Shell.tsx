import Link from 'next/link'

const nav = [
  ['Dashboard', '/dashboard'], ['Templates', '/templates'], ['Builder', '/builder'], ['Run Console', '/run-console'],
  ['Approvals', '/approvals'], ['Documents', '/documents'], ['Connectors', '/connectors'], ['Policies', '/policies'], ['Reliability', '/reliability'], ['Audit Logs', '/audit-logs'], ['Reports', '/reports'], ['Settings', '/settings']
]

export function Shell({ children }: { children: React.ReactNode }) {
  return <div className="min-h-screen bg-slate-50">
    <aside className="fixed inset-y-0 left-0 w-72 bg-slate-950 text-white p-6">
      <Link href="/" className="text-2xl font-bold">WorkflowOps AI</Link>
      <p className="mt-2 text-sm text-slate-300">Governed AI automation with approvals, audit logs, and reliability testing.</p>
      <div className="mt-4 rounded-xl bg-slate-900 p-3 text-xs text-slate-300">Demo API: FastAPI + SQLite/Postgres. Synthetic data only.</div>
      <nav className="mt-8 space-y-2">
        {nav.map(([label, href]) => <Link key={href} href={href} className="block rounded-xl px-3 py-2 text-sm hover:bg-slate-800">{label}</Link>)}
      </nav>
    </aside>
    <main className="ml-72 p-8">{children}</main>
  </div>
}
