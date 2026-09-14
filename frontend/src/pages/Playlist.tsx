import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../services/api'
import SongRow from '../components/music/SongRow'
import { usePlayer } from '../context/PlayerContext'
export default function Playlist(){
  const {id}=useParams()
  const [pl,setPl]=useState<any>(null)
  const {play}=usePlayer()
  const load=()=> api.get(`/playlists/${id}/`).then(r=> setPl(r.data)).catch(()=>{})
  useEffect(()=>{load()},[id])
  if(!pl) return <div style={{padding:24}}>Loading…</div>
  const songs=pl.songs?.map((x:any)=> x.song) || []
  return <div style={{padding:24}}>
    <div style={{display:'flex',gap:16,alignItems:'end',marginBottom:24}}>
      <img src={pl.cover_url||'https://picsum.photos/300'} alt="" style={{width:160,height:160,borderRadius:16,objectFit:'cover',boxShadow:'var(--shadow)'}}/>
      <div>
        <h1 style={{fontSize:28,fontWeight:800,margin:0}}>{pl.name}</h1>
        <div style={{color:'var(--text-secondary)',fontSize:13}}>{pl.song_count} songs • {pl.description||'No description'}</div>
        <button onClick={()=> songs[0]&& play(songs[0], songs)} style={{marginTop:12,padding:'10px 18px',borderRadius:999,background:'var(--accent)',color:'#fff',border:'none',cursor:'pointer'}}>▶ Play</button>
      </div>
    </div>
    <div style={{display:'grid',gap:8}}>
      {pl.songs?.map((ps:any)=> <SongRow key={ps.song.id} song={ps.song}/>)}
      {!pl.songs?.length && <div style={{color:'var(--text-secondary)',background:'var(--surface)',border:'1px solid var(--border)',borderRadius:12,padding:24,textAlign:'center'}}>Empty playlist — add songs from Search.</div>}
    </div>
  </div>
}
