import React from 'react'
import { Outlet } from 'react-router-dom'
import { GlobalStateProvider } from './context/GlobalStateContext'
import Navbar from './components/Navbar'
import VoiceAssistant from './components/VoiceAssistant'
import Footer from './components/Footer'

const App = () => {
  return (
    <GlobalStateProvider>
      <Navbar />
      <Outlet />
      <VoiceAssistant />
      <Footer />
    </GlobalStateProvider>
  )
}

export default App