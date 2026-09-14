import { useTheme } from '../../context/ThemeContext'
import { useAuth } from '../../context/AuthContext'
export default function Header({onSearch}:{onSearch?:(v:string)=>void}){
  const {resolved,toggle}=useTheme()
  const {user}=useAuth()
  return <header style={{height:64,display:'flex',alignItems:'center',gap:16,padding:'0 24px',background:'var(--surface)',borderBottom:'1px solid var(--border)',position:'sticky',top:0,zIndex:5}}>
    <div style={{flex:1,maxWidth:480,position:'relative'}}>
      <span style={{position:'absolute',left:12,top:'50%',transform:'translateY(-50%)',color:'var(--text-muted)'}}>⌕</span>
      <input placeholder="Search music, artists, albums…" onChange={e=>onSearch?.(e.target.value)} style={{width:'100%',height:40,paddingLeft:36,paddingRight:12,border:'1px solid var(--border)',borderRadius:999,background:'var(--input-background)',color:'var(--text-primary)'}}/>
    </div>
    <button onClick={toggle} style={{width:40,height:40,borderRadius:999,border:'1px solid var(--border)',background:'var(--surface-secondary)',cursor:'pointer'}}>{resolved==='dark'?'☀':'🌙'}</button>
    <div style={{display:'flex',alignItems:'center',gap:8}}>
      <img src={user?`https://i.pravatar.cc/100?u=${user.username}`:'https://i.pravatar.cc/100'} alt="" style={{width:32,height:32,borderRadius:999}}/>
      <span style={{fontSize:14,color:'var(--text-primary)',fontWeight:600}}>{user?user.username:'Guest'}</span>
    </div>
  </header>
}
