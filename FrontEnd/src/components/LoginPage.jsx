import React, { useState, useContext, useEffect } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import "./CSS/Login.css"
import { GlobalStateContext } from '../context/GlobalStateContext'
const LoginPage = () => {
  const [isLogin, setIsLogin] = useState(true)
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  
  const { login, isLoggedIn } = useContext(GlobalStateContext)
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || '/'

  useEffect(() => {
    if (isLoggedIn) {
      navigate(from, { replace: true })
    }
  }, [isLoggedIn, navigate, from])

  const [submitting, setSubmitting] = useState(false)
  const API_URL = (import.meta.env.VITE_API_URL || (import.meta.env.PROD ? 'https://echoeats-voice-assistant-1.onrender.com' : 'http://localhost:8000')).replace(/\/+$/, '')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")

    const cleanEmail = email.trim().toLowerCase()
    const cleanPassword = password.trim()
    const cleanName = name.trim()

    if (!cleanEmail || !cleanPassword) {
      setError("Please fill in all required fields.")
      return
    }

    if (!isLogin && !cleanName) {
      setError("Please enter your full name.")
      return
    }

    if (!isLogin && cleanPassword.length < 6) {
      setError("Password must be at least 6 characters.")
      return
    }

    setSubmitting(true)

    try {
      if (isLogin) {
        const response = await fetch(`${API_URL}/login/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email: cleanEmail, password: cleanPassword })
        })
        
        const data = await response.json()
        
        if (response.ok && data.success) {
          login(data.user)
          navigate(from, { replace: true })
        } else {
          setError(data.error || "Login failed. Please check your credentials.")
        }
      } else {
        const response = await fetch(`${API_URL}/signup/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ name: cleanName, email: cleanEmail, password: cleanPassword })
        })
        
        const data = await response.json()
        
        if (response.ok && data.success) {
          login(data.user)
          navigate(from, { replace: true })
        } else {
          setError(data.error || "Signup failed. Please try again.")
        }
      }
    } catch (err) {
      console.error("Auth request error:", err)
      setError("Unable to connect to the backend server. Please verify your connection.")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-card">
        <h2>{isLogin ? "Login" : "Sign Up"}</h2>
        
        {error && <div className="error-message">{error}</div>}

        {!isLogin && (
          <input
            type="text"
            placeholder="Full Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="login-input"
            required
          />
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="login-input"
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="login-input"
          required
        />

        <button type="submit" className="login-button" disabled={submitting}>
          {submitting ? (isLogin ? "Signing In..." : "Creating Account...") : (isLogin ? "Login" : "Sign Up")}
        </button>

        <p className="login-toggle">
          {isLogin ? "Don't have an account?" : "Already have an account?"}
          <span onClick={() => setIsLogin(!isLogin)}>
            {" "}
            {isLogin ? "Sign Up" : "Login"}
          </span>
        </p>
      </form>
    </div>
  )
}

export default LoginPage