'use client'
import { MouseEvent, useEffect, useState } from 'react'
import { Shell } from '@/components/Shell'
import { API_URL, apiFetch, getToken } from '@/lib/api'
import { Card, EmptyState, ErrorState } from '@/components/Cards'

export default function Reports() {
  const [items, setItems] = useState<any[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    apiFetch<any[]>('/reports').then(setItems).catch((fetchError) => setError(fetchError.message || 'Could not load reports'))
  }, [])

  const url = (id: string, format: string) => `${API_URL}/reports/${id}/download?format=${format}`

  async function downloadReport(event: MouseEvent<HTMLAnchorElement>, id: string, format: string, reportType: string) {
    const token = getToken()
    if (!token) return
    event.preventDefault()
    const response = await fetch(url(id, format), { headers: { Authorization: `Bearer ${token}` } })
    const blob = await response.blob()
    const anchor = document.createElement('a')
    anchor.href = URL.createObjectURL(blob)
    anchor.download = `${reportType}.${format}`
    anchor.click()
  }

  return <Shell>
    <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
      <div className="grid gap-8 xl:grid-cols-[1.05fr_0.95fr]">
        <div>
          <div className="inline-flex rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-amber-700">Operational evidence</div>
          <h1 className="font-display mt-4 text-4xl font-semibold tracking-tight text-slate-950">Reports</h1>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-500">Reports turn workflow activity into business-ready output: summaries, evidence packs, reliability snapshots, and exportable deliverables for stakeholders.</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Card title="Reports" value={items.length} caption="Registered report records currently available for download." />
          <Card title="Formats" value="4" caption="JSON, Markdown, HTML, and PDF are supported for each report." />
          <Card title="Report types" value={new Set(items.map((item) => item.report_type)).size || 0} caption="Distinct report categories available in the current dataset." />
          <Card title="Mode" value="Ready to export" caption="Report assets can be downloaded directly from the running backend." />
        </div>
      </div>
    </section>

    {error ? <div className="mt-6"><ErrorState message={error} /></div> : null}
    {!items.length && !error ? <div className="mt-8"><EmptyState title="No reports" caption="Run generate_demo_reports.py or the reliability tester to populate report records." /></div> : null}

    <div className="mt-8 space-y-4">
      {items.map((report) => <div key={report.id} className="surface-panel-strong rounded-[30px] p-5 lg:p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-400">{report.report_type}</p>
            <h2 className="font-display mt-3 text-2xl font-semibold tracking-tight text-slate-950">{report.title}</h2>
            <p className="mt-3 text-sm leading-7 text-slate-500">{report.summary}</p>
          </div>
          <div className="rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-xs font-semibold text-slate-600">Export package</div>
        </div>
        <div className="mt-5 flex flex-wrap gap-2">
          {['json', 'md', 'html', 'pdf'].map((format) => <a
            key={format}
            href={url(report.id, format)}
            onClick={(event) => downloadReport(event, report.id, format, report.report_type)}
            className="rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-white"
          >
            {format.toUpperCase()}
          </a>)}
        </div>
      </div>)}
    </div>
  </Shell>
}
