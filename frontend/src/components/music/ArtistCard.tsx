export default function ArtistCard({name,image}:{name:string; image:string}){
  return <div style={{textAlign:'center',width:88}}>
    <img src={image} alt="" style={{width:72,height:72,borderRadius:999,objectFit:'cover',margin:'0 auto',border:'1px solid var(--border)'}}/>
    <div style={{fontSize:12,marginTop:6,fontWeight:600,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>{name}</div>
  </div>
}
