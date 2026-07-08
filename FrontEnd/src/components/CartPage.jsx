import React, { useEffect, useState, useContext, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import './CSS/Cart.css'
import { GlobalStateContext } from '../context/GlobalStateContext'

const CartPage = () => {
    const { Quantity, setQuantity, isLoggedIn, user, foodData, updateQuantity, fetchFoodData } = useContext(GlobalStateContext)
    const [cartItems, setCartItems] = useState([])
    const [total, setTotal] = useState(0)
    const [loading, setLoading] = useState(false)
    const [showPaymentModal, setShowPaymentModal] = useState(false)
    const [showOrderPopup, setShowOrderPopup] = useState(false)
    const [orderMessage, setOrderMessage] = useState('')
    const navigate = useNavigate()

    useEffect(() => {
        const itemsInCart = foodData.filter(item => item.Quantity > 0)
        setCartItems(itemsInCart)
        
        const totalPrice = itemsInCart.reduce((sum, item) => 
            sum + (parseFloat(item.Price) * item.Quantity), 0
        )
        setTotal(totalPrice)
    }, [foodData]) 

    useEffect(() => {
        if (window.location.hash === '#payment-modal' && isLoggedIn) {
            setShowPaymentModal(true)
        }
    }, [isLoggedIn])

    const handleIncreaseQuantity = async (item) => {
        await updateQuantity(item.FoodID, 1)
    }

    const handleDecreaseQuantity = async (item) => {
        if (item.Quantity > 1) {
            await updateQuantity(item.FoodID, -1)
        } else {
            await handleRemoveItem(item)
        }
    }

    const handleRemoveItem = async (item) => {
        const currentQuantity = item.Quantity
        await updateQuantity(item.FoodID, -currentQuantity)
    }

    const handleCheckout = () => {
        if (!isLoggedIn) {
            navigate('/login', { state: { from: { pathname: '/cart' } } })
            return
        }
        setShowPaymentModal(true)
        window.location.hash = 'payment-modal'
    }

    const handleCOD = async () => {
        setShowPaymentModal(false)
        window.location.hash = ''
        setLoading(true)

        try {
            const orderResponse = await fetch("http://localhost:3000/create-order/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    userId: user.user_id,
                    amount: total,
                    items: cartItems,
                    paymentMethod: 'COD'
                })
            })

            const orderData = await orderResponse.json()

            if (orderData.success) {
                setOrderMessage('Order placed successfully! Your food will be delivered soon.')
                setShowOrderPopup(true)

                for (const item of cartItems) {
                    await updateQuantity(item.FoodID, -item.Quantity)
                }

                setTimeout(() => {
                    setOrderMessage('Your order has been delivered! Enjoy your meal! 🍕')
                    setShowOrderPopup(true)
                    
                    setTimeout(() => {
                        setShowOrderPopup(false)
                    }, 3000)
                }, 35000)

                setTimeout(() => {
                    setShowOrderPopup(false)
                }, 3000)

                navigate('/orders')
            }
        } catch (error) {
            console.error("Order error:", error)
            alert("Failed to place order")
        } finally {
            setLoading(false)
        }
    }

    const handleUPI = async () => {
    setShowPaymentModal(false)
    window.location.hash = ''
    setLoading(true)

    try {
        const orderResponse = await fetch("http://localhost:3000/create-order/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userId: user.user_id,
                amount: total,
                items: cartItems,
                paymentMethod: 'UPI'
            })
        })

        const orderData = await orderResponse.json()
        
        if (!orderData.success) {
            throw new Error(orderData.error || "Failed to create order")
        }

        if (!window.Razorpay) {
            await new Promise((resolve, reject) => {
                const script = document.createElement('script')
                script.src = 'https://checkout.razorpay.com/v1/checkout.js'
                script.onload = resolve
                script.onerror = reject
                document.body.appendChild(script)
            })
        }

        const options = {
            key: 'rzp_test_SdTWYyzys8e6Zq',
            amount: total * 100,
            currency: 'INR',
            name: 'EchoEats',
            description: 'Food Order Payment',
            order_id: orderData.razorpayOrderId,
            handler: async (response) => {
                try {
                    const verifyResponse = await fetch("http://localhost:3000/verify-payment/", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_signature: response.razorpay_signature,
                            orderId: orderData.orderId
                        })
                    })

                    const verifyData = await verifyResponse.json()

                    if (verifyData.success) {
                        setOrderMessage('Payment successful! Order placed successfully!')
                        setShowOrderPopup(true)

                        // Clear cart
                        for (const item of cartItems) {
                            await updateQuantity(item.FoodID, -item.Quantity)
                        }

     
                        setTimeout(() => {
                            setOrderMessage('Your order has been delivered! Enjoy your meal! 🍕')
                            setShowOrderPopup(true)
                            setTimeout(() => {
                                setShowOrderPopup(false)
                            }, 3000)
                        }, 35000)

                    
                        setTimeout(() => {
                            setShowOrderPopup(false)
                        }, 3000)

                        navigate('/orders')
                    } else {
                        throw new Error(verifyData.error || "Payment verification failed")
                    }
                } catch (error) {
                    console.error("Verification error:", error)
                    alert("Payment verification failed: " + error.message)
                }
            },
            prefill: {
                name: user.name,
                email: user.email
            },
            theme: {
                color: '#a75e3d'
            },
            modal: {
                ondismiss: () => {
                    console.log("Payment modal closed")
                    setLoading(false)
                }
            }
        }

        const razorpay = new window.Razorpay(options)
        razorpay.on('payment.failed', (response) => {
            console.error("Payment failed:", response.error)
            alert(`Payment failed: ${response.error.description}`)
            setLoading(false)
        })
        razorpay.open()
        
    } catch (error) {
        console.error("Payment error:", error)
        alert("Payment failed: " + error.message)
        setLoading(false)
    } finally {
        
    }
}

    return (
        <div className="cart-container">
            {showOrderPopup && (
                <div className="order-popup">
                    <p>{orderMessage}</p>
                </div>
            )}

            {showPaymentModal && (
                <div className="payment-modal" id='payment-modal'>
                    <div className="payment-modal-content">
                        <h3>Select Payment Method</h3>
                        <button 
                            className="payment-option cod" 
                            onClick={handleCOD}
                            disabled={loading}
                        >
                            💵 Cash on Delivery
                        </button>
                        <button 
                            className="payment-option upi" 
                            onClick={handleUPI}
                            disabled={loading}
                        >
                            📱 UPI / Card / NetBanking
                        </button>
                        <button 
                            className="payment-option cancel" 
                            onClick={() => {
                                setShowPaymentModal(false)
                                window.location.hash = ''
                            }}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}

            <h1>Your Cart</h1>
            {cartItems.length === 0 ? (
                <div className="empty-cart">
                    <h2>Your cart is empty</h2>
                    <p>Add some delicious items from our menu!</p>
                    <button onClick={() => navigate('/')}>Browse Menu</button>
                </div>
            ) : (
                <>
                    <div className="cart-items">
                        {cartItems.map((item) => (
                            <div key={item.FoodID} className="cart-item">
                                <img src={item.ImageName} alt={item.FoodName} />
                                <div className="cart-item-details">
                                    <h3>{item.FoodName}</h3>
                                    <p>₹{parseFloat(item.Price).toFixed(2)}</p>
                                </div>
                                <div className="cart-item-quantity">
                                    <button onClick={() => handleDecreaseQuantity(item)}>-</button>
                                    <span>{item.Quantity}</span>
                                    <button onClick={() => handleIncreaseQuantity(item)}>+</button>
                                </div>
                                <div className="cart-item-total">
                                    ₹{(parseFloat(item.Price) * item.Quantity).toFixed(2)}
                                </div>
                                <button className="remove-btn" onClick={() => handleRemoveItem(item)}>
                                    Remove
                                </button>
                            </div>
                        ))}
                    </div>
                    <div className="cart-total">
                        <h3>Total: ₹{total.toFixed(2)}</h3>
                        <button 
                            className="checkout-btn" 
                            onClick={handleCheckout}
                            disabled={loading}
                        >
                            {loading ? 'Processing...' : 'Proceed to Checkout'}
                        </button>
                    </div>
                </>
            )}
        </div>
    )
}

export default CartPage