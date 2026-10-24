import React, { useEffect, useContext } from 'react'
import { Link } from 'react-router-dom'
import './CSS/Hero.css'
import ItemsPage from './ItemsPage'
import { GlobalStateContext } from '../context/GlobalStateContext'

const HomePage = () => {
  const { isLoggedIn, user, Quantity } = useContext(GlobalStateContext)

  useEffect(() => {
    // Only spawn particles if hero is rendered (logged out)
    if (!isLoggedIn) {
      const heroEl = document.querySelector('.outerHero')
      if (!heroEl) return

      const particles = document.createElement('div')
      particles.className = 'particles'
      
      for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div')
        particle.className = 'particle'
        particle.style.left = Math.random() * 100 + '%'
        particle.style.animationDelay = Math.random() * 10 + 's'
        particle.style.animationDuration = 10 + Math.random() * 10 + 's'
        particles.appendChild(particle)
      }
      
      heroEl.appendChild(particles)
      
      return () => {
        if (particles.parentNode) {
          particles.remove()
        }
      }
    }
  }, [isLoggedIn])

  const firstName = user?.name ? user.name.trim().split(' ')[0] : 'Foodie'

  return (
    <main className="home-container">
      {/* Show existing Hero section ONLY when logged out */}
      {!isLoggedIn ? (
        <div className='outerHero'>
            <div className='Hero'>
                <div className='HeroContent'>
                    <h1>
                        <span className='line'>DELICIOUS</span>
                        <span className='line'>
                            <span className='gradient-text'>FOOD</span>
                        </span>
                        <span className='line'>DELIVERED TO YOU</span>
                    </h1>
                    <p>Experience the best cuisine from top restaurants in your city. Fresh, hot, and delivered right to your doorstep in under 20 minutes.</p>
                    <div className='HeroButtons'>
                        <a href="#items">
                            <button className='HeroButtonPrimary'>ORDER NOW →</button>
                        </a>
                        <Link to="/about">
                            <button className='HeroButton'>LEARN MORE</button>
                        </Link>
                    </div>

                    <div className='HeroFeatures'>
                        <div className='feature-item'>
                            <span className='feature-number'>500+</span>
                            <span className='feature-label'>Restaurants</span>
                        </div>
                        <div className='feature-item'>
                            <span className='feature-number'>20min</span>
                            <span className='feature-label'>Delivery</span>
                        </div>
                        <div className='feature-item'>
                            <span className='feature-number'>50k+</span>
                            <span className='feature-label'>Happy Customers</span>
                        </div>
                    </div>
                </div>
                <div className='HeroImage'>
                    <div className='blob-1'></div>
                    <div className='blob-2'></div>
                    <img src="/ECHOEATS.png" alt="Delicious Food" />
                    <div className='floating-element floating-1'>⚡</div>
                    <div className='floating-element floating-2'>🔥</div>
                    <div className='floating-element floating-3'>🍕</div>
                </div>
            </div>
        </div>
      ) : (
        /* When logged in: Show food products directly with a welcome bar */
        <div className="logged-in-welcome-banner">
          <div className="welcome-banner-inner">
            <div className="welcome-text-col">
              <span className="welcome-badge">⚡ Quick Delivery • Under 20 Mins</span>
              <h1 className="welcome-title">
                Welcome back, <span className="welcome-highlight">{firstName}</span>!
              </h1>
              <p className="welcome-subtitle">
                Ready for lunch or dinner? Pick your favorites or use the voice assistant to order in seconds.
              </p>
            </div>
            <div className="welcome-quick-actions">
              <Link to="/orders" className="welcome-action-chip">
                <span>📦</span>
                <span>Track Orders</span>
              </Link>
              <Link to="/cart" className="welcome-action-chip cart-chip">
                <span>🛒</span>
                <span>Cart ({Quantity})</span>
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Food Products Section */}
      <ItemsPage />
    </main>
  )
}

export default HomePage