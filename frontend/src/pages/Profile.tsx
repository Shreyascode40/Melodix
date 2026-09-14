import { useAuth } from '../context/AuthContext'
export default function Profile(){
  const {user,logout}=useAuth()
  if(!user) return <div style={{padding:24}}>Please <a href="/login" style={{color:'var(--accent)'}}>log in</a>.</div>
  return <div style={{padding:24, maxWidth:480}}>
    <h2 style={{fontWeight:800}}>Profile</h2>
    <div style={{background:'var(--surface)',border:'1px solid var(--border)',borderRadius:16,padding:16,marginTop:12,display:'grid',gap:8}}>
      <div><b>Username:</b> {user.username}</div>
      <div><b>Email:</b> {user.email}</div>
      <div><b>Display:</b> {user.display_name||'—'}</div>
      <button onClick={logout} style={{marginTop:8,padding:'8px 14px',borderRadius:999,border:'1px solid var(--border)',background:'var(--surface-secondary)',cursor:'pointer'}}>Log out</button>
    </div>
  </div>
}
