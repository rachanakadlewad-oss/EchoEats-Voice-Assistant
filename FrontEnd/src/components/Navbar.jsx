import React, { useState } from 'react'
import { Link } from 'react-router-dom';
import './CSS/Navbar.css'
import { GlobalStateContext } from '../context/GlobalStateContext'
import { useContext } from 'react';

const Navbar = () => {
  const { displayCart, isLoggedIn, user, logout } = useContext(GlobalStateContext)
  const [showDropdown, setShowDropdown] = useState(false)
  
  const getInitials = () => {
    if (!user || !user.name) return '?'
    const names = user.name.split(' ')
    if (names.length > 1) {
      return (names[0].charAt(0) + names[1].charAt(0)).toUpperCase()
    }
    return user.name.slice(0, 2).toUpperCase()
  }

  const handleLogout = () => {
    setShowDropdown(false)
    logout()
  }

  return (
    <div className='outerNavbar'>
        <div className='Navbar'>
            <div className='LogoImage'>
                <img src="ECHOEATS.png" alt="" />
            </div>
            <div className='NavButtons'>
                <Link to="/"><button className='navbut'>Home</button></Link>
                <Link to="/about"><button className='navbut'>About</button></Link>
                {isLoggedIn && (
                  <Link to="/orders"><button className='navbut'>Orders</button></Link>
                )}
                {displayCart && (
                  <Link to="/cart"><button className='navbut'>Cart</button></Link>
                )}
                
                {isLoggedIn ? (
                  <div className="user-profile">
                    <div 
                      className="profile-circle" 
                      onClick={() => setShowDropdown(!showDropdown)}
                    >
                      {getInitials()}
                    </div>
                    
                    {showDropdown && (
                      <div className="profile-dropdown">
                        <Link to="/profile" onClick={() => setShowDropdown(false)}>
                          <div className="dropdown-item">
                            <span className="dropdown-icon">👤</span>
                            Profile
                          </div>
                        </Link>
                        <Link to="/orders" onClick={() => setShowDropdown(false)}>
                          <div className="dropdown-item">
                            <span className="dropdown-icon">📦</span>
                            My Orders
                          </div>
                        </Link>
                        <div className="dropdown-divider"></div>
                        <div className="dropdown-item logout" onClick={handleLogout}>
                          <span className="dropdown-icon">🚪</span>
                          Logout
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <Link to="/login"><button className='navbutloin'>Login/SignUp</button></Link>
                )}
            </div>
        </div>
    </div>
  )
}

export default Navbar