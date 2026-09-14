import { useEffect, useRef, useState } from 'react'
import api from '../services/api'
const frontCache=new Map<string,{data:any; ts:number}>()
const TTL= 15*60*1000
export function useSearch(query:string){
  const [results,setResults]=useState<any[]>([])
  const [loading,setLoading]=useState(false)
  const [error,setError]=useState<string|null>(null)
  const ctrl=useRef<AbortController|null>(null)
  const lastQ=useRef('')
  useEffect(()=>{
    const nq=query.trim().toLowerCase().replace(/\s+/g,' ')
    if(!nq){ setResults([]); setError(null); return}
    const cached=frontCache.get(nq)
    if(cached && Date.now()-cached.ts < TTL){ setResults(cached.data); return}
    if(lastQ.current===nq && results.length) return
    const t=setTimeout(async()=>{
      ctrl.current?.abort(); ctrl.current=new AbortController()
      lastQ.current=nq; setLoading(true); setError(null)
      try{
        const r=await api.get('/music/search/',{params:{q:nq, limit:12}, signal: ctrl.current.signal})
        frontCache.set(nq,{data:r.data.results||[], ts:Date.now()})
        if(nq===query.trim().toLowerCase().replace(/\s+/g,' ')) setResults(r.data.results||[])
      }catch(e:any){
        if(e.name==='CanceledError' || e.code==='ERR_CANCELED') return
        setError(e.response?.data?.detail || 'Music provider temporarily unavailable')
      }finally{ setLoading(false)}
    },350)
    return()=>clearTimeout(t)
  },[query])
  return {results,loading,error}
}
