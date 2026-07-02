'use client'
import { useEffect, useState } from 'react'
import { Shell } from '@/components/Shell'
import { ErrorState, EmptyState, StatusPill } from '@/components/Cards'
import { apiFetch } from '@/lib/api'

export default function AuditLogs(){
 const [items,setItems]=useState<any[]>([]); const [error,setError]=useState('')
 useEffect(()=>{apiFetch<any[]>('/audit-logs').then(setItems).catch(e=>setError(e.message||'Could not load audit logs'))},[])
 return <Shell><h1 className="text-3xl font-bold text-slate-950">Audit Logs</h1><p className="text-slate-500">Important actions and denied RBAC attempts are persisted.</p>{error?<div className="mt-4"><ErrorState message={error}/></div>:null}{!items.length&&!error?<div className="mt-6"><EmptyState title="No audit events" caption="Login, upload, run, approve, or download a report."/></div>:null}<div className="mt-6 overflow-hidden rounded-2xl border bg-white"><table className="w-full text-sm"><thead className="bg-slate-50 text-left"><tr><th className="p-3">Action</th><th>Actor</th><th>Outcome</th><th>Target</th></tr></thead><tbody>{items.map(l=><tr key={l.id} className="border-t"><td className="p-3 font-medium">{l.action}</td><td>{l.actor_email}</td><td><StatusPill status={l.outcome}/></td><td>{l.target_type}</td></tr>)}</tbody></table></div></Shell>
}
