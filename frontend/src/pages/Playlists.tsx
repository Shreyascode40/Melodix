import { useEffect, useState } from 'react'
import api from '../services/api'
import PlaylistCard from '../components/music/PlaylistCard'
import { Link } from 'react-router-dom'
export default function Playlists(){
  const [list,setList]=useState<any[]>([])
  const [name,setName]=useState('')
  const load=()=> api.get('/playlists/?mine=1').then(r=>setList(r.data)).catch(()=>{})
  useEffect(()=>{load()},[])
  const create=async()=>{
    if(!name.trim()) return
    await api.post('/playlists/',{name}); setName(''); load()
  }
  return <div style={{padding:24}}>
    <h2 style={{fontSize:20,fontWeight:800}}>Playlists</h2>
    <div style={{display:'flex',gap:8,margin:'12px 0'}}>
      <input placeholder="New playlist name" value={name} onChange={e=>setName(e.target.value)} style={{height:36,padding:'0 12px',borderRadius:999,border:'1px solid var(--border)',background:'var(--input-background)',flex:1,maxWidth:320}}/>
      <button onClick={create} style={{padding:'8px 16px',borderRadius:999,background:'var(--accent)',color:'#fff',border:'none',cursor:'pointer'}}>Create</button>
      <Link to="/screenshot-import" style={{padding:'8px 16px',borderRadius:999,background:'var(--surface)',border:'1px solid var(--border)',fontSize:13}}>Create from Screenshot</Link>
    </div>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(240px,1fr))',gap:12}}>
      {list.map((p:any)=> <Link key={p.id} to={`/playlists/${p.id}`}><PlaylistCard name={p.name} count={p.song_count} cover={p.cover_url}/></Link>)}
    </div>
  </div>
}
