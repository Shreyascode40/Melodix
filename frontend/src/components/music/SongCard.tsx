import type { Song } from '../../context/PlayerContext'
import { usePlayer } from '../../context/PlayerContext'
export default function SongCard({song,list}:{song:Song; list?:Song[]}){
  const {play,currentSong,isPlaying}=usePlayer()
  const active=currentSong?.id===song.id
  return <div onClick={()=>play(song,list)} style={{width:160,cursor:'pointer',transition:'.15s'}}>
    <div style={{width:160,height:160,borderRadius:999,overflow:'hidden',position:'relative',background:'var(--surface-secondary)',boxShadow:'var(--shadow)'}}>
      <img src={song.cover_url||'https://picsum.photos/300'} alt="" style={{width:'100%',height:'100%',objectFit:'cover',transition:'.2s',transform:'scale(1)'}}/>
      <div style={{position:'absolute',inset:0,display:'grid',placeItems:'center',background:'rgba(0,0,0,.2)',opacity:0.01}} className="ov"><span style={{width:36,height:36,borderRadius:999,background:'var(--accent)',color:'#fff',display:'grid',placeItems:'center'}}>▶</span></div>
      {active&&isPlaying&&<span style={{position:'absolute',bottom:8,left:'50%',transform:'translateX(-50%)',background:'var(--accent)',color:'#fff',fontSize:10,padding:'2px 8px',borderRadius:999}}>Playing</span>}
    </div>
    <div style={{marginTop:10,textAlign:'center'}}>
      <div style={{fontSize:14,fontWeight:600,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis',color:'var(--text-primary)'}}>{song.title}</div>
      <div style={{fontSize:12,color:'var(--text-secondary)'}}>{song.artist}</div>
    </div>
    <style>{`div:hover .ov{opacity:1!important}`}</style>
  </div>
}
