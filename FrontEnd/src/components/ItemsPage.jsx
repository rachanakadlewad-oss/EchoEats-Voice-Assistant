import React, { useState, useEffect, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import './CSS/Items.css'
import { GlobalStateContext } from '../context/GlobalStateContext'

const ItemsPage = () => {
    const { foodData, updateQuantity } = useContext(GlobalStateContext)
    const [selectedCategory, setSelectedCategory] = useState('All')
    const [categories, setCategories] = useState([])
    const [searchQuery, setSearchQuery] = useState('')
    const [previewItem, setPreviewItem] = useState(null)
    const [modalQty, setModalQty] = useState(1)
    const [toastMessage, setToastMessage] = useState('')
    const navigate = useNavigate()

    const categoryIcons = {
        'All': '🍽️',
        'Pizza': '🍕',
        'Burger': '🍔',
        'Main Course': '🍛',
        'Snacks': '🥟',
        'Dessert': '🍰',
    }

    useEffect(() => {
        if (foodData.length > 0) {
            const uniqueCategories = ['All', ...new Set(foodData.map(item => item.Category).filter(Boolean))]
            setCategories(uniqueCategories)
        }
    }, [foodData])

    // Filter items based on category and search query
    const filteredItems = foodData.filter(item => {
        const matchesCategory = selectedCategory === 'All' || item.Category === selectedCategory
        const matchesSearch = !searchQuery || 
            item.FoodName.toLowerCase().includes(searchQuery.toLowerCase()) ||
            (item.Description && item.Description.toLowerCase().includes(searchQuery.toLowerCase()))
        return matchesCategory && matchesSearch
    })

    const showToast = (msg) => {
        setToastMessage(msg)
        setTimeout(() => {
            setToastMessage('')
        }, 2500)
    }

    const handleQuantityChange = async (e, item, delta) => {
        e.stopPropagation() // prevent opening modal
        await updateQuantity(item.FoodID, delta)
        if (delta > 0) {
            showToast(`Added ${item.FoodName} to cart! 🛒`)
        }
    }

    const openPreview = (item) => {
        setPreviewItem(item)
        setModalQty(item.Quantity > 0 ? item.Quantity : 1)
    }

    const closePreview = () => {
        setPreviewItem(null)
    }

    const handleModalAdd = async () => {
        if (!previewItem) return
        const currentQty = previewItem.Quantity || 0
        const delta = modalQty - currentQty
        if (delta !== 0) {
            await updateQuantity(previewItem.FoodID, delta)
        }
        showToast(`Updated ${previewItem.FoodName} in cart! 🛒`)
        closePreview()
    }

    const handleModalBuyNow = async () => {
        if (!previewItem) return
        const currentQty = previewItem.Quantity || 0
        const delta = modalQty - currentQty
        if (delta !== 0) {
            await updateQuantity(previewItem.FoodID, delta)
        }
        closePreview()
        navigate('/cart')
    }

    return (
        <section className="menu-section" id="items">
            {/* Toast Notification */}
            {toastMessage && (
                <div className="cart-toast-notification">
                    <span>{toastMessage}</span>
                </div>
            )}

            {/* Menu Header */}
            <div className="menu-header">
                <span className="menu-badge">CHEF'S SPECIAL SELECTION</span>
                <h2 className="menu-title">Explore Our Delicious Menu</h2>
                <p className="menu-subtitle">
                    Hand-crafted recipes made with fresh, locally sourced ingredients. Click any card to customize!
                </p>

                {/* Search Bar */}
                <div className="search-bar-container">
                    <span className="search-icon">🔍</span>
                    <input 
                        type="text" 
                        placeholder="Search for pizza, biryani, burger..." 
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="search-input"
                    />
                    {searchQuery && (
                        <button className="clear-search-btn" onClick={() => setSearchQuery('')}>✕</button>
                    )}
                </div>
            </div>

            {/* Categories Filter Pills */}
            <div className='Categories'>
                <div className='categories-nav'>
                    {categories.map((category) => (
                        <button
                            key={category}
                            className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
                            onClick={() => setSelectedCategory(category)}
                        >
                            <span className="cat-icon">{categoryIcons[category] || '🍴'}</span>
                            <span className="cat-name">{category}</span>
                        </button>
                    ))}
                </div>
            </div>
            
            {/* Food Cards Grid */}
            {filteredItems.length === 0 ? (
                <div className="no-items-found">
                    <span className="no-items-emoji">🍽️</span>
                    <h3>No items found</h3>
                    <p>Try searching for a different dish or category.</p>
                    <button onClick={() => { setSearchQuery(''); setSelectedCategory('All'); }} className="reset-filter-btn">
                        View All Items
                    </button>
                </div>
            ) : (
                <div className="cards-grid">
                    {filteredItems.map((item) => {
                        const isVeg = !item.FoodName.toLowerCase().includes('chicken') && 
                                      !item.FoodName.toLowerCase().includes('pepperoni');

                        return (
                            <div 
                                key={item.FoodID} 
                                className="card"
                                onClick={() => openPreview(item)}
                                title="Click to view details & customize"
                            >
                                <div className="card-image-wrap">
                                    <img 
                                        src={`/${item.ImageName}`} 
                                        alt={item.FoodName}
                                        className="card-img"
                                        onError={(e) => {
                                            e.target.src = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop&q=80"
                                        }}
                                    />
                                    {/* Dietary Indicator Badge */}
                                    <div className={`diet-badge ${isVeg ? 'veg' : 'non-veg'}`}>
                                        <span className="diet-dot"></span>
                                    </div>

                                    {/* Rating Tag */}
                                    <div className="card-rating-tag">
                                        ⭐ {item.Rating ? parseFloat(item.Rating).toFixed(1) : '4.8'}
                                    </div>

                                    {/* Quick View Button on Hover */}
                                    <div className="card-quick-view-btn">
                                        <span>👁️ Quick View</span>
                                    </div>
                                </div>

                                <div className="card-content">
                                    <div className="card-top-row">
                                        <h3 className="card-title">{item.FoodName}</h3>
                                        <span className="card-price">₹{parseFloat(item.Price).toFixed(0)}</span>
                                    </div>

                                    <p className="card-description">
                                        {item.Description || "Freshly cooked gourmet delight packed with irresistible flavor."}
                                    </p>

                                    <div className="card-category-tag">
                                        {item.Category || 'Special'}
                                    </div>
                                </div>

                                <div className="card-footer" onClick={(e) => e.stopPropagation()}>
                                    {item.Quantity > 0 ? (
                                        <div className="quantity-controls">
                                            <button 
                                                className="quantity-btn minus"
                                                onClick={(e) => handleQuantityChange(e, item, -1)}
                                                aria-label="Decrease quantity"
                                            >
                                                -
                                            </button>
                                            <span className="quantity-display">{item.Quantity}</span>
                                            <button 
                                                className="quantity-btn plus"
                                                onClick={(e) => handleQuantityChange(e, item, 1)}
                                                aria-label="Increase quantity"
                                            >
                                                +
                                            </button>
                                        </div>
                                    ) : (
                                        <button 
                                            className="add-btn" 
                                            onClick={(e) => handleQuantityChange(e, item, 1)}
                                        >
                                            <span>+ Add</span>
                                        </button>
                                    )}
                                </div>
                            </div>
                        )
                    })}
                </div>
            )}

            {/* Food Detail Modal */}
            {previewItem && (
                <div className="food-modal-overlay" onClick={closePreview}>
                    <div className="food-modal-content" onClick={(e) => e.stopPropagation()}>
                        <button className="modal-close-btn" onClick={closePreview} aria-label="Close modal">
                            ✕
                        </button>

                        <div className="modal-body-split">
                            <div className="modal-image-col">
                                <img 
                                    src={`/${previewItem.ImageName}`} 
                                    alt={previewItem.FoodName} 
                                    className="modal-food-img"
                                    onError={(e) => {
                                        e.target.src = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&auto=format&fit=crop&q=80"
                                    }}
                                />
                                <div className="modal-img-badges">
                                    <span className="modal-badge-cat">{previewItem.Category}</span>
                                    <span className="modal-badge-rating">⭐ {previewItem.Rating || '4.8'}</span>
                                    <span className="modal-badge-status">🟢 Freshly Prepared</span>
                                </div>
                            </div>

                            <div className="modal-details-col">
                                <h2 className="modal-title">{previewItem.FoodName}</h2>
                                <div className="modal-price-row">
                                    <span className="modal-price">₹{parseFloat(previewItem.Price).toFixed(0)}</span>
                                    <span className="modal-tax-note">inclusive of all taxes</span>
                                </div>

                                <div className="modal-divider"></div>

                                <h4 className="modal-section-title">About this dish</h4>
                                <p className="modal-description">
                                    {previewItem.Description || "Enjoy authentic gourmet taste crafted with precision, fresh spices, and premium ingredients."}
                                </p>

                                <div className="modal-highlights">
                                    <div className="highlight-pill">⚡ Ready in 15-20 mins</div>
                                    <div className="highlight-pill">🔥 Freshly cooked</div>
                                    <div className="highlight-pill">🌱 Quality assured</div>
                                </div>

                                <div className="modal-divider"></div>

                                {/* Quantity Selector */}
                                <div className="modal-quantity-row">
                                    <span className="quantity-label">Quantity:</span>
                                    <div className="modal-qty-stepper">
                                        <button 
                                            className="modal-qty-btn"
                                            onClick={() => setModalQty(Math.max(1, modalQty - 1))}
                                        >
                                            -
                                        </button>
                                        <span className="modal-qty-value">{modalQty}</span>
                                        <button 
                                            className="modal-qty-btn"
                                            onClick={() => setModalQty(modalQty + 1)}
                                        >
                                            +
                                        </button>
                                    </div>
                                    <div className="modal-subtotal">
                                        Total: <strong>₹{(parseFloat(previewItem.Price) * modalQty).toFixed(0)}</strong>
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="modal-actions-row">
                                    <button className="modal-btn-cart" onClick={handleModalAdd}>
                                        🛒 Add to Cart
                                    </button>
                                    <button className="modal-btn-buy" onClick={handleModalBuyNow}>
                                        ⚡ Buy Now
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </section>
    )
}

export default ItemsPage