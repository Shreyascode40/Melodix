import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate, Link } from 'react-router-dom'
export default function Login(){
  const {login}=useAuth(); const nav=useNavigate()
  const [u,setU]=useState(''); const [p,setP]=useState(''); const [err,setErr]=useState('')
  const submit=async(e:any)=>{ e.preventDefault(); setErr(''); try{ await login(u,p); nav('/')}catch(e:any){ setErr(e.response?.data?.detail||'Login failed')}}
  return <div style={{minHeight:'60vh',display:'grid',placeItems:'center',padding:24}}>
    <form onSubmit={submit} style={{width:360,background:'var(--surface)',border:'1px solid var(--border)',borderRadius:16,padding:24,display:'grid',gap:12}}>
      <h2 style={{margin:0}}>Welcome back</h2>
      {err&&<div style={{color:'#ef4444',fontSize:13}}>{err}</div>}
      <input placeholder="Username" value={u} onChange={e=>setU(e.target.value)} style={{height:40,padding:'0 12px',borderRadius:10,border:'1px solid var(--border)',background:'var(--input-background)'}}/>
      <input placeholder="Password" type="password" value={p} onChange={e=>setP(e.target.value)} style={{height:40,padding:'0 12px',borderRadius:10,border:'1px solid var(--border)',background:'var(--input-background)'}}/>
      <button type="submit" style={{height:40,borderRadius:999,background:'var(--accent)',color:'#fff',border:'none',cursor:'pointer',fontWeight:600}}>Log in</button>
      <div style={{fontSize:13,color:'var(--text-secondary)',textAlign:'center'}}>No account? <Link to="/register" style={{color:'var(--accent)'}}>Register</Link></div>
    </form>
  </div>
}
