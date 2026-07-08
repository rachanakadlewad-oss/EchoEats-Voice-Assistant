import React from 'react'
import { Link } from 'react-router-dom'
import './CSS/Footer.css'

const Footer = () => {
  return (
    <div className='outerFooter'>
        <div className='Footer'>
            <div className='FooterContent'>
                <div className='FooterSection'>
                    <h3>About EchoEats</h3>
                    <ul>
                        <li><Link to="/about">Our Story</Link></li>
                        <li><Link to="/careers">Careers</Link></li>
                        <li><Link to="/press">Press</Link></li>
                        <li><Link to="/blog">Blog</Link></li>
                    </ul>
                </div>
                
                <div className='FooterSection'>
                    <h3>Quick Links</h3>
                    <ul>
                        <li><Link to="/home">Home</Link></li>
                        <li><Link to="/menu">Menu</Link></li>
                        <li><Link to="/offers">Login/SignUp</Link></li>
                        <li><Link to="/contact">Contact Us</Link></li>
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
                
                <div className='FooterSection'>
                    <h3>Follow Us</h3>
                    <div className='SocialIcons'>
                        <a href="https://www.facebook.com/vamshidu10/" target="_blank" rel="noopener noreferrer">FB</a>
                        <a href="https://x.com/vamshitwts" target="_blank" rel="noopener noreferrer">TW</a>
                        <a href="https://www.instagram.com/vamshidu/" target="_blank" rel="noopener noreferrer">IG</a>
                        <a href="https://www.linkedin.com/in/duvamshi/
                        " target="_blank" rel="noopener noreferrer">LI</a>
                    </div>
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