import { useEffect, useState } from 'react'
import api from '../services/api'
import SongRow from '../components/music/SongRow'
export default function Library(){
  const [liked,setLiked]=useState<any[]>([])
  const [recent,setRecent]=useState<any[]>([])
  useEffect(()=>{
    api.get('/library/liked/').then(r=>setLiked(r.data)).catch(()=>{})
    api.get('/library/recent/').then(r=>setRecent(r.data)).catch(()=>{})
  },[])
  return <div style={{padding:24,display:'grid',gap:24}}>
    <h2 style={{fontSize:20,fontWeight:800}}>Library</h2>
    <section>
      <h3 style={{fontWeight:700,marginBottom:12}}>Liked Songs — {liked.length}</h3>
      <div style={{display:'grid',gap:8}}>{liked.length? liked.map((s:any)=> <SongRow key={s.id} song={s}/>) : <div style={{color:'var(--text-secondary)'}}>No liked songs.</div>}</div>
    </section>
    <section>
      <h3 style={{fontWeight:700,marginBottom:12}}>Recently Played</h3>
      <div style={{display:'grid',gap:8}}>{recent.length? recent.map((s:any)=> <SongRow key={s.id} song={s}/>) : <div style={{color:'var(--text-secondary)'}}>No history.</div>}</div>
    </section>
  </div>
}
