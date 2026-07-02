'use client'
import { useEffect, useState } from 'react'
import { Shell } from '@/components/Shell'
import { ErrorState, EmptyState, RiskBadge, StatusPill } from '@/components/Cards'
import { apiFetch } from '@/lib/api'

export default function Approvals(){
 const [items,setItems]=useState<any[]>([]); const [error,setError]=useState('')
 const load=()=>apiFetch<any[]>('/approvals').then(setItems).catch(e=>setError(e.message||'Could not load approvals'))
 useEffect(()=>{load()},[])
 async function decide(id:string,action:string){setError('');try{await apiFetch(`/approvals/${id}/${action}`,{method:'POST',body:JSON.stringify({reason:`${action} from connected frontend demo`})}); await load()}catch(e:any){setError(e.message||'Decision failed')}}
 return <Shell><h1 className="text-3xl font-bold text-slate-950">Approval Queue</h1><p className="text-slate-500">Reviewer actions call FastAPI and write audit logs.</p>{error?<div className="mt-4"><ErrorState message={error}/></div>:null}{!items.length&&!error?<div className="mt-6"><EmptyState title="No approvals" caption="Start a high-risk workflow to create an approval request."/></div>:null}<div className="mt-6 space-y-4">{items.map(a=><div key={a.id} className="rounded-3xl border bg-white p-5 shadow-sm"><div className="flex items-center justify-between"><div><h2 className="font-semibold">{a.title}</h2><p className="text-sm text-slate-500">{a.reason}</p></div><div className="flex gap-2"><StatusPill status={a.status}/><RiskBadge score={a.risk_score}/></div></div>{a.status==='pending'?<div className="mt-4 flex gap-2"><button onClick={()=>decide(a.id,'approve')} className="rounded-xl bg-emerald-600 px-3 py-2 text-sm font-semibold text-white">Approve</button><button onClick={()=>decide(a.id,'reject')} className="rounded-xl bg-red-600 px-3 py-2 text-sm font-semibold text-white">Reject</button><button onClick={()=>decide(a.id,'request-changes')} className="rounded-xl bg-amber-500 px-3 py-2 text-sm font-semibold text-white">Request Changes</button></div>:null}</div>)}</div></Shell>
}
