import { createContext, useContext, useEffect, useRef, useState } from 'react'
export type Song={id:string; provider:string; title:string; artist:string; album:string; cover_url:string; duration:number; stream_url:string}
type Ctx={
  currentSong:Song|null; queue:Song[]; index:number; isPlaying:boolean; currentTime:number; duration:number; volume:number; shuffle:boolean; repeat:'off'|'one'|'all';
  play:(s:Song, list?:Song[])=>void; toggle:()=>void; next:()=>void; prev:()=>void; seek:(t:number)=>void; setVol:(v:number)=>void; toggleShuffle:()=>void; toggleRepeat:()=>void;
}
const PlayerContext=createContext<Ctx>(null as any)
export const usePlayer=()=>useContext(PlayerContext)
export function PlayerProvider({children}:{children:React.ReactNode}){
  const audioRef=useRef<HTMLAudioElement>(null)
  const [queue,setQueue]=useState<Song[]>([])
  const [index,setIndex]=useState(-1)
  const [isPlaying,setIsPlaying]=useState(false)
  const [currentTime,setCurrentTime]=useState(0)
  const [duration,setDuration]=useState(0)
  const [volume,setVolume]=useState(0.85)
  const [shuffle,setShuffle]=useState(false)
  const [repeat,setRepeat]=useState<'off'|'one'|'all'>('off')
  const currentSong= index>=0 ? queue[index] : null
  const play=async(s:Song,list?:Song[])=>{
    let toPlay=s
    if(!s.stream_url){
      try{
        const {default: api} = await import('../services/api')
        const q=`${s.title} ${s.artist}`.trim()
        const r=await api.get('/music/search/',{params:{q, limit:5}})
        const cand=r.data.results?.[0]
        if(cand?.stream_url) toPlay={...s, stream_url:cand.stream_url, cover_url:cand.cover_url||s.cover_url, provider:cand.provider, id:cand.id}
        else if(cand) toPlay={...s, cover_url:cand.cover_url||s.cover_url}
      }catch{}
    }
    if(list){ const nl=list.map(x=> x.id===s.id? toPlay : x); setQueue(nl); setIndex(nl.findIndex(x=>x.id===toPlay.id && x.provider===toPlay.provider))}
    else if(!queue.find(x=>x.id===s.id)){ setQueue(q=>[...q,toPlay]); setIndex(queue.length)}
    else {
      const idx=queue.findIndex(x=>x.id===s.id)
      const nq=[...queue]; nq[idx]=toPlay; setQueue(nq); setIndex(idx)
    }
    setIsPlaying(true)
  }
  const toggle=()=> setIsPlaying(v=>!v)
  const next=()=>{
    if(repeat==='one'){ const a=audioRef.current; if(a) a.currentTime=0; return}
    if(queue.length===0) return
    if(shuffle){ setIndex(Math.floor(Math.random()*queue.length)); return}
    setIndex(i=> i < queue.length-1 ? i+1 : repeat==='all'?0:i)
  }
  const prev=()=>{
    const a=audioRef.current; if(a && a.currentTime>3) {a.currentTime=0; return}
    setIndex(i=> i>0?i-1:i)
  }
  const seek=(t:number)=>{ if(audioRef.current) audioRef.current.currentTime=t}
  const setVol=(v:number)=>{ setVolume(v); if(audioRef.current) audioRef.current.volume=v}
  const toggleShuffle=()=>setShuffle(v=>!v)
  const toggleRepeat=()=>setRepeat(r=> r==='off'?'all':r==='all'?'one':'off')
  const currentIdRef=useRef<string>("")
  useEffect(()=>{
    const a=audioRef.current; if(!a || !currentSong) return
    const sid=`${currentSong.provider}:${currentSong.id}`
    if(currentIdRef.current===sid) return
    currentIdRef.current=sid
    a.src=currentSong.stream_url||''
    a.volume=volume
    if(isPlaying) a.play().catch(()=>setIsPlaying(false))
  },[currentSong?.id, currentSong?.provider, currentSong?.stream_url])
  useEffect(()=>{ const a=audioRef.current; if(!a) return; if(!currentSong) return; a.volume=volume; isPlaying? a.play().catch(()=>{}): a.pause()},[isPlaying, volume, currentSong?.id])
  return <PlayerContext.Provider value={{currentSong,queue,index,isPlaying,currentTime,duration,volume,shuffle,repeat,play,toggle,next,prev,seek,setVol,toggleShuffle,toggleRepeat}}>
    {children}
    <audio ref={audioRef} preload="metadata" onTimeUpdate={e=>setCurrentTime(e.currentTarget.currentTime)} onLoadedMetadata={e=>setDuration(e.currentTarget.duration||0)} onError={()=>{ if(currentSong?.stream_url) { const a=audioRef.current; if(a){ a.src=currentSong.stream_url; a.play().catch(()=>{}) }}}} onEnded={()=>{ if(repeat==='one'){ const a=audioRef.current; if(a){a.currentTime=0;a.play()}} else next()}} />
  </PlayerContext.Provider>
}
