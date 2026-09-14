import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
export default function ScreenshotImport(){
  const nav=useNavigate()
  const [file,setFile]=useState<File|null>(null)
  const [preview,setPreview]=useState<string>('')
  const [analyzed,setAnalyzed]=useState<any>(null)
  const [loading,setLoading]=useState(false)
  const [creating,setCreating]=useState(false)
  const [drag,setDrag]=useState(false)
  const [error,setError]=useState<string>('')
  const onFile=(f:File)=>{ setError(''); setAnalyzed(null); setFile(f); setPreview(URL.createObjectURL(f)) }
  const analyze=async()=>{
    if(!file) return
    const token=localStorage.getItem('access')
    if(!token){ setError('Please log in first'); nav('/login'); return }
    setLoading(true); setError('')
    const fd=new FormData(); fd.append('image',file)
    try{
      const r=await api.post('/screenshot/analyze/',fd,{headers:{'Content-Type':'multipart/form-data'}})
      setAnalyzed(r.data)
    }catch(e:any){
      const status=e.response?.status
      const detail=e.response?.data?.detail || e.response?.data?.error || e.message
      if(status===401){ setError('Session expired — please log in again'); nav('/login') }
      else if(status===422){ setError(detail || 'OCR could not read text — try cropping to song list only') }
      else if(status===400){ setError(detail) }
      else { setError(detail || 'Failed — is backend running on :8000?') }
      console.error('analyze failed', e.response?.data || e)
    } finally{setLoading(false)}
  }
  const create=async()=>{
    if(!analyzed) return
    setCreating(true); setError('')
    const songs=(analyzed.matched||[]).filter((m:any)=> m.best).map((m:any)=> m.best.track)
    if(!songs.length) { setError('No songs to create'); setCreating(false); return}
    try{ const r=await api.post('/screenshot/confirm/',{name:'Screenshot Playlist', songs}); nav(`/playlists/${r.data.id}`)}catch(e:any){ setError(e.response?.data?.detail || 'Create failed')}
    setCreating(false)
  }
  return <div style={{padding:24, maxWidth:820, margin:'0 auto'}}>
    <h1 style={{fontSize:26,fontWeight:800}}>Create playlist from screenshot</h1>
    <p style={{color:'var(--text-secondary)',marginBottom:16}}>Upload a playlist screenshot — we’ll OCR and match tracks.</p>
    <div onDragOver={e=>{e.preventDefault(); setDrag(true)}} onDragLeave={()=>setDrag(false)} onDrop={e=>{e.preventDefault(); setDrag(false); const f=e.dataTransfer.files[0]; if(f) onFile(f)}}
      style={{border:'2px dashed var(--border)',borderColor:drag?'var(--accent)':'var(--border)',background:'var(--surface)',borderRadius:16,padding:32,textAlign:'center',transition:'.15s'}}>
      {preview? <img src={preview} alt="" style={{maxWidth:400,maxHeight:260,margin:'0 auto',borderRadius:12}}/> : <div style={{color:'var(--text-secondary)'}}>Drag & drop screenshot<br/>or</div>}
      <label style={{display:'inline-block',marginTop:12,padding:'10px 18px',background:'var(--surface-secondary)',border:'1px solid var(--border)',borderRadius:999,cursor:'pointer'}}>Upload Image
        <input type="file" accept="image/*" hidden onChange={e=>{ const f=e.target.files?.[0]; if(f) onFile(f)}}/>
      </label>
    </div>
    {error && <div style={{marginTop:12,padding:12,background:'#fef2f2',border:'1px solid #fecaca',borderRadius:12,color:'#991b1b',fontSize:13}}>{error}</div>}
    <button onClick={analyze} disabled={!file||loading} style={{marginTop:16,padding:'12px 24px',borderRadius:999,background:'var(--accent)',color:'#fff',border:'none',cursor:'pointer',opacity:!file||loading?0.6:1}}>{loading?'Analyzing…':'Analyze Screenshot'}</button>

    {analyzed && <div style={{marginTop:24,background:'var(--surface)',border:'1px solid var(--border)',borderRadius:16,padding:16}}>
      <h3 style={{fontWeight:700}}>Songs found — {analyzed.matched?.length||0}</h3>
      <div style={{display:'grid',gap:10,marginTop:12}}>
        {analyzed.matched?.map((m:any,i:number)=> <div key={i} style={{display:'flex',gap:12,padding:12,border:'1px solid var(--border)',borderRadius:12,background:m.best?.needs_review?'#fff3cd': m.best?.track?.playable===false ? '#fef2f2':'var(--surface-secondary)'}}>
          <img src={m.best?.track?.cover_url||m.best?.track?.artwork||'https://picsum.photos/100'} alt="" style={{width:48,height:48,borderRadius:8}}/>
          <div style={{flex:1}}>
            <div style={{fontSize:12,color:'var(--text-secondary)'}}>Detected: "{m.detected.raw}"</div>
            <div style={{fontWeight:600,fontSize:14}}>{m.best? `${m.best.track.title} — ${m.best.track.artist}`:'Needs review'}</div>
            {m.best && <div style={{fontSize:12}}>Confidence: {Math.round(m.best.score)}% {m.best.needs_review&&'• Needs review'} {m.best.track?.playable===false && '• Not yet playable (metadata only)'} {m.best.source && `• ${m.best.source}`}</div>}
          </div>
          <span style={{width:20,height:20,borderRadius:4,border:'1px solid var(--border)',background:m.best?'var(--accent)':'transparent',display:'grid',placeItems:'center',color:'#fff'}}>✓</span>
        </div>)}
      </div>
      <button onClick={create} disabled={creating} style={{marginTop:16,padding:'10px 18px',borderRadius:999,background:'var(--accent)',color:'#fff',border:'none',cursor:'pointer'}}>{creating?'Creating…':'Create Playlist'}</button>
    </div>}
  </div>
}
