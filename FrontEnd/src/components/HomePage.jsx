import React, { useEffect } from 'react'
import { Link } from 'react-router-dom'
import './CSS/Hero.css'
import ItemsPage from './ItemsPage';

const HomePage = () => {
  useEffect(() => {
    const particles = document.createElement('div');
    particles.className = 'particles';
    
    for (let i = 0; i < 20; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';
      particle.style.left = Math.random() * 100 + '%';
      particle.style.animationDelay = Math.random() * 10 + 's';
      particle.style.animationDuration = 10 + Math.random() * 10 + 's';
      particles.appendChild(particle);
    }
    
    document.querySelector('.outerHero').appendChild(particles);
    
    return () => {
      if (particles.parentNode) {
        particles.remove();
      }
    };
  }, []);

  return (
    <>
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
                    <img src="ECHOEATS.png" alt="Delicious Food" />
                    <div className='floating-element floating-1'>⚡</div>
                    <div className='floating-element floating-2'>🔥</div>
                    <div className='floating-element floating-3'>🍕</div>
                </div>
            </div>
        </div>
        <ItemsPage  />
        
    </>

  )
}

export default HomePage