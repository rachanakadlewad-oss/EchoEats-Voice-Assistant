import React, { useState, useContext } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import "./CSS/Login.css"
import { GlobalStateContext } from '../context/GlobalStateContext'
const LoginPage = () => {
  const [isLogin, setIsLogin] = useState(true)
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  
  const { login } = useContext(GlobalStateContext)
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || '/'

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")

    try {
      if (isLogin) {
        const response = await fetch("http://localhost:3000/login/", {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, password })
        })
        
        const data = await response.json()
        
        if (response.ok) {
          login(data.user)
          navigate(from, { replace: true })
        } else {
          setError(data.error)
        }
      } else {
        const response = await fetch("http://localhost:3000/signup/", {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ name, email, password })
        })
        
        const data = await response.json()
        
        if (response.ok) {
          login(data.user)
          navigate(from, { replace: true })
        } else {
          setError(data.error)
        }
      }
    } catch (error) {
      setError("Server error. Please try again.")
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

        <button type="submit" className="login-button">
          {isLogin ? "Login" : "Sign Up"}
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