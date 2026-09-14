import { NavLink } from 'react-router-dom'
export default function MobileNav(){
  const items=[['/','⌂'],['/search','⌕'],['/library','♡'],['/playlists','≡'],['/profile','◉'] as const]
  return <nav style={{display:'none'}} className="mobile-nav">
    <style>{`@media(max-width:768px){.mobile-nav{display:flex!important;position:fixed;bottom:72px;left:0;right:0;height:56px;background:var(--surface);border-top:1px solid var(--border);justify-content:space-around;align-items:center;z-index:6}}`}</style>
    {items.map(([to,i])=> <NavLink key={to} to={to} style={({isActive})=>({fontSize:20,color:isActive?'var(--accent)':'var(--text-secondary)'})}>{i}</NavLink>)}
  </nav>
}
