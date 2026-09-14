export default function PlaylistCard({name,count,cover,onClick}:{name:string;count:number;cover:string; onClick?:()=>void}){
  return <div onClick={onClick} style={{display:'flex',gap:12,padding:12,background:'var(--surface)',border:'1px solid var(--border)',borderRadius:12,cursor:'pointer',alignItems:'center'}}>
    <img src={cover||'https://picsum.photos/200'} alt="" style={{width:56,height:56,borderRadius:10,objectFit:'cover'}}/>
    <div style={{flex:1}}>
      <div style={{fontWeight:600,fontSize:14}}>{name}</div>
      <div style={{fontSize:12,color:'var(--text-secondary)'}}>{count} songs</div>
    </div>
    <button style={{width:28,height:28,borderRadius:999,background:'var(--accent)',color:'#fff',border:'none',cursor:'pointer'}}>▶</button>
  </div>
}
