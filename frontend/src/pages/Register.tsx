import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate, Link } from 'react-router-dom'
export default function Register(){
  const {register}=useAuth(); const nav=useNavigate()
  const [form,setForm]=useState({username:'',email:'',password:'',display_name:''}); const [err,setErr]=useState('')
  const submit=async(e:any)=>{ e.preventDefault(); setErr(''); try{ await register(form); nav('/')}catch(e:any){ setErr(JSON.stringify(e.response?.data||'Failed'))}}
  return <div style={{minHeight:'60vh',display:'grid',placeItems:'center',padding:24}}>
    <form onSubmit={submit} style={{width:380,background:'var(--surface)',border:'1px solid var(--border)',borderRadius:16,padding:24,display:'grid',gap:12}}>
      <h2 style={{margin:0}}>Create account</h2>
      {err&&<div style={{color:'#ef4444',fontSize:12,wordBreak:'break-all'}}>{err}</div>}
      <input placeholder="Username" required value={form.username} onChange={e=>setForm({...form,username:e.target.value})} style={{height:40,padding:'0 12px',borderRadius:10,border:'1px solid var(--border)',background:'var(--input-background)'}}/>
      <input placeholder="Email" type="email" required value={form.email} onChange={e=>setForm({...form,email:e.target.value})} style={{height:40,padding:'0 12px',borderRadius:10,border:'1px solid var(--border)',background:'var(--input-background)'}}/>
      <input placeholder="Display name" value={form.display_name} onChange={e=>setForm({...form,display_name:e.target.value})} style={{height:40,padding:'0 12px',borderRadius:10,border:'1px solid var(--border)',background:'var(--input-background)'}}/>
      <input placeholder="Password (min 8)" type="password" required value={form.password} onChange={e=>setForm({...form,password:e.target.value})} style={{height:40,padding:'0 12px',borderRadius:10,border:'1px solid var(--border)',background:'var(--input-background)'}}/>
      <button type="submit" style={{height:40,borderRadius:999,background:'var(--accent)',color:'#fff',border:'none',cursor:'pointer',fontWeight:600}}>Create account</button>
      <div style={{fontSize:13,color:'var(--text-secondary)',textAlign:'center'}}>Have account? <Link to="/login" style={{color:'var(--accent)'}}>Log in</Link></div>
    </form>
  </div>
}
