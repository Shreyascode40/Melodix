import axios from 'axios'
const api=axios.create({baseURL:'/api'})
api.interceptors.request.use(c=>{ const t=localStorage.getItem('access'); if(t) c.headers.Authorization=`Bearer ${t}`; return c})
api.interceptors.response.use(r=>r, async err=>{
  const orig=err.config
  if(err.response?.status===401 && !orig._retry && localStorage.getItem('refresh')){
    orig._retry=true
    try{
      const r=await axios.post('/api/auth/token/refresh/',{refresh:localStorage.getItem('refresh')})
      localStorage.setItem('access',r.data.access); orig.headers.Authorization=`Bearer ${r.data.access}`; return api(orig)
    }catch{ localStorage.removeItem('access'); localStorage.removeItem('refresh')}
  }
  return Promise.reject(err)
})
export default api
