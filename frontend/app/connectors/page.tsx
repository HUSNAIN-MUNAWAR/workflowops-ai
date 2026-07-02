'use client'

import { useEffect, useMemo, useState } from 'react'
import { Shell } from '@/components/Shell'
import { Card, EmptyState, ErrorState, StatusPill } from '@/components/Cards'
import { apiFetch } from '@/lib/api'

export default function Page() {
  const [rows, setRows] = useState<any[]>([])
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')
  const [selectedAction, setSelectedAction] = useState('')

  useEffect(() => {
    apiFetch<any[]>('/connectors')
      .then(setRows)
      .catch((fetchError: any) => setError(fetchError.message || 'Login/backend required'))
  }, [])

  async function dry(id: string, action: string) {
    setError('')
    setSelectedAction(`${id}:${action}`)
    try {
      setResult(await apiFetch(`/connectors/${id}/actions/${action}/dry-run`, {
        method: 'POST',
        body: JSON.stringify({ payload: { to: 'client@example.com', url: 'http://localhost/demo', row: { demo: true } } }),
      }))
    } catch (dryRunError: any) {
      setError(dryRunError.message || 'Dry-run failed')
    }
  }

  const metrics = useMemo(() => ({
    connectors: rows.length,
    actions: rows.reduce((sum, row) => sum + row.actions.length, 0),
    categories: new Set(rows.map((row) => row.category)).size,
  }), [rows])

  return <Shell>
    <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
      <div className="grid gap-8 xl:grid-cols-[1.05fr_0.95fr]">
        <div>
          <div className="inline-flex rounded-full border border-cyan-200 bg-cyan-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-cyan-700">Controlled integrations</div>
          <h1 className="font-display mt-4 text-4xl font-semibold tracking-tight text-slate-950">Safe Demo Connectors</h1>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-500">Connector actions are exposed in a way business users can understand: which system is involved, what the action is, and how a dry-run behaves before anything sensitive is allowed to execute.</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Card title="Connectors" value={metrics.connectors} caption="Systems registered in the safe local connector catalog." />
          <Card title="Actions" value={metrics.actions} caption="Dry-runnable operations available across the catalog." />
          <Card title="Categories" value={metrics.categories} caption="Different types of operational systems represented in the demo." />
          <Card title="Mode" value="Local-safe" caption="External sends, payments, and live outbound actions remain disabled by default." />
        </div>
      </div>
    </section>

    {error ? <div className="mt-6"><ErrorState message={error} /></div> : null}

    <div className="mt-8 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
      <section className="space-y-4">
        {!rows.length && !error ? <EmptyState title="No connectors" caption="Start the backend and seed demo data to inspect the connector registry." /> : null}
        {rows.map((connector) => <div key={connector.connector_id} className="surface-panel-strong rounded-[30px] p-5">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div className="max-w-2xl">
              <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-400">{connector.connector_id}</p>
              <h2 className="font-display mt-3 text-2xl font-semibold tracking-tight text-slate-950">{connector.name}</h2>
              <p className="mt-3 text-sm leading-7 text-slate-500">{connector.description}</p>
            </div>
            <StatusPill status={connector.category} />
          </div>
          <div className="mt-5 flex flex-wrap gap-2">
            {connector.actions.map((action: any) => <button
              key={action.name}
              onClick={() => dry(connector.connector_id, action.name)}
              className={`rounded-2xl border px-4 py-3 text-sm font-semibold transition ${selectedAction === `${connector.connector_id}:${action.name}` ? 'border-cyan-300 bg-cyan-50 text-cyan-700' : 'border-slate-200 bg-white/90 text-slate-700 hover:bg-white'}`}
            >
              Dry-run {action.name}
            </button>)}
          </div>
        </div>)}
      </section>

      <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
        <div className="inline-flex rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Dry-run output</div>
        <h2 className="font-display mt-4 text-2xl font-semibold tracking-tight text-slate-950">Connector response preview</h2>
        <p className="mt-2 text-sm leading-6 text-slate-500">The result payload shows what the workflow would send to the connector without executing a live side effect.</p>
        <div className="mt-5 rounded-[28px] border border-slate-200 bg-slate-950 p-5 text-xs leading-6 text-slate-100">
          <pre className="overflow-auto whitespace-pre-wrap">{JSON.stringify(result || { status: 'Select a dry-run action to inspect the connector response.' }, null, 2)}</pre>
        </div>
      </section>
    </div>
  </Shell>
}
