import { useState } from 'react'
import SongRow from '../components/music/SongRow'
import { useSearch } from '../hooks/useSearch'

export default function Search(){
  const [q,setQ]=useState('')
  const {results,loading,error}=useSearch(q)
  return <div style={{padding:24}}>
    <input autoFocus placeholder="Search music, artists, albums…" value={q} onChange={e=>setQ(e.target.value)} style={{width:'100%',maxWidth:560,height:44,padding:'0 16px',borderRadius:999,border:'1px solid var(--border)',background:'var(--input-background)'}}/>
    <div style={{display:'flex',gap:8,marginTop:16}}>
      {['Songs','Artists','Albums','Playlists'].map(t=> <span key={t} style={{padding:'6px 14px',borderRadius:999,background:t==='Songs'?'var(--text-primary)':'var(--surface)',color:t==='Songs'?'var(--surface)':'var(--text-secondary)',border:'1px solid var(--border)',fontSize:13}}>{t}</span>)}
    </div>
    <div style={{marginTop:20,display:'grid',gap:10}}>
      {loading && results.length===0 && Array.from({length:4}).map((_,i)=> <div key={i} style={{height:66,background:'var(--surface)',border:'1px solid var(--border)',borderRadius:12,animation:'pulse 1s infinite'}}/>)}
      {error && <div style={{padding:12,background:'#fef2f2',border:'1px solid #fecaca',borderRadius:12,color:'#991b1b',fontSize:13}}>{error}</div>}
      {!loading && !results.length && q.trim() && !error && <div style={{color:'var(--text-secondary)',padding:24,background:'var(--surface)',border:'1px solid var(--border)',borderRadius:12,textAlign:'center'}}>No results for "{q.trim()}"</div>}
      {results.map((s:any)=> <SongRow key={s.id+s.provider} song={{...s, duration:s.duration||0}}/>)}
    </div>
  </div>
}
