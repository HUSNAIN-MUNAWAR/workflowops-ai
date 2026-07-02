'use client'
import { useEffect, useState } from 'react'
import { Shell } from '@/components/Shell'
import { ErrorState, EmptyState } from '@/components/Cards'
import { apiFetch } from '@/lib/api'

export default function TemplatesPage(){
 const [items,setItems]=useState<any[]>([]); const [error,setError]=useState('')
 useEffect(()=>{apiFetch<any[]>('/workflow-templates').then(setItems).catch(e=>setError(e.message||'Could not load templates'))},[])
 return <Shell><h1 className="text-3xl font-bold text-slate-950">Workflow Template Marketplace</h1><p className="mt-2 text-slate-500">Templates are loaded from persisted database records.</p>{error?<div className="mt-6"><ErrorState message={error}/></div>:null}{!error && !items.length?<div className="mt-6"><EmptyState title="No templates" caption="Run the seed script or backend startup seed."/></div>:null}<div className="mt-6 grid grid-cols-3 gap-5">{items.map(t=><div key={t.id} className="rounded-3xl border bg-white p-6 shadow-sm"><p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{t.slug}</p><h2 className="mt-2 text-xl font-bold text-slate-950">{t.name}</h2><p className="mt-2 text-sm text-slate-600">{t.description}</p><p className="mt-4 text-sm text-slate-500">Risk threshold: {t.risk_threshold}</p><p className="mt-2 text-xs text-slate-400">Nodes: {t.definition_json?.nodes?.length || 0}</p></div>)}</div></Shell>
}
