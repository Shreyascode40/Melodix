import { NavLink } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
const items=[['/','Home','⌂'],['/search','Search','⌕'],['/explore','Discover','◇'],['/library','Library','♡'],['/playlists','Playlists','≡'],['/liked','Liked','♥'],['/screenshot-import','Import','⬆'] as const]
export default function Sidebar(){
  const {user}=useAuth()
  return <aside style={{width:80,background:'var(--surface)',borderRight:'1px solid var(--border)',display:'flex',flexDirection:'column',alignItems:'center',padding:'16px 0',gap:8,position:'fixed',top:0,left:0,bottom:72,overflowY:'auto'}}>
    <div style={{width:36,height:36,borderRadius:12,background:'var(--accent)',display:'grid',placeItems:'center',color:'#fff',fontWeight:800,marginBottom:12}}>♪</div>
    {items.map(([to,label,icon])=> <NavLink key={to} to={to} style={({isActive})=>({width:52,height:52,borderRadius:14,display:'grid',placeItems:'center',background:isActive?'var(--surface-secondary)':'transparent',color:isActive?'var(--text-primary)':'var(--text-secondary)',fontSize:18,transition:'.15s'})} title={label}>{icon}</NavLink>)}
    <div style={{flex:1}}/>
    <img src={user?`https://i.pravatar.cc/100?u=${user.username}`:`https://i.pravatar.cc/100`} alt="" style={{width:36,height:36,borderRadius:999,objectFit:'cover',border:'1px solid var(--border)'}}/>
    <NavLink to="/settings" style={{width:36,height:36,display:'grid',placeItems:'center',color:'var(--text-secondary)'}}>⚙</NavLink>
  </aside>
}
