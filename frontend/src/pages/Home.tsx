import { useEffect, useState } from 'react'
import SongCard from '../components/music/SongCard'
import ArtistCard from '../components/music/ArtistCard'
import AlbumCard from '../components/music/AlbumCard'
import PlaylistCard from '../components/music/PlaylistCard'
import api from '../services/api'
import type { Song } from '../context/PlayerContext'

const mockSongs:Song[]=[1,2,3,4,5].map(i=>({id:String(i),provider:'audius',title:['Fall in Love Alone','Submarine','Shape of You','Hysteria','Kesariya'][i-1],artist:['Stacey Ryan','Alex Turner','Ed Sheeran','Muse','Arijit Singh'][i-1],album:'Top Hit',cover_url:`https://picsum.photos/300/300?random=${i}`,duration:210,stream_url:''}))
const artists=[['Bad Bunny','https://picsum.photos/100?random=10'],['Lil Baby','https://picsum.photos/100?random=11'],['Harry Styles','https://picsum.photos/100?random=12'],['Doja Cat','https://picsum.photos/100?random=13']]

export default function Home(){
  const [trending,setTrending]=useState<Song[]>(mockSongs)
  const [playlists,setPlaylists]=useState<any[]>([])
  const greet= new Date().getHours()<12?'Good morning':new Date().getHours()<18?'Good afternoon':'Good evening'
  useEffect(()=>{
    api.get('/music/trending/').then(r=>{ if(r.data.results?.length) setTrending(r.data.results)}).catch(()=>{})
    const token=localStorage.getItem('access'); if(token) api.get('/playlists/?mine=1').then(r=> setPlaylists(r.data)).catch(()=>{})
  },[])
  return <div style={{padding:'24px 24px 0'}}>
    <h1 style={{fontSize:28,margin:'8px 0 2px',fontWeight:800}}>{greet}, Shreyas</h1>
    <p style={{color:'var(--text-secondary)',marginBottom:24}}>Discover something you'll love.</p>

    <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:12}}>
      <h2 style={{fontSize:18,fontWeight:700}}>Recommendation for You</h2>
      <span style={{fontSize:12,color:'var(--text-secondary)'}}>See All</span>
    </div>
    <div style={{display:'flex',gap:16,overflowX:'auto',paddingBottom:8}}>
      {trending.map(s=> <SongCard key={s.id} song={s} list={trending}/>)}
    </div>

    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:24,marginTop:24}}>
      <div>
        <h3 style={{fontSize:16,fontWeight:700,marginBottom:12}}>Top Artist</h3>
        <div style={{display:'flex',gap:12,flexWrap:'wrap',background:'var(--surface)',border:'1px solid var(--border)',borderRadius:16,padding:16}}>
          {artists.map(([n,img])=> <ArtistCard key={n} name={n as string} image={img as string}/>)}
        </div>
        <h3 style={{fontSize:16,fontWeight:700,margin:'16px 0 12px'}}>Recent Playlist</h3>
        <div style={{display:'grid',gap:12}}>
          {[
            ['Stay','Zedd, Alessia Cara','https://picsum.photos/200?random=20'],
            ['Midnight Rain','Zach Boucer','https://picsum.photos/200?random=21'],
            ['Starboy','The Weeknd','https://picsum.photos/200?random=22'],
          ].map(([t,a,c])=> <div key={t} style={{display:'flex',gap:12,alignItems:'center',background:'var(--surface)',border:'1px solid var(--border)',borderRadius:12,padding:12}}>
            <img src={c} alt="" style={{width:44,height:44,borderRadius:8}}/><div style={{flex:1}}><div style={{fontWeight:600,fontSize:14}}>{t}</div><div style={{fontSize:12,color:'var(--text-secondary)'}}>{a}</div></div><button style={{width:28,height:28,borderRadius:999,background:'var(--accent)',color:'#fff',border:'none'}}>▶</button>
          </div>)}
        </div>
      </div>
      <div>
        <h3 style={{fontSize:16,fontWeight:700,marginBottom:12}}>Top Album</h3>
        <div style={{display:'grid',gap:12}}>
          <AlbumCard title="Melodrama" artist="Lorde" cover="https://picsum.photos/200?random=30"/>
          <AlbumCard title="White Trash" artist="Adeem the Artist" cover="https://picsum.photos/200?random=31"/>
          <AlbumCard title="Bell Bottom" artist="Lainey Wilson" cover="https://picsum.photos/200?random=32"/>
        </div>
        <h3 style={{fontSize:16,fontWeight:700,margin:'16px 0 12px'}}>Your Playlists</h3>
        <div style={{display:'grid',gap:12}}>
          {playlists.length? playlists.slice(0,3).map((p:any)=> <PlaylistCard key={p.id} name={p.name} count={p.song_count} cover={p.cover_url} />) : <div style={{color:'var(--text-secondary)',fontSize:13,background:'var(--surface)',border:'1px solid var(--border)',borderRadius:12,padding:16}}>No playlists yet — create one!</div>}
        </div>
      </div>
    </div>
  </div>
}
