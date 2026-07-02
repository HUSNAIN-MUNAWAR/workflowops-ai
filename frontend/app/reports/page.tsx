'use client'
import { useEffect, useState } from 'react'
import { Shell } from '@/components/Shell'
import { API_URL, apiFetch, getToken } from '@/lib/api'
import { ErrorState, EmptyState } from '@/components/Cards'

export default function Reports(){
 const [items,setItems]=useState<any[]>([]); const [error,setError]=useState('')
 useEffect(()=>{apiFetch<any[]>('/reports').then(setItems).catch(e=>setError(e.message||'Could not load reports'))},[])
 const url=(id:string,fmt:string)=>`${API_URL}/reports/${id}/download?format=${fmt}`
 return <Shell><h1 className="text-3xl font-bold text-slate-950">Reports</h1><p className="text-slate-500">Download report files registered in the reports table.</p>{error?<div className="mt-4"><ErrorState message={error}/></div>:null}{!items.length&&!error?<div className="mt-6"><EmptyState title="No reports" caption="Run generate_demo_reports.py or the reliability tester."/></div>:null}<div className="mt-6 space-y-4">{items.map(r=><div key={r.id} className="rounded-3xl border bg-white p-5 shadow-sm"><h2 className="font-semibold">{r.title}</h2><p className="text-sm text-slate-500">{r.summary}</p><div className="mt-3 flex gap-2">{['json','md','html','pdf'].map(fmt=><a key={fmt} href={url(r.id,fmt)} onClick={e=>{const token=getToken(); if(token){e.preventDefault(); fetch(url(r.id,fmt),{headers:{Authorization:`Bearer ${token}`}}).then(async res=>{const blob=await res.blob(); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download=`${r.report_type}.${fmt}`; a.click()})}}} className="rounded-xl bg-slate-100 px-3 py-2 text-sm font-semibold">{fmt.toUpperCase()}</a>)}</div></div>)}</div></Shell>
}
