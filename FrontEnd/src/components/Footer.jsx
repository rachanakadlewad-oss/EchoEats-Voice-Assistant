import React, { useContext } from 'react'
import { Link } from 'react-router-dom'
import './CSS/Footer.css'
import { GlobalStateContext } from '../context/GlobalStateContext'

const Footer = () => {
  const { isLoggedIn } = useContext(GlobalStateContext)

  return (
    <div className='outerFooter'>
        <div className='Footer'>
            <div className='FooterContent'>
                <div className='FooterSection'>
                    <h3>EchoEats Dining</h3>
                    <ul>
                        {!isLoggedIn && <li><Link to="/about">Our Story</Link></li>}
                        <li><Link to="/#items">Featured Delights</Link></li>
                        <li><Link to="/cart">Shopping Basket</Link></li>
                        {isLoggedIn && <li><Link to="/orders">Order History</Link></li>}
                    </ul>
                </div>
                
                <div className='FooterSection'>
                    <h3>Quick Links</h3>
                    <ul>
                        <li><Link to="/">Home</Link></li>
                        <li><Link to="/#items">Explore Menu</Link></li>
                        {!isLoggedIn ? (
                          <li><Link to="/login">Login / Sign Up</Link></li>
                        ) : (
                          <li><Link to="/profile">My Profile</Link></li>
                        )}
                        <li><Link to="/cart">Cart</Link></li>
                    </ul>
                </div>
                
                <div className='FooterSection'>
                    <h3>Support</h3>
                    <ul>
                        <li><Link to="/faq">FAQ</Link></li>
                        <li><Link to="/terms">Terms of Service</Link></li>
                        <li><Link to="/privacy">Privacy Policy</Link></li>
                        <li><Link to="/help">Help Center</Link></li>
                    </ul>
                </div>
            </div>
            
            <div className='FooterBottom'>
                <p>&copy; 2026 EchoEats. All rights reserved. | Designed with ❤️ for food lovers</p>
            </div>
        </div>
    </div>
  )
}

export default Footer