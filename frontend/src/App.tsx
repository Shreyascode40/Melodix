import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import { AuthProvider } from './context/AuthContext'
import { PlayerProvider } from './context/PlayerContext'
import Sidebar from './components/layout/Sidebar'
import Header from './components/layout/Header'
import MobileNav from './components/layout/MobileNav'
import MusicPlayer from './components/player/MusicPlayer'
import Home from './pages/Home'
import Search from './pages/Search'
import Library from './pages/Library'
import Playlists from './pages/Playlists'
import Playlist from './pages/Playlist'
import ScreenshotImport from './pages/ScreenshotImport'
import Login from './pages/Login'
import Register from './pages/Register'
import Settings from './pages/Settings'
import Profile from './pages/Profile'

function Shell(){
  return <div style={{display:'flex',minHeight:'100vh'}}>
    <div style={{width:80}} className="hide-mobile"><Sidebar/></div>
    <style>{`@media(max-width:768px){.hide-mobile{display:none}.main{margin-left:0!important}}`}</style>
    <div className="main" style={{flex:1,marginLeft:0,marginBottom:72,background:'var(--background)'}}>
      <Header/>
      <Routes>
        <Route path="/" element={<Home/>}/>
        <Route path="/search" element={<Search/>}/>
        <Route path="/explore" element={<Home/>}/>
        <Route path="/library" element={<Library/>}/>
        <Route path="/liked" element={<Library/>}/>
        <Route path="/playlists" element={<Playlists/>}/>
        <Route path="/playlists/:id" element={<Playlist/>}/>
        <Route path="/screenshot-import" element={<ScreenshotImport/>}/>
        <Route path="/settings" element={<Settings/>}/>
        <Route path="/profile" element={<Profile/>}/>
        <Route path="/login" element={<Login/>}/>
        <Route path="/register" element={<Register/>}/>
        <Route path="*" element={<Navigate to="/" />}/>
      </Routes>
    </div>
    <MobileNav/>
    <MusicPlayer/>
  </div>
}

export default function App(){
  return <ThemeProvider><AuthProvider><PlayerProvider>
    <BrowserRouter><Shell/></BrowserRouter>
  </PlayerProvider></AuthProvider></ThemeProvider>
}
