export default function AlbumCard({title,artist,cover}:{title:string;artist:string;cover:string}){
  return <div style={{display:'flex',gap:12,padding:12,background:'var(--surface)',border:'1px solid var(--border)',borderRadius:12,alignItems:'center'}}>
    <img src={cover} alt="" style={{width:64,height:64,borderRadius:10,objectFit:'cover'}}/>
    <div style={{flex:1}}>
      <div style={{fontSize:14,fontWeight:600}}>{title}</div>
      <div style={{fontSize:12,color:'var(--text-secondary)'}}>{artist}</div>
    </div>
    <span style={{fontSize:12,color:'#f59e0b'}}>★ 4.9</span>
    <button style={{padding:'6px 12px',borderRadius:999,border:'1px solid var(--border)',background:'var(--surface-secondary)',cursor:'pointer',fontSize:12}}>Play</button>
  </div>
}
