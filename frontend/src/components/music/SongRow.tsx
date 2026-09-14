import type { Song } from '../../context/PlayerContext'
import { usePlayer } from '../../context/PlayerContext'
import api from '../../services/api'
export default function SongRow({song, onAdd}:{song:Song; onAdd?:()=>void}){
  const {play,currentSong,isPlaying}=usePlayer()
  const active=currentSong?.id===song.id
  const score = (song as any).match_score
  const status = (song as any).match_status
  return <div style={{display:'flex',alignItems:'center',gap:12,padding:'10px 12px',background:'var(--surface)',border:'1px solid var(--border)',borderRadius:12,transition:'.15s'}}>
    <img src={song.cover_url||(song as any).artwork||'https://picsum.photos/100'} alt="" style={{width:44,height:44,borderRadius:8,objectFit:'cover'}}/>
    <div style={{flex:1,minWidth:0}}>
      <div style={{fontSize:14,fontWeight:600,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis',color:active?'var(--accent)':'var(--text-primary)'}}>{song.title}</div>
      <div style={{fontSize:12,color:'var(--text-secondary)'}}>{song.artist} • {song.album}</div>
      {score!=null && <div style={{fontSize:10,color: status==='high'?'#16a34a': status==='low'?'#dc2626':'var(--text-muted)'}}>Match: {Math.round(score*100)}% {status && `• ${status}`}</div>}
    </div>
    <div style={{fontSize:12,color:'var(--text-muted)'}}>{Math.floor(song.duration/60)}:{String(song.duration%60).padStart(2,'0')}</div>
    <button onClick={()=>play(song)} style={{width:32,height:32,borderRadius:999,border:'1px solid var(--border)',background:active&&isPlaying?'var(--accent)':'var(--surface-secondary)',color:active&&isPlaying?'#fff':'var(--text-primary)',cursor:'pointer'}}>{active&&isPlaying?'❚❚':'▶'}</button>
    <button onClick={async()=>{ if(onAdd) onAdd(); else try{ await api.post('/library/like/',song); }catch{}}} style={{width:28,height:28,borderRadius:999,border:'1px solid var(--border)',background:'var(--surface)',cursor:'pointer'}}>♡</button>
  </div>
}
