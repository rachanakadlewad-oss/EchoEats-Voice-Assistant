import React, { useEffect, useState, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import './CSS/Cart.css'
import { GlobalStateContext } from '../context/GlobalStateContext'

const CartPage = () => {
    const { isLoggedIn, user, foodData, updateQuantity, clearCart } = useContext(GlobalStateContext)
    const [cartItems, setCartItems] = useState([])
    const [subtotal, setSubtotal] = useState(0)
    const [couponCode, setCouponCode] = useState('')
    const [discount, setDiscount] = useState(0)
    const [appliedCoupon, setAppliedCoupon] = useState('')
    const [couponError, setCouponError] = useState('')
    
    // Checkout state
    const [isCheckoutOpen, setIsCheckoutOpen] = useState(false)
    const [checkoutStep, setCheckoutStep] = useState(1) // 1: Address, 2: Summary, 3: Payment, 4: Success
    const [loading, setLoading] = useState(false)
    const [confirmedOrder, setConfirmedOrder] = useState(null)
    
    // Delivery Address Management (ShopVerse-like)
    const [addresses, setAddresses] = useState([])
    const [selectedAddressId, setSelectedAddressId] = useState(null)
    const [showNewAddressForm, setShowNewAddressForm] = useState(false)
    const [newAddress, setNewAddress] = useState({
        fullName: '',
        phone: '',
        street: '',
        city: '',
        state: 'Karnataka',
        pincode: '',
        type: 'Home',
        landmark: ''
    })
    const [deliveryNotes, setDeliveryNotes] = useState('')
    const [paymentMethod, setPaymentMethod] = useState('COD')

    const navigate = useNavigate()
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    // Sync cart items from foodData
    useEffect(() => {
        const items = foodData.filter(item => (item.Quantity || 0) > 0)
        setCartItems(items)
        const sum = items.reduce((acc, item) => acc + (parseFloat(item.Price) * item.Quantity), 0)
        setSubtotal(sum)
    }, [foodData])

    // Load saved addresses for user
    useEffect(() => {
        const storageKey = user ? `echoeats_addresses_${user.user_id}` : 'echoeats_guest_addresses'
        const saved = localStorage.getItem(storageKey)
        if (saved) {
            try {
                const parsed = JSON.parse(saved)
                setAddresses(parsed)
                if (parsed.length > 0) {
                    setSelectedAddressId(parsed[0].id)
                }
            } catch (e) {
                console.error(e)
            }
        } else {
            // Default sample addresses
            const defaults = [
                {
                    id: 1,
                    fullName: user?.name || 'Alex Turner',
                    phone: '9876543210',
                    street: 'Flat 402, Green Valley Apartments, 12th Main Road',
                    landmark: 'Near Indiranagar Metro Station',
                    city: 'Bengaluru',
                    state: 'Karnataka',
                    pincode: '560038',
                    type: 'Home'
                },
                {
                    id: 2,
                    fullName: user?.name || 'Alex Turner',
                    phone: '9876543210',
                    street: 'Tech Park Blvd, Tower B, 3rd Floor',
                    landmark: 'Opposite Central Mall',
                    city: 'Bengaluru',
                    state: 'Karnataka',
                    pincode: '560100',
                    type: 'Work'
                }
            ]
            setAddresses(defaults)
            setSelectedAddressId(1)
            localStorage.setItem(storageKey, JSON.stringify(defaults))
        }

        if (user && user.name) {
            setNewAddress(prev => ({ ...prev, fullName: user.name }))
        }
    }, [user])

    // Auto-open payment modal if hash contains payment-modal
    useEffect(() => {
        if (window.location.hash === '#payment-modal' && cartItems.length > 0) {
            if (!isLoggedIn) {
                navigate('/login', { state: { from: { pathname: '/cart' } } })
            } else {
                setIsCheckoutOpen(true)
                setCheckoutStep(3)
            }
        }
    }, [isLoggedIn, cartItems.length])

    // Calculations
    const deliveryFee = subtotal > 300 || subtotal === 0 ? 0 : 40
    const taxes = Math.round(subtotal * 0.05)
    const grandTotal = Math.max(0, subtotal + deliveryFee + taxes - discount)

    // Coupon logic
    const handleApplyCoupon = (e) => {
        e.preventDefault()
        setCouponError('')
        const code = couponCode.trim().toUpperCase()
        if (code === 'ECHO50') {
            if (subtotal < 199) {
                setCouponError('Minimum order of ₹199 required for ECHO50')
                return
            }
            setDiscount(50)
            setAppliedCoupon('ECHO50 (₹50 OFF)')
            setCouponCode('')
        } else if (code === 'FEAST20') {
            const disc = Math.round(subtotal * 0.2)
            setDiscount(disc)
            setAppliedCoupon(`FEAST20 (20% OFF - ₹${disc})`)
            setCouponCode('')
        } else if (code === 'FREEDEL') {
            setDiscount(deliveryFee)
            setAppliedCoupon('FREEDEL (Free Delivery)')
            setCouponCode('')
        } else {
            setCouponError('Invalid coupon code. Try ECHO50 or FEAST20')
        }
    }

    const removeCoupon = () => {
        setDiscount(0)
        setAppliedCoupon('')
    }

    // Address actions
    const handleSaveNewAddress = (e) => {
        e.preventDefault()
        if (!newAddress.fullName || !newAddress.phone || !newAddress.street || !newAddress.pincode) {
            alert('Please fill all required address fields.')
            return
        }

        const newId = Date.now()
        const created = { ...newAddress, id: newId }
        const updated = [...addresses, created]
        setAddresses(updated)
        setSelectedAddressId(newId)
        setShowNewAddressForm(false)

        const storageKey = user ? `echoeats_addresses_${user.user_id}` : 'echoeats_guest_addresses'
        localStorage.setItem(storageKey, JSON.stringify(updated))
    }

    const handleDeleteAddress = (id, e) => {
        e.stopPropagation()
        const updated = addresses.filter(a => a.id !== id)
        setAddresses(updated)
        if (selectedAddressId === id && updated.length > 0) {
            setSelectedAddressId(updated[0].id)
        }
        const storageKey = user ? `echoeats_addresses_${user.user_id}` : 'echoeats_guest_addresses'
        localStorage.setItem(storageKey, JSON.stringify(updated))
    }

    const getSelectedAddress = () => {
        return addresses.find(a => a.id === selectedAddressId) || addresses[0] || {}
    }

    // Checkout initiation
    const handleStartCheckout = () => {
        if (!isLoggedIn) {
            navigate('/login', { state: { from: { pathname: '/cart' } } })
            return
        }
        setIsCheckoutOpen(true)
        setCheckoutStep(1)
    }

    // Place Order handler (COD & UPI)
    const handlePlaceOrder = async () => {
        setLoading(true)
        const chosenAddr = getSelectedAddress()

        try {
            const payload = {
                userId: user.user_id,
                amount: grandTotal,
                items: cartItems,
                paymentMethod: paymentMethod,
                address: chosenAddr,
                deliveryNotes: deliveryNotes,
                customerName: chosenAddr.fullName || user.name,
                customerPhone: chosenAddr.phone || ''
            }

            const res = await fetch(`${API_URL}/create-order/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })

            const orderData = await res.json()

            if (!orderData.success) {
                throw new Error(orderData.error || "Order creation failed")
            }

            // Handle UPI / Online via Razorpay
            if (paymentMethod === 'UPI' && orderData.razorpayOrderId) {
                // If it's a simulated order or Razorpay test
                if (orderData.razorpayOrderId.startsWith('order_sim_') || orderData.razorpayOrderId.startsWith('order_test_')) {
                    // Call verify-payment directly for test flow
                    await fetch(`${API_URL}/verify-payment/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            razorpay_payment_id: `pay_test_${Date.now()}`,
                            razorpay_order_id: orderData.razorpayOrderId,
                            razorpay_signature: 'test_signature_valid',
                            orderId: orderData.orderId
                        })
                    })

                    finishOrder(orderData.orderId, chosenAddr)
                    return
                }

                // If real Razorpay key
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
                    amount: grandTotal * 100,
                    currency: 'INR',
                    name: 'EchoEats',
                    description: 'Order Payment',
                    order_id: orderData.razorpayOrderId,
                    handler: async (paymentResp) => {
                        try {
                            const vRes = await fetch(`${API_URL}/verify-payment/`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    razorpay_payment_id: paymentResp.razorpay_payment_id,
                                    razorpay_order_id: paymentResp.razorpay_order_id,
                                    razorpay_signature: paymentResp.razorpay_signature,
                                    orderId: orderData.orderId
                                })
                            })
                            const vData = await vRes.json()
                            if (vData.success) {
                                finishOrder(orderData.orderId, chosenAddr)
                            } else {
                                alert("Payment verification check: " + (vData.error || "Please check orders"))
                                finishOrder(orderData.orderId, chosenAddr)
                            }
                        } catch (err) {
                            console.error(err)
                            finishOrder(orderData.orderId, chosenAddr)
                        }
                    },
                    prefill: {
                        name: user.name,
                        email: user.email,
                        contact: chosenAddr.phone || ''
                    },
                    theme: { color: '#ff6b35' },
                    modal: {
                        ondismiss: () => { setLoading(false) }
                    }
                }

                const rzp = new window.Razorpay(options)
                rzp.open()
                return
            }

            // Cash on Delivery
            finishOrder(orderData.orderId, chosenAddr)

        } catch (error) {
            console.error("Order error:", error)
            alert("Error placing order: " + error.message)
            setLoading(false)
        }
    }

    const finishOrder = async (orderId, address) => {
        setConfirmedOrder({
            orderId,
            items: [...cartItems],
            amount: grandTotal,
            address,
            paymentMethod,
            date: new Date().toISOString()
        })
        setLoading(false)
        setCheckoutStep(4)
        await clearCart()
    }

    // Invoice generator function
    const downloadInvoice = (order) => {
        if (!order) return
        const printWindow = window.open('', '_blank')
        const itemsHtml = order.items.map(item => `
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">${item.FoodName || item.name}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">${item.Quantity}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">₹${parseFloat(item.Price).toFixed(2)}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right; font-weight: bold;">₹${(parseFloat(item.Price) * item.Quantity).toFixed(2)}</td>
            </tr>
        `).join('')

        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>EchoEats Tax Invoice - ${order.orderId}</title>
                <style>
                    body { font-family: 'Helvetica Neue', Arial, sans-serif; color: #333; margin: 40px; }
                    .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #ff6b35; padding-bottom: 20px; }
                    .logo { font-size: 26px; font-weight: 800; color: #ff6b35; }
                    .invoice-title { font-size: 20px; font-weight: bold; color: #333; }
                    .details-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin: 25px 0; }
                    .box { background: #fafafa; border: 1px solid #eaeaea; border-radius: 8px; padding: 15px; }
                    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                    th { background: #fff5f0; color: #ff6b35; padding: 10px; text-align: left; font-size: 13px; text-transform: uppercase; }
                    .total-box { margin-left: auto; width: 300px; padding: 15px; border-top: 2px solid #ff6b35; }
                    .row { display: flex; justify-content: space-between; margin: 6px 0; }
                    .footer { text-align: center; margin-top: 50px; font-size: 12px; color: #888; border-top: 1px solid #eee; padding-top: 20px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <div>
                        <div class="logo">EchoEats 🍕</div>
                        <p style="margin: 4px 0; font-size: 12px; color: #666;">Voice & Gourmet Food Delivery</p>
                    </div>
                    <div style="text-align: right;">
                        <div class="invoice-title">TAX INVOICE</div>
                        <p style="margin: 4px 0; font-size: 13px;"><strong>Invoice No:</strong> INV-${order.orderId}</p>
                        <p style="margin: 4px 0; font-size: 13px;"><strong>Date:</strong> ${new Date(order.date).toLocaleDateString('en-IN')}</p>
                    </div>
                </div>

                <div class="details-grid">
                    <div class="box">
                        <h4 style="margin: 0 0 10px 0; color: #ff6b35;">Billed To:</h4>
                        <p style="margin: 3px 0; font-weight: bold;">${order.address?.fullName || user?.name}</p>
                        <p style="margin: 3px 0;">${order.address?.street || 'Indiranagar'}</p>
                        <p style="margin: 3px 0;">${order.address?.city || 'Bengaluru'}, ${order.address?.pincode || '560038'}</p>
                        <p style="margin: 3px 0;">Phone: ${order.address?.phone || 'N/A'}</p>
                    </div>
                    <div class="box">
                        <h4 style="margin: 0 0 10px 0; color: #ff6b35;">Order Info:</h4>
                        <p style="margin: 3px 0;"><strong>Order ID:</strong> ${order.orderId}</p>
                        <p style="margin: 3px 0;"><strong>Payment Method:</strong> ${order.paymentMethod === 'COD' ? 'Cash on Delivery' : 'Online / UPI'}</p>
                        <p style="margin: 3px 0;"><strong>Status:</strong> Confirmed & Paid</p>
                    </div>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Item Description</th>
                            <th style="text-align: center;">Qty</th>
                            <th style="text-align: right;">Unit Price</th>
                            <th style="text-align: right;">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${itemsHtml}
                    </tbody>
                </table>

                <div class="total-box">
                    <div class="row"><span>Subtotal:</span><span>₹${order.amount.toFixed(2)}</span></div>
                    <div class="row"><span>GST (5%):</span><span>Included</span></div>
                    <div class="row"><span>Delivery Fee:</span><span>FREE</span></div>
                    <hr style="border: 0; border-top: 1px solid #ddd; margin: 10px 0;">
                    <div class="row" style="font-size: 18px; font-weight: bold; color: #ff6b35;">
                        <span>Total Paid:</span>
                        <span>₹${order.amount.toFixed(2)}</span>
                    </div>
                </div>

                <div class="footer">
                    <p>Thank you for ordering with EchoEats! Enjoy your fresh and delicious meal.</p>
                    <p>Need support? Contact support@echoeats.com • GSTIN: 29ABCDE1234F1Z5</p>
                </div>
                <script>
                    window.onload = function() { window.print(); }
                </script>
            </body>
            </html>
        `)
        printWindow.document.close()
    }

    return (
        <div className="cart-page-wrap">
            <div className="cart-container-main">
                <div className="cart-header-row">
                    <div>
                        <h1 className="cart-main-title">Shopping Cart</h1>
                        <p className="cart-main-subtitle">
                            {cartItems.length > 0 
                                ? `You have ${cartItems.reduce((acc, i) => acc + i.Quantity, 0)} item(s) ready for checkout`
                                : 'Your culinary basket is currently empty'}
                        </p>
                    </div>
                    {cartItems.length > 0 && (
                        <button className="cart-clear-btn" onClick={clearCart}>
                            🗑️ Clear Cart
                        </button>
                    )}
                </div>

                {cartItems.length === 0 ? (
                    <div className="empty-cart-card">
                        <div className="empty-cart-illustration">🛒</div>
                        <h2>Your Cart is Hungry!</h2>
                        <p>Explore top dishes from our curated kitchen menu and fill your belly with delicious flavors.</p>
                        <button className="browse-menu-action-btn" onClick={() => navigate('/#items')}>
                            Explore Menu Now →
                        </button>
                    </div>
                ) : (
                    <div className="cart-split-layout">
                        {/* Left: Items List */}
                        <div className="cart-items-column">
                            {cartItems.map((item) => (
                                <div key={item.FoodID} className="modern-cart-item-card">
                                    <img 
                                        src={`/${item.ImageName}`} 
                                        alt={item.FoodName} 
                                        className="cart-item-thumb"
                                        onError={(e) => {
                                            e.target.src = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=200&auto=format&fit=crop&q=80"
                                        }}
                                    />
                                    <div className="cart-item-info">
                                        <div className="cart-item-title-row">
                                            <h3>{item.FoodName}</h3>
                                            <span className="cart-item-cat">{item.Category}</span>
                                        </div>
                                        <div className="cart-item-rate">
                                            ₹{parseFloat(item.Price).toFixed(0)} each
                                        </div>
                                    </div>

                                    {/* Stepper */}
                                    <div className="cart-item-stepper">
                                        <button 
                                            onClick={() => updateQuantity(item.FoodID, -1)}
                                            className="stepper-btn"
                                            aria-label="Decrease"
                                        >
                                            -
                                        </button>
                                        <span className="stepper-val">{item.Quantity}</span>
                                        <button 
                                            onClick={() => updateQuantity(item.FoodID, 1)}
                                            className="stepper-btn"
                                            aria-label="Increase"
                                        >
                                            +
                                        </button>
                                    </div>

                                    {/* Item Total */}
                                    <div className="cart-item-total-col">
                                        <span className="cart-item-total-price">
                                            ₹{(parseFloat(item.Price) * item.Quantity).toFixed(0)}
                                        </span>
                                    </div>

                                    {/* Remove button */}
                                    <button 
                                        className="cart-item-remove-btn" 
                                        onClick={() => updateQuantity(item.FoodID, -item.Quantity)}
                                        title="Remove item"
                                    >
                                        ✕
                                    </button>
                                </div>
                            ))}

                            {/* Delivery Assurance Strip */}
                            <div className="delivery-promise-strip">
                                <div className="promise-item">
                                    <span>⚡</span>
                                    <div>
                                        <strong>Lightning Fast Delivery</strong>
                                        <p>Hot food at your doorstep in 20-30 mins</p>
                                    </div>
                                </div>
                                <div className="promise-item">
                                    <span>🛡️</span>
                                    <div>
                                        <strong>100% Hygienic Food</strong>
                                        <p>Double packed with contact-free safety</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Right: Order Summary & Coupon Card */}
                        <div className="cart-summary-column">
                            {/* Promo Code Box */}
                            <div className="cart-promo-box">
                                <h4>Have a Coupon Code?</h4>
                                {appliedCoupon ? (
                                    <div className="applied-coupon-pill">
                                        <span>🎟️ Applied: <strong>{appliedCoupon}</strong></span>
                                        <button onClick={removeCoupon} className="coupon-remove-btn">Remove</button>
                                    </div>
                                ) : (
                                    <form onSubmit={handleApplyCoupon} className="coupon-input-group">
                                        <input 
                                            type="text" 
                                            placeholder="Try ECHO50 or FEAST20" 
                                            value={couponCode}
                                            onChange={(e) => setCouponCode(e.target.value)}
                                            className="coupon-field"
                                        />
                                        <button type="submit" className="coupon-apply-btn">Apply</button>
                                    </form>
                                )}
                                {couponError && <p className="coupon-err-msg">{couponError}</p>}
                            </div>

                            {/* Bill Breakdown Card */}
                            <div className="cart-bill-card">
                                <h3>Order Summary</h3>
                                <div className="bill-divider"></div>

                                <div className="bill-row">
                                    <span>Item Subtotal</span>
                                    <span>₹{subtotal.toFixed(2)}</span>
                                </div>

                                <div className="bill-row">
                                    <span>Delivery Fee</span>
                                    {deliveryFee === 0 ? (
                                        <span className="free-tag">FREE</span>
                                    ) : (
                                        <span>₹{deliveryFee.toFixed(2)}</span>
                                    )}
                                </div>

                                <div className="bill-row">
                                    <span>Restaurant Taxes & GST (5%)</span>
                                    <span>₹{taxes.toFixed(2)}</span>
                                </div>

                                {discount > 0 && (
                                    <div className="bill-row discount-row">
                                        <span>Coupon Discount</span>
                                        <span>- ₹{discount.toFixed(2)}</span>
                                    </div>
                                )}

                                <div className="bill-divider"></div>

                                <div className="bill-total-row">
                                    <div>
                                        <strong>To Pay</strong>
                                        <p className="savings-note">
                                            {deliveryFee === 0 ? '✨ You unlocked Free Delivery!' : 'Add items worth ₹' + (300 - subtotal) + ' for Free Delivery'}
                                        </p>
                                    </div>
                                    <strong className="grand-total-amount">₹{grandTotal.toFixed(0)}</strong>
                                </div>

                                <button 
                                    className="proceed-checkout-btn"
                                    onClick={handleStartCheckout}
                                    disabled={loading}
                                >
                                    Proceed to Checkout →
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* ========================================================= */}
            {/* SHOPVERSE-LIKE MULTI-STEP CHECKOUT MODAL                  */}
            {/* ========================================================= */}
            {isCheckoutOpen && (
                <div className="checkout-modal-overlay">
                    <div className="checkout-modal-container">
                        {/* Header */}
                        <div className="checkout-modal-header">
                            <div>
                                <h2>Complete Your Order</h2>
                                <p className="step-tracker-text">
                                    {checkoutStep === 1 && 'Step 1 of 3: Select or Add Delivery Address'}
                                    {checkoutStep === 2 && 'Step 2 of 3: Review Order Summary'}
                                    {checkoutStep === 3 && 'Step 3 of 3: Payment Options'}
                                    {checkoutStep === 4 && '🎉 Order Placed Successfully!'}
                                </p>
                            </div>
                            {checkoutStep !== 4 && (
                                <button className="checkout-close-btn" onClick={() => setIsCheckoutOpen(false)}>
                                    ✕
                                </button>
                            )}
                        </div>

                        {/* Step Progress Stepper Bar */}
                        {checkoutStep !== 4 && (
                            <div className="checkout-stepper-bar">
                                <div className={`step-dot-item ${checkoutStep >= 1 ? 'active' : ''}`}>
                                    <span className="dot-number">1</span>
                                    <span className="dot-label">Address</span>
                                </div>
                                <div className={`step-connector ${checkoutStep >= 2 ? 'active' : ''}`}></div>
                                <div className={`step-dot-item ${checkoutStep >= 2 ? 'active' : ''}`}>
                                    <span className="dot-number">2</span>
                                    <span className="dot-label">Summary</span>
                                </div>
                                <div className={`step-connector ${checkoutStep >= 3 ? 'active' : ''}`}></div>
                                <div className={`step-dot-item ${checkoutStep >= 3 ? 'active' : ''}`}>
                                    <span className="dot-number">3</span>
                                    <span className="dot-label">Payment</span>
                                </div>
                            </div>
                        )}

                        {/* Modal Body */}
                        <div className="checkout-modal-body">
                            {/* STEP 1: ADDRESS MANAGEMENT */}
                            {checkoutStep === 1 && (
                                <div className="checkout-step-view">
                                    <div className="address-section-header">
                                        <h3>Where should we deliver?</h3>
                                        <button 
                                            className="add-address-toggle-btn"
                                            onClick={() => setShowNewAddressForm(!showNewAddressForm)}
                                        >
                                            {showNewAddressForm ? 'Cancel' : '+ Add New Address'}
                                        </button>
                                    </div>

                                    {/* New Address Form */}
                                    {showNewAddressForm ? (
                                        <form onSubmit={handleSaveNewAddress} className="new-address-form">
                                            <h4>Add Delivery Address</h4>
                                            <div className="form-grid-2">
                                                <input 
                                                    type="text" 
                                                    placeholder="Full Name *" 
                                                    value={newAddress.fullName}
                                                    onChange={e => setNewAddress({ ...newAddress, fullName: e.target.value })}
                                                    required
                                                />
                                                <input 
                                                    type="tel" 
                                                    placeholder="10-Digit Mobile Phone *" 
                                                    value={newAddress.phone}
                                                    onChange={e => setNewAddress({ ...newAddress, phone: e.target.value })}
                                                    required
                                                />
                                            </div>
                                            <input 
                                                type="text" 
                                                placeholder="Street Address, Flat / House No, Floor *" 
                                                value={newAddress.street}
                                                onChange={e => setNewAddress({ ...newAddress, street: e.target.value })}
                                                required
                                            />
                                            <div className="form-grid-3">
                                                <input 
                                                    type="text" 
                                                    placeholder="Landmark" 
                                                    value={newAddress.landmark}
                                                    onChange={e => setNewAddress({ ...newAddress, landmark: e.target.value })}
                                                />
                                                <input 
                                                    type="text" 
                                                    placeholder="City *" 
                                                    value={newAddress.city}
                                                    onChange={e => setNewAddress({ ...newAddress, city: e.target.value })}
                                                    required
                                                />
                                                <input 
                                                    type="text" 
                                                    placeholder="PIN Code *" 
                                                    value={newAddress.pincode}
                                                    onChange={e => setNewAddress({ ...newAddress, pincode: e.target.value })}
                                                    required
                                                />
                                            </div>

                                            <div className="address-type-selector">
                                                <span className="type-label">Address Tag:</span>
                                                {['Home', 'Work', 'Other'].map(type => (
                                                    <button 
                                                        type="button" 
                                                        key={type}
                                                        className={`type-chip ${newAddress.type === type ? 'selected' : ''}`}
                                                        onClick={() => setNewAddress({ ...newAddress, type })}
                                                    >
                                                        {type === 'Home' ? '🏠' : type === 'Work' ? '🏢' : '📍'} {type}
                                                    </button>
                                                ))}
                                            </div>

                                            <button type="submit" className="save-address-submit-btn">
                                                Save and Select Address
                                            </button>
                                        </form>
                                    ) : (
                                        <div className="saved-addresses-grid">
                                            {addresses.map((addr) => (
                                                <div 
                                                    key={addr.id}
                                                    className={`address-card ${selectedAddressId === addr.id ? 'selected' : ''}`}
                                                    onClick={() => setSelectedAddressId(addr.id)}
                                                >
                                                    <div className="addr-card-top">
                                                        <span className="addr-tag">
                                                            {addr.type === 'Home' ? '🏠' : addr.type === 'Work' ? '🏢' : '📍'} {addr.type}
                                                        </span>
                                                        {addresses.length > 1 && (
                                                            <button 
                                                                className="addr-delete-btn"
                                                                onClick={(e) => handleDeleteAddress(addr.id, e)}
                                                                title="Delete address"
                                                            >
                                                                ✕
                                                            </button>
                                                        )}
                                                    </div>
                                                    <div className="addr-name">{addr.fullName}</div>
                                                    <div className="addr-street">{addr.street}</div>
                                                    {addr.landmark && <div className="addr-landmark">Near {addr.landmark}</div>}
                                                    <div className="addr-city">{addr.city}, {addr.state} - {addr.pincode}</div>
                                                    <div className="addr-phone">📞 {addr.phone}</div>
                                                    
                                                    <div className="addr-radio-indicator">
                                                        {selectedAddressId === addr.id ? '✓ Selected' : 'Select'}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {/* Delivery Instructions */}
                                    <div className="delivery-instructions-box">
                                        <label>Special Delivery Instructions (Optional):</label>
                                        <input 
                                            type="text" 
                                            placeholder="e.g. Ring doorbell, leave at security desk, call upon arrival"
                                            value={deliveryNotes}
                                            onChange={e => setDeliveryNotes(e.target.value)}
                                            className="instructions-input"
                                        />
                                    </div>

                                    <div className="checkout-step-footer">
                                        <button className="secondary-btn" onClick={() => setIsCheckoutOpen(false)}>
                                            Back to Cart
                                        </button>
                                        <button 
                                            className="primary-btn" 
                                            disabled={!selectedAddressId}
                                            onClick={() => setCheckoutStep(2)}
                                        >
                                            Continue to Order Summary →
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* STEP 2: ORDER SUMMARY */}
                            {checkoutStep === 2 && (
                                <div className="checkout-step-view">
                                    <div className="summary-step-grid">
                                        {/* Left: Review Items */}
                                        <div className="summary-items-list">
                                            <h4>Review Items ({cartItems.length})</h4>
                                            {cartItems.map(item => (
                                                <div key={item.FoodID} className="summary-item-row">
                                                    <img src={`/${item.ImageName}`} alt={item.FoodName} className="summary-thumb" />
                                                    <div className="summary-item-meta">
                                                        <strong>{item.FoodName}</strong>
                                                        <span>₹{parseFloat(item.Price).toFixed(0)} × {item.Quantity}</span>
                                                    </div>
                                                    <div className="summary-item-price">
                                                        ₹{(parseFloat(item.Price) * item.Quantity).toFixed(0)}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>

                                        {/* Right: Chosen Address & Bill Preview */}
                                        <div className="summary-details-box">
                                            <h4>Deliver To:</h4>
                                            <div className="chosen-address-preview">
                                                <strong>{getSelectedAddress().fullName} ({getSelectedAddress().type})</strong>
                                                <p>{getSelectedAddress().street}, {getSelectedAddress().city} - {getSelectedAddress().pincode}</p>
                                                <p>Phone: {getSelectedAddress().phone}</p>
                                                {deliveryNotes && <p className="notes-preview">Note: "{deliveryNotes}"</p>}
                                                <button className="change-addr-link" onClick={() => setCheckoutStep(1)}>
                                                    Change Address
                                                </button>
                                            </div>

                                            <div className="summary-bill-preview">
                                                <div className="bill-row"><span>Total Items:</span><span>{cartItems.reduce((a, b) => a + b.Quantity, 0)}</span></div>
                                                <div className="bill-row"><span>Subtotal:</span><span>₹{subtotal.toFixed(2)}</span></div>
                                                <div className="bill-row"><span>Delivery:</span><span>{deliveryFee === 0 ? 'FREE' : `₹${deliveryFee}`}</span></div>
                                                <div className="bill-row"><span>Taxes:</span><span>₹{taxes.toFixed(2)}</span></div>
                                                {discount > 0 && <div className="bill-row discount-row"><span>Discount:</span><span>-₹{discount.toFixed(2)}</span></div>}
                                                <div className="bill-divider"></div>
                                                <div className="bill-row grand-total-row">
                                                    <span>Grand Total:</span>
                                                    <span>₹{grandTotal.toFixed(0)}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="checkout-step-footer">
                                        <button className="secondary-btn" onClick={() => setCheckoutStep(1)}>
                                            ← Back to Address
                                        </button>
                                        <button className="primary-btn" onClick={() => setCheckoutStep(3)}>
                                            Proceed to Payment →
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* STEP 3: PAYMENT OPTIONS */}
                            {checkoutStep === 3 && (
                                <div className="checkout-step-view">
                                    <div className="payment-options-container">
                                        <h3>Select Preferred Payment Method</h3>
                                        <p className="pay-subtitle">Amount to Pay: <strong>₹{grandTotal.toFixed(0)}</strong></p>

                                        <div className="payment-options-grid">
                                            {/* COD Option */}
                                            <div 
                                                className={`payment-option-card ${paymentMethod === 'COD' ? 'selected' : ''}`}
                                                onClick={() => setPaymentMethod('COD')}
                                            >
                                                <div className="pay-option-icon">💵</div>
                                                <div className="pay-option-content">
                                                    <strong>Cash on Delivery (COD)</strong>
                                                    <p>Pay with cash or UPI at your doorstep upon delivery.</p>
                                                </div>
                                                <div className="pay-radio">{paymentMethod === 'COD' ? '●' : '○'}</div>
                                            </div>

                                            {/* Razorpay Online Option */}
                                            <div 
                                                className={`payment-option-card ${paymentMethod === 'UPI' ? 'selected' : ''}`}
                                                onClick={() => setPaymentMethod('UPI')}
                                            >
                                                <div className="pay-option-icon">📱</div>
                                                <div className="pay-option-content">
                                                    <strong>UPI / Credit & Debit Cards / NetBanking</strong>
                                                    <p>Instant online checkout powered securely by Razorpay.</p>
                                                </div>
                                                <div className="pay-radio">{paymentMethod === 'UPI' ? '●' : '○'}</div>
                                            </div>
                                        </div>

                                        <div className="secure-badge">
                                            <span>🔒 256-Bit Bank Grade SSL Encrypted Checkout</span>
                                        </div>
                                    </div>

                                    <div className="checkout-step-footer">
                                        <button className="secondary-btn" onClick={() => setCheckoutStep(2)}>
                                            ← Back to Summary
                                        </button>
                                        <button 
                                            className="primary-btn place-order-btn" 
                                            onClick={handlePlaceOrder}
                                            disabled={loading}
                                        >
                                            {loading ? 'Processing Order...' : `Pay ₹${grandTotal.toFixed(0)} & Place Order`}
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* STEP 4: ORDER SUCCESS */}
                            {checkoutStep === 4 && confirmedOrder && (
                                <div className="checkout-success-view">
                                    <div className="success-icon-animation">🎉</div>
                                    <h2>Order Placed Successfully!</h2>
                                    <p className="success-ord-id">Order ID: <strong>#{confirmedOrder.orderId}</strong></p>
                                    <p className="success-eta">
                                        ⚡ Delicious food is being prepared and will arrive in <strong>20-30 minutes</strong>!
                                    </p>

                                    <div className="success-summary-box">
                                        <div className="success-row">
                                            <span>Delivering to:</span>
                                            <strong>{confirmedOrder.address?.fullName}, {confirmedOrder.address?.street}</strong>
                                        </div>
                                        <div className="success-row">
                                            <span>Payment Method:</span>
                                            <strong>{confirmedOrder.paymentMethod === 'COD' ? 'Cash on Delivery' : 'Online / UPI'}</strong>
                                        </div>
                                        <div className="success-row">
                                            <span>Amount Paid / Due:</span>
                                            <strong>₹{confirmedOrder.amount.toFixed(0)}</strong>
                                        </div>
                                    </div>

                                    <div className="success-actions-row">
                                        <button 
                                            className="invoice-download-btn"
                                            onClick={() => downloadInvoice(confirmedOrder)}
                                        >
                                            📄 Download Tax Invoice (PDF)
                                        </button>
                                        <button 
                                            className="view-orders-action-btn"
                                            onClick={() => {
                                                setIsCheckoutOpen(false)
                                                navigate('/orders')
                                            }}
                                        >
                                            📦 Track in My Orders
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default CartPage