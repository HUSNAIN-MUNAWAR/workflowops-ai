'use client'
import { useEffect, useState } from 'react'
import { Shell } from '@/components/Shell'
import { ErrorState, RiskBadge, StatusPill } from '@/components/Cards'
import { apiFetch } from '@/lib/api'

export default function Reliability(){
 const [runs,setRuns]=useState<any[]>([]); const [detail,setDetail]=useState<any>(null); const [error,setError]=useState(''); const [loading,setLoading]=useState(false)
 const load=()=>apiFetch<any[]>('/reliability-tests').then(setRuns).catch(e=>setError(e.message||'Could not load reliability runs'))
 useEffect(()=>{load()},[])
 async function start(){setLoading(true);setError('');try{const r=await apiFetch<any>('/reliability-tests/run',{method:'POST',body:JSON.stringify({template_slug:'invoice_approval'})}); await load(); setDetail(await apiFetch(`/reliability-tests/${r.id}`))}catch(e:any){setError(e.message||'Run failed')}finally{setLoading(false)}}
 return <Shell><div className="flex items-center justify-between"><div><h1 className="text-3xl font-bold text-slate-950">Workflow EvalBench</h1><p className="text-slate-500">Signature reliability tester with synthetic adversarial scenarios.</p></div><button onClick={start} className="rounded-xl bg-slate-950 px-4 py-3 font-semibold text-white">{loading?'Running...':'Run Reliability Tests'}</button></div>{error?<div className="mt-4"><ErrorState message={error}/></div>:null}<div className="mt-6 grid grid-cols-2 gap-6"><div className="space-y-3">{runs.map(r=><button key={r.id} onClick={async()=>setDetail(await apiFetch(`/reliability-tests/${r.id}`))} className="block w-full rounded-2xl border bg-white p-4 text-left"><div className="flex justify-between"><b>{r.workflow_template_slug}</b><StatusPill status={r.status}/></div><p className="mt-2"><RiskBadge score={r.reliability_score}/></p><p className="mt-1 text-xs text-slate-500">Failed cases: {r.failed_cases} · Safety: {r.safety_score}</p></button>)}</div><div className="rounded-3xl bg-white p-6 shadow-sm"><h2 className="font-semibold">Case Results</h2>{detail?.cases?.map((c:any)=><div key={c.id} className="mt-3 rounded-xl border p-3"><div className="flex justify-between"><b>{c.test_name}</b><StatusPill status={c.passed?'passed':'failed'}/></div><p className="mt-1 text-xs text-slate-500">{c.scenario_type} · {c.severity}</p><p className="mt-2 text-sm">{c.mitigation_recommendation}</p></div>)||<p className="mt-2 text-sm text-slate-500">Select or run a test.</p>}</div></div></Shell>
}
