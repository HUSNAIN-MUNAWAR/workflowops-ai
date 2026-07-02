'use client'
import { useEffect, useState } from 'react'
import { Shell } from '@/components/Shell'
import { Card, EmptyState, ErrorState, StatusPill } from '@/components/Cards'
import { apiFetch } from '@/lib/api'

export default function AuditLogs(){
 const [items,setItems]=useState<any[]>([]); const [error,setError]=useState('')
 useEffect(()=>{apiFetch<any[]>('/audit-logs').then(setItems).catch(e=>setError(e.message||'Could not load audit logs'))},[])
 const metrics={events:items.length, actors:new Set(items.map(item=>item.actor_email)).size, blocked:items.filter(item=>String(item.outcome).includes('deny')||String(item.outcome).includes('fail')).length, successful:items.filter(item=>String(item.outcome).includes('success')||String(item.outcome).includes('allow')||String(item.outcome).includes('completed')).length}
 return <Shell>
   <section className="surface-panel-strong rounded-[34px] p-6 lg:p-7">
     <div className="grid gap-8 xl:grid-cols-[1.05fr_0.95fr]">
       <div>
         <div className="inline-flex rounded-full border border-slate-200 bg-white/90 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Audit trail</div>
         <h1 className="font-display mt-4 text-4xl font-semibold tracking-tight text-slate-950">Audit Logs</h1>
         <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-500">The audit log shows who triggered an action, what the system decided, and which business object was affected so reviews stay evidence-based.</p>
       </div>
       <div className="grid gap-4 sm:grid-cols-2">
         <Card title="Events" value={metrics.events} caption="Persisted audit records currently available in the workspace." />
         <Card title="Actors" value={metrics.actors} caption="Distinct users represented in the captured audit trail." />
         <Card title="Blocked or failed" value={metrics.blocked} caption="Events showing denied or failed control outcomes." />
         <Card title="Successful" value={metrics.successful} caption="Events that completed or were allowed to proceed." />
       </div>
     </div>
   </section>
   {error?<div className="mt-6"><ErrorState message={error}/></div>:null}
   {!items.length&&!error?<div className="mt-8"><EmptyState title="No audit events" caption="Login, upload, run a workflow, approve a request, or download a report to populate the audit trail." /></div>:null}
   <div className="mt-8 overflow-hidden rounded-[30px] border border-slate-200 bg-white/90 shadow-[0_24px_70px_rgba(15,23,42,0.08)]">
     <table className="w-full min-w-[720px] text-sm">
       <thead className="bg-slate-50/90 text-left">
         <tr>
           <th className="px-4 py-4 font-semibold text-slate-500">Action</th>
           <th className="px-4 py-4 font-semibold text-slate-500">Actor</th>
           <th className="px-4 py-4 font-semibold text-slate-500">Outcome</th>
           <th className="px-4 py-4 font-semibold text-slate-500">Target</th>
         </tr>
       </thead>
       <tbody>
         {items.map(log=><tr key={log.id} className="border-t border-slate-100">
           <td className="px-4 py-4 font-medium text-slate-800">{log.action}</td>
           <td className="px-4 py-4 text-slate-600">{log.actor_email}</td>
           <td className="px-4 py-4"><StatusPill status={log.outcome}/></td>
           <td className="px-4 py-4 text-slate-600">{log.target_type}</td>
         </tr>)}
       </tbody>
     </table>
   </div>
 </Shell>
}
