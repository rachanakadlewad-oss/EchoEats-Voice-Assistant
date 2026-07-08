import React, { useState, useEffect, useContext } from 'react'
import './CSS/Items.css'
import { GlobalStateContext } from '../context/GlobalStateContext'

const ItemsPage = () => {
    const { foodData, updateQuantity } = useContext(GlobalStateContext)
    const [selectedCategory, setSelectedCategory] = useState('All')
    const [categories, setCategories] = useState([])

    useEffect(() => {
        if (foodData.length > 0) {
            const uniqueCategories = ['All', ...new Set(foodData.map(item => item.Category))]
            setCategories(uniqueCategories)
        }
    }, [foodData])

    const filteredItems = selectedCategory === 'All' 
        ? foodData 
        : foodData.filter(item => item.Category === selectedCategory)

    const handleQuantityChange = async (item, delta) => {
        await updateQuantity(item.FoodID, delta)
    }

    return (
        <>
        <div className='Categories' id='items'>
            <div className='categories-nav'>
                {categories.map((category) => (
                    <button
                        key={category}
                        className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
                        onClick={() => setSelectedCategory(category)}
                    >
                        {category}
                    </button>
                ))}
            </div>
        </div>
        
        <div className="cards-grid">
            {filteredItems.map((item) => (
                <div key={item.FoodID} className="card">
                    <div className="card-image">
                        <img 
                            src={item.ImageName} 
                            alt={item.FoodName}
                            onError={(e) => {
                                e.target.src = "https://via.placeholder.com/300x300/ff9f4b/ffffff?text=Food"
                            }}
                        />
                    </div>
                    <div className="card-content">
                        <h3 className="card-title">{item.FoodName}</h3>
                        <p className="card-price">₹{parseFloat(item.Price).toFixed(2)}</p>
                        <p className="card-description">{item.Description}</p>
                        <div className="card-category">{item.Category}</div>
                    </div>
                    <div className="card-footer">
                        {item.Quantity > 0 ? (
                            <div className="quantity-controls">
                                <button 
                                    className="quantity-btn"
                                    onClick={() => handleQuantityChange(item, -1)}
                                >
                                    -
                                </button>
                                <span className="quantity-display">{item.Quantity}</span>
                                <button 
                                    className="quantity-btn"
                                    onClick={() => handleQuantityChange(item, 1)}
                                >
                                    +
                                </button>
                            </div>
                        ) : (
                            <button 
                                className="add-btn" 
                                onClick={() => handleQuantityChange(item, 1)}
                            >
                                Add
                            </button>
                        )}
                    </div>
                </div>
            ))}
        </div>
        </>
    )
}

export default ItemsPage