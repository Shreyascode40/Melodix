import { usePlayer } from '../../context/PlayerContext'
export default function MusicPlayer(){
  const {currentSong,isPlaying,toggle,next,prev,currentTime,duration,seek,volume,setVol,shuffle,repeat,toggleShuffle,toggleRepeat}=usePlayer()
  const fmt=(s:number)=> isNaN(s)?'0:00': `${Math.floor(s/60)}:${String(Math.floor(s%60)).padStart(2,'0')}`
  return <div style={{position:'fixed',bottom:0,left:0,right:0,height:72,background:'var(--player-background)',borderTop:'1px solid var(--player-border)',display:'flex',alignItems:'center',gap:12,padding:'0 16px',zIndex:10}}>
    <img src={currentSong?.cover_url||'https://picsum.photos/100'} alt="" style={{width:48,height:48,borderRadius:8,objectFit:'cover'}}/>
    <div style={{width:180}}>
      <div style={{fontSize:14,fontWeight:600,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>{currentSong?.title||'Nothing playing'}</div>
      <div style={{fontSize:12,color:'var(--text-secondary)'}}>{currentSong?.artist||'—'}</div>
    </div>
    <button style={{width:32,height:32,borderRadius:999,border:'1px solid var(--border)',background:'var(--surface)',cursor:'pointer'}} onClick={toggleShuffle} title="shuffle" >{shuffle?'🔀':'◯'}</button>
    <button onClick={prev} style={{width:36,height:36,borderRadius:999,border:'1px solid var(--border)',cursor:'pointer'}}>⏮</button>
    <button onClick={toggle} style={{width:44,height:44,borderRadius:999,background:'var(--accent)',color:'#fff',border:'none',cursor:'pointer',fontSize:16}}>{isPlaying?'❚❚':'▶'}</button>
    <button onClick={next} style={{width:36,height:36,borderRadius:999,border:'1px solid var(--border)',cursor:'pointer'}}>⏭</button>
    <button onClick={toggleRepeat} style={{width:32,height:32,borderRadius:999,border:'1px solid var(--border)',background:repeat!=='off'?'var(--surface-secondary)':'var(--surface)',cursor:'pointer'}}>{repeat==='one'?'🔂':repeat==='all'?'🔁':'↻'}</button>
    <div style={{flex:1,display:'flex',alignItems:'center',gap:8}}>
      <span style={{fontSize:11,color:'var(--text-secondary)',width:32,textAlign:'right'}}>{fmt(currentTime)}</span>
      <input type="range" min={0} max={duration||100} value={currentTime} onChange={e=>seek(Number(e.target.value))} style={{flex:1,accentColor:'var(--accent)'}}/>
      <span style={{fontSize:11,color:'var(--text-secondary)',width:32}}>{fmt(duration)}</span>
    </div>
    <input type="range" min={0} max={1} step={0.01} value={volume} onChange={e=>setVol(Number(e.target.value))} style={{width:80,accentColor:'var(--accent)'}}/>
  </div>
}
