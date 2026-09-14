import { createContext, useContext, useEffect, useState } from 'react'
import api from '../services/api'
type User={id:number;username:string;email:string;display_name:string;avatar_url:string|null}
type Ctx={user:User|null; loading:boolean; login:(u:string,p:string)=>Promise<void>; register:(d:any)=>Promise<void>; logout:()=>Promise<void>}
const AuthContext=createContext<Ctx>(null as any)
export const useAuth=()=>useContext(AuthContext)
export function AuthProvider({children}:{children:React.ReactNode}){
  const [user,setUser]=useState<User|null>(null)
  const [loading,setLoading]=useState(true)
  const load=async()=>{
    const t=localStorage.getItem('access')
    if(!t){ setLoading(false); return}
    try{ const r=await api.get('/auth/me/'); setUser(r.data)}catch{ localStorage.removeItem('access'); localStorage.removeItem('refresh')}
    setLoading(false)
  }
  useEffect(()=>{load()},[])
  const login=async(username:string,password:string)=>{
    const r=await api.post('/auth/login/',{username,password})
    localStorage.setItem('access',r.data.access); localStorage.setItem('refresh',r.data.refresh)
    const me=await api.get('/auth/me/'); setUser(me.data)
  }
  const register=async(d:any)=>{
    const r=await api.post('/auth/register/',d)
    localStorage.setItem('access',r.data.access); localStorage.setItem('refresh',r.data.refresh); setUser(r.data.user)
  }
  const logout=async()=>{
    try{ await api.post('/auth/logout/',{refresh:localStorage.getItem('refresh')})}catch{}
    localStorage.removeItem('access'); localStorage.removeItem('refresh'); setUser(null)
  }
  return <AuthContext.Provider value={{user,loading,login,register,logout}}>{children}</AuthContext.Provider>
}
