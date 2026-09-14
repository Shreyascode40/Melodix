import { createContext, useContext, useEffect, useState } from 'react'
type Theme='light'|'dark'|'system'
type Ctx={theme:Theme; resolved:'light'|'dark'; setTheme:(t:Theme)=>void; toggle:()=>void}
const ThemeContext=createContext<Ctx>(null as any)
export const useTheme=()=>useContext(ThemeContext)
export function ThemeProvider({children}:{children:React.ReactNode}){
  const [theme,setTheme]=useState<Theme>(()=>(localStorage.getItem('theme') as Theme)||'system')
  const [resolved,setResolved]=useState<'light'|'dark'>('light')
  const calc=(t:Theme):'light'|'dark'=> t==='system' ? (window.matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light') : t
  useEffect(()=>{
    const r=calc(theme)
    setResolved(r)
    document.documentElement.setAttribute('data-theme',r)
    localStorage.setItem('theme',theme)
  },[theme])
  useEffect(()=>{
    const m=window.matchMedia('(prefers-color-scheme:dark)')
    const h=()=>{ if(theme==='system'){ const r=m.matches?'dark':'light'; setResolved(r); document.documentElement.setAttribute('data-theme',r)}}
    m.addEventListener('change',h)
    return()=>m.removeEventListener('change',h)
  },[theme])
  const toggle=()=> setTheme(resolved==='dark'?'light':'dark')
  return <ThemeContext.Provider value={{theme,resolved,setTheme,toggle}}>{children}</ThemeContext.Provider>
}
