import React, { useState, useEffect, useRef, useContext } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import './CSS/Navbar.css'
import { GlobalStateContext } from '../context/GlobalStateContext'

const Navbar = () => {
  const { Quantity, isLoggedIn, user, logout, Togg, setTogg } = useContext(GlobalStateContext)
  const [showDropdown, setShowDropdown] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const dropdownRef = useRef(null)
  const location = useLocation()
  const navigate = useNavigate()

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false)
    setShowDropdown(false)
  }, [location])

  const getInitials = () => {
    if (!user || !user.name) return 'U'
    const names = user.name.trim().split(' ')
    if (names.length > 1) {
      return (names[0].charAt(0) + names[1].charAt(0)).toUpperCase()
    }
    return user.name.slice(0, 2).toUpperCase()
  }

  const handleLogout = () => {
    setShowDropdown(false)
    setMobileMenuOpen(false)
    logout()
  }

  const scrollToMenu = () => {
    if (location.pathname !== '/') {
      navigate('/#items')
    } else {
      const el = document.getElementById('items')
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' })
      }
    }
    setMobileMenuOpen(false)
  }

  return (
    <header className="outerNavbar">
      <nav className="Navbar">
        {/* Brand Logo */}
        <Link to="/" className="BrandLink">
          <div className="LogoImageWrapper">
            <img src="/ECHOEATS.png" alt="EchoEats Logo" className="BrandLogo" />
          </div>
          <div className="BrandText">
            <span className="BrandTitle">Echo<span className="BrandAccent">Eats</span></span>
            <span className="BrandTagline">Voice & Gourmet</span>
          </div>
        </Link>

        {/* Desktop Nav Links */}
        <div className="NavButtons">
          <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>
            Home
          </Link>

          <button onClick={scrollToMenu} className="nav-link menu-link-btn">
            Menu
          </button>

          {!isLoggedIn && (
            <Link to="/about" className={`nav-link ${location.pathname === '/about' ? 'active' : ''}`}>
              About
            </Link>
          )}

          {isLoggedIn && (
            <Link to="/orders" className={`nav-link ${location.pathname === '/orders' ? 'active' : ''}`}>
              Orders
            </Link>
          )}

          {/* Voice Assistant Toggle in Navbar */}
          <button 
            type="button"
            className={`nav-voice-btn ${!Togg ? 'voice-active' : ''}`}
            onClick={() => setTogg(prev => !prev)}
            title={!Togg ? "Voice Assistant Active (Click to Hide)" : "Click to Open Voice Assistant"}
          >
            <span className="mic-icon">🎙️</span>
            <span className="voice-text">{!Togg ? 'Voice On' : 'Voice'}</span>
            {!Togg && <span className="voice-pulse-dot"></span>}
          </button>

          {/* Cart Button with dynamic badge */}
          <Link to="/cart" className="nav-cart-btn" title="View Cart">
            <span className="cart-icon">🛒</span>
            <span className="cart-label">Cart</span>
            <span className={`cart-badge ${Quantity > 0 ? 'has-items' : ''}`}>
              {Quantity}
            </span>
          </Link>

          {/* User Profile or Login */}
          {isLoggedIn ? (
            <div className="user-profile" ref={dropdownRef}>
              <button 
                type="button"
                className="profile-circle" 
                onClick={() => setShowDropdown(!showDropdown)}
                aria-label="User Profile"
              >
                {getInitials()}
              </button>
              
              {showDropdown && (
                <div className="profile-dropdown">
                  <div className="dropdown-header">
                    <div className="dropdown-user-name">{user?.name || 'Customer'}</div>
                    <div className="dropdown-user-email">{user?.email || ''}</div>
                  </div>
                  <div className="dropdown-divider"></div>
                  
                  <Link to="/profile" onClick={() => setShowDropdown(false)} className="dropdown-item">
                    <span className="dropdown-icon">👤</span>
                    <span>My Profile</span>
                  </Link>
                  
                  <Link to="/orders" onClick={() => setShowDropdown(false)} className="dropdown-item">
                    <span className="dropdown-icon">📦</span>
                    <span>My Orders</span>
                  </Link>

                  <Link to="/cart" onClick={() => setShowDropdown(false)} className="dropdown-item">
                    <span className="dropdown-icon">🛍️</span>
                    <span>View Cart ({Quantity})</span>
                  </Link>
                  
                  <div className="dropdown-divider"></div>
                  <button type="button" className="dropdown-item logout" onClick={handleLogout}>
                    <span className="dropdown-icon">🚪</span>
                    <span>Log Out</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link to="/login" className="nav-login-btn">
              <span>Sign In</span>
              <span className="login-arrow">→</span>
            </Link>
          )}
        </div>

        {/* Mobile Hamburger Toggle */}
        <button 
          className={`mobile-hamburger ${mobileMenuOpen ? 'open' : ''}`}
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle Navigation"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
      </nav>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="mobile-nav-drawer">
          <Link to="/" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">
            🏠 Home
          </Link>
          <button onClick={scrollToMenu} className="mobile-nav-link text-left">
            🍕 Explore Menu
          </button>
          {!isLoggedIn && (
            <Link to="/about" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">
              ℹ️ About Us
            </Link>
          )}
          {isLoggedIn && (
            <Link to="/orders" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">
              📦 My Orders
            </Link>
          )}
          <Link to="/cart" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">
            🛒 Cart ({Quantity} items)
          </Link>
          <button 
            onClick={() => { setTogg(prev => !prev); setMobileMenuOpen(false); }}
            className="mobile-nav-link text-left"
          >
            🎙️ Voice Assistant ({!Togg ? 'Active' : 'Closed'})
          </button>

          <div className="mobile-nav-divider"></div>

          {isLoggedIn ? (
            <>
              <Link to="/profile" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">
                👤 Profile ({user?.name})
              </Link>
              <button onClick={handleLogout} className="mobile-nav-link text-left logout-link">
                🚪 Sign Out
              </button>
            </>
          ) : (
            <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="mobile-login-action">
              Sign In / Register
            </Link>
          )}
        </div>
      )}
    </header>
  )
}

export default Navbar