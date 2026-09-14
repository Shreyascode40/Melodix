import { useTheme } from '../context/ThemeContext'
export default function Settings(){
  const {theme,setTheme}=useTheme()
  return <div style={{padding:24, maxWidth:600}}>
    <h2 style={{fontWeight:800}}>Settings</h2>
    <div style={{marginTop:16,background:'var(--surface)',border:'1px solid var(--border)',borderRadius:16,padding:16}}>
      <div style={{fontWeight:600}}>Appearance</div>
      <div style={{display:'grid',gap:8,marginTop:12}}>
        {(['light','dark','system'] as const).map(t=> <label key={t} style={{display:'flex',gap:8,alignItems:'center',cursor:'pointer'}}>
          <input type="radio" name="theme" checked={theme===t} onChange={()=>setTheme(t)}/> {t==='light'?'☀ Light':t==='dark'?'🌙 Dark':'⚙ System'}
        </label>)}
      </div>
    </div>
  </div>
}
