'use client'
import { useEffect, useState } from 'react'
import { Shell } from '@/components/Shell'
import { ErrorState, EmptyState, StatusPill } from '@/components/Cards'
import { API_URL, apiFetch, getToken } from '@/lib/api'

export default function Documents(){
 const [items,setItems]=useState<any[]>([]); const [fields,setFields]=useState<any[]>([]); const [error,setError]=useState(''); const [uploading,setUploading]=useState(false)
 const load=()=>apiFetch<any[]>('/documents').then(setItems).catch(e=>setError(e.message||'Could not load documents'))
 useEffect(()=>{load()},[])
 async function upload(e:React.ChangeEvent<HTMLInputElement>){const file=e.target.files?.[0]; if(!file)return; setUploading(true); setError(''); const data=new FormData(); data.append('file',file); try{const res=await fetch(`${API_URL}/documents/upload`,{method:'POST',headers:{Authorization:`Bearer ${getToken()}`},body:data}); if(!res.ok) throw new Error(await res.text()); await load()}catch(err:any){setError(err.message||'Upload failed')}finally{setUploading(false)}}
 async function showFields(id:string){setFields(await apiFetch<any[]>(`/documents/${id}/extracted-fields`))}
 return <Shell><h1 className="text-3xl font-bold text-slate-950">Documents Inbox</h1><p className="text-slate-500">Uploads are stored locally, parsed, classified, and persisted.</p><div className="mt-4"><input type="file" onChange={upload}/>{uploading?<span className="ml-3 text-sm text-slate-500">Uploading...</span>:null}</div>{error?<div className="mt-4"><ErrorState message={error}/></div>:null}{!items.length&&!error?<div className="mt-6"><EmptyState title="No documents" caption="Upload a generated sample PDF or seed demo data."/></div>:null}<div className="mt-6 grid grid-cols-2 gap-6"><div className="space-y-3">{items.map(d=><button key={d.id} onClick={()=>showFields(d.id)} className="block w-full rounded-2xl border bg-white p-4 text-left shadow-sm"><div className="flex justify-between"><b>{d.filename}</b><StatusPill status={d.document_type}/></div><p className="mt-1 text-xs text-slate-500">Extraction confidence {d.extraction_confidence}</p></button>)}</div><div className="rounded-3xl bg-white p-6 shadow-sm"><h2 className="font-semibold">Extracted Fields</h2>{fields.length?fields.map(f=><p key={f.name} className="mt-2 text-sm"><b>{f.name}</b>: {JSON.stringify(f.value)} ({f.confidence})</p>):<p className="mt-2 text-sm text-slate-500">Select a document.</p>}</div></div></Shell>
}
