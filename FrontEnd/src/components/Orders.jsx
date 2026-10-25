import React, { useEffect, useState, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import './CSS/Orders.css'
import { GlobalStateContext } from '../context/GlobalStateContext'

const OrdersPage = () => {
    const { isLoggedIn, user, updateQuantity } = useContext(GlobalStateContext)
    const [orders, setOrders] = useState([])
    const [loading, setLoading] = useState(true)
    const [reviewModalOrder, setReviewModalOrder] = useState(null)
    const [ratingVal, setRatingVal] = useState(5)
    const [reviewText, setReviewText] = useState('')
    const [reviewSubmitted, setReviewSubmitted] = useState(false)
    const navigate = useNavigate()
    const API_URL = (import.meta.env.VITE_API_URL || (import.meta.env.PROD ? 'https://echoeats-voice-assistant-1.onrender.com' : 'http://localhost:8000')).replace(/\/+$/, '')

    useEffect(() => {
        const storedLogin = localStorage.getItem('isLoggedIn') === 'true'
        if (!isLoggedIn && !storedLogin) {
            navigate('/login', { state: { from: { pathname: '/orders' } } })
            return
        }

        fetchOrders()
        const intervalId = setInterval(fetchOrders, 8000)
        return () => clearInterval(intervalId)
    }, [isLoggedIn, user])

    const fetchOrders = async () => {
        let storedUser = null
        try {
            storedUser = JSON.parse(localStorage.getItem('user') || 'null')
        } catch (e) {
            storedUser = null
        }

        const targetUserId = (
            user?.user_id ||
            user?.id ||
            user?.userId ||
            user?.email ||
            storedUser?.user_id ||
            storedUser?.id ||
            storedUser?.userId ||
            storedUser?.email ||
            ''
        )

        try {
            const primaryUrl = targetUserId 
                ? `${API_URL}/orders/${encodeURIComponent(targetUserId)}/`
                : `${API_URL}/orders/`

            let response = await fetch(primaryUrl)
            
            // If primary URL fails (e.g. 404), try query param and route variants
            if (!response.ok && targetUserId) {
                response = await fetch(`${API_URL}/orders/?userId=${encodeURIComponent(targetUserId)}`)
            }
            if (!response.ok) {
                response = await fetch(`${API_URL}/orders/`)
            }
            if (!response.ok) {
                response = await fetch(`${API_URL}/orders`)
            }

            if (response.ok) {
                const data = await response.json()
                if (Array.isArray(data)) {
                    setOrders(data)
                } else {
                    setOrders([])
                }
            } else {
                setOrders([])
            }
            setLoading(false)
        } catch (error) {
            console.error("Error fetching orders:", error)
            setOrders([])
            setLoading(false)
        }
    }


    const handleReorder = async (order) => {
        if (!order.items || !order.items.length) return
        for (const item of order.items) {
            const fid = item.food_id || item.FoodID
            const qty = item.quantity || item.Quantity || 1
            if (fid) {
                await updateQuantity(fid, qty)
            }
        }
        navigate('/cart')
    }

    // Download / Print Tax Invoice
    const handleDownloadInvoice = (order) => {
        const printWindow = window.open('', '_blank')
        const items = order.items || []
        const addr = order.customer_details?.address || {}

        const itemsRows = items.map(item => `
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">
                    <strong>${item.name || item.FoodName}</strong>
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">${item.quantity || 1}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">₹${parseFloat(item.price || 0).toFixed(2)}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right; font-weight: bold;">₹${(parseFloat(item.price || 0) * (item.quantity || 1)).toFixed(2)}</td>
            </tr>
        `).join('')

        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>EchoEats Tax Invoice - ${order.order_id}</title>
                <style>
                    body { font-family: 'Helvetica Neue', Arial, sans-serif; color: #2d1a0e; margin: 40px; background: #fff; }
                    .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #ff6b35; padding-bottom: 20px; }
                    .logo { font-size: 28px; font-weight: 800; color: #ff6b35; }
                    .invoice-title { font-size: 22px; font-weight: bold; color: #1a1a1a; }
                    .details-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin: 25px 0; }
                    .box { background: #fff8f5; border: 1px solid #ffe3d5; border-radius: 12px; padding: 18px; }
                    table { width: 100%; border-collapse: collapse; margin: 25px 0; }
                    th { background: #ffeae0; color: #d9480f; padding: 12px 10px; text-align: left; font-size: 13px; text-transform: uppercase; }
                    .total-box { margin-left: auto; width: 320px; padding: 18px; border-top: 2px solid #ff6b35; }
                    .row { display: flex; justify-content: space-between; margin: 6px 0; font-size: 14px; }
                    .grand-total { font-size: 18px; font-weight: bold; color: #ff6b35; border-top: 1px solid #ddd; padding-top: 10px; margin-top: 8px; }
                    .footer { text-align: center; margin-top: 50px; font-size: 12px; color: #888; border-top: 1px solid #eee; padding-top: 20px; }
                    .paid-stamp { display: inline-block; padding: 4px 10px; background: #e6fcf5; color: #0ca678; border: 1px solid #0ca678; border-radius: 6px; font-weight: bold; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <div>
                        <div class="logo">EchoEats 🍕</div>
                        <p style="margin: 4px 0; font-size: 13px; color: #666;">Gourmet & Voice Food Delivery</p>
                    </div>
                    <div style="text-align: right;">
                        <div class="invoice-title">ORIGINAL TAX INVOICE</div>
                        <p style="margin: 4px 0; font-size: 13px;"><strong>Invoice No:</strong> INV-${order.order_id}</p>
                        <p style="margin: 4px 0; font-size: 13px;"><strong>Date:</strong> ${new Date(order.order_date).toLocaleDateString('en-IN')}</p>
                        <span class="paid-stamp">PAYMENT: ${order.payment_method === 'COD' ? 'CASH ON DELIVERY' : 'PAID ONLINE (VERIFIED)'}</span>
                    </div>
                </div>

                <div class="details-grid">
                    <div class="box">
                        <h4 style="margin: 0 0 10px 0; color: #d9480f;">Customer & Delivery Details:</h4>
                        <p style="margin: 4px 0; font-weight: bold;">${addr.fullName || user?.name}</p>
                        <p style="margin: 4px 0;">${addr.street || 'Indiranagar Delivery Address'}</p>
                        ${addr.landmark ? `<p style="margin: 4px 0;">Landmark: ${addr.landmark}</p>` : ''}
                        <p style="margin: 4px 0;">${addr.city || 'Bengaluru'}, ${addr.state || 'Karnataka'} - ${addr.pincode || '560038'}</p>
                        <p style="margin: 4px 0;">Phone: ${addr.phone || 'N/A'}</p>
                    </div>
                    <div class="box">
                        <h4 style="margin: 0 0 10px 0; color: #d9480f;">Order Summary:</h4>
                        <p style="margin: 4px 0;"><strong>Order ID:</strong> ${order.order_id}</p>
                        <p style="margin: 4px 0;"><strong>Current Status:</strong> ${order.order_status?.toUpperCase()}</p>
                        <p style="margin: 4px 0;"><strong>Method:</strong> ${order.payment_method}</p>
                        ${order.payment_id ? `<p style="margin: 4px 0;"><strong>Txn Ref:</strong> ${order.payment_id}</p>` : ''}
                    </div>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Food Item</th>
                            <th style="text-align: center;">Qty</th>
                            <th style="text-align: right;">Unit Price</th>
                            <th style="text-align: right;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${itemsRows}
                    </tbody>
                </table>

                <div class="total-box">
                    <div class="row"><span>Items Total:</span><span>₹${parseFloat(order.total_amount).toFixed(2)}</span></div>
                    <div class="row"><span>GST & Restaurant Tax:</span><span>Included (5%)</span></div>
                    <div class="row"><span>Delivery Partner Fee:</span><span>FREE</span></div>
                    <div class="row grand-total">
                        <span>Grand Total:</span>
                        <span>₹${parseFloat(order.total_amount).toFixed(2)}</span>
                    </div>
                </div>

                <div class="footer">
                    <p>Thank you for choosing EchoEats! This is a computer-generated tax invoice.</p>
                    <p>FSSAI Lic. No: 11223344556677 • Support: support@echoeats.com</p>
                </div>
                <script>
                    window.onload = function() { window.print(); }
                </script>
            </body>
            </html>
        `)
        printWindow.document.close()
    }

    const getStatusIndex = (status) => {
        const statuses = ['placed', 'confirmed', 'preparing', 'out-for-delivery', 'delivered']
        const idx = statuses.indexOf(status)
        return idx !== -1 ? idx : 0
    }

    const handleOpenReview = (order) => {
        setReviewModalOrder(order)
        setRatingVal(5)
        setReviewText('')
        setReviewSubmitted(false)
    }

    const handleSaveReview = () => {
        setReviewSubmitted(true)
        setTimeout(() => {
            setReviewModalOrder(null)
            setReviewSubmitted(false)
        }, 1800)
    }

    if (!isLoggedIn) {
        return null
    }

    return (
        <div className="orders-container-main">
            <div className="orders-header">
                <div>
                    <h1 className="orders-title">My Orders & Live Tracking</h1>
                    <p className="orders-subtitle">View past orders, track live food preparation, and download tax invoices.</p>
                </div>
                <button className="new-order-btn" onClick={() => navigate('/#items')}>
                    + Order More Food
                </button>
            </div>
            
            {loading ? (
                <div className="orders-loading-card">
                    <div className="loading-spinner"></div>
                    <p>Fetching your orders from the kitchen...</p>
                </div>
            ) : !Array.isArray(orders) || orders.length === 0 ? (
                <div className="no-orders-card">
                    <div className="no-orders-illustration">📦</div>
                    <h2>No Orders Found</h2>
                    <p>Looks like you haven't placed an order yet. Treat yourself to something delicious right now!</p>
                    <button className="browse-menu-btn" onClick={() => navigate('/#items')}>
                        Browse Menu →
                    </button>
                </div>
            ) : (
                <div className="orders-grid-list">
                    {orders.map((order) => {
                        const statusIdx = getStatusIndex(order.order_status)
                        const addr = order.customer_details?.address || {}

                        return (
                            <div key={order.order_id} className="order-main-card">
                                {/* Top Header */}
                                <div className="order-card-header">
                                    <div className="ord-id-time">
                                        <div className="ord-badge-row">
                                            <span className="order-id-badge">#{order.order_id}</span>
                                            <span className={`order-status-pill ${order.order_status}`}>
                                                {order.order_status === 'placed' && '📝 Placed'}
                                                {order.order_status === 'confirmed' && '✅ Confirmed'}
                                                {order.order_status === 'preparing' && '👨‍🍳 Preparing'}
                                                {order.order_status === 'out-for-delivery' && '🛵 Out for Delivery'}
                                                {order.order_status === 'delivered' && '🍽️ Delivered'}
                                            </span>
                                        </div>
                                        <div className="order-timestamp">
                                            Placed on {new Date(order.order_date).toLocaleDateString('en-IN', {
                                                day: 'numeric',
                                                month: 'short',
                                                year: 'numeric',
                                                hour: '2-digit',
                                                minute: '2-digit'
                                            })}
                                        </div>
                                    </div>

                                    {/* Action buttons */}
                                    <div className="order-top-actions">
                                        <button 
                                            className="invoice-btn" 
                                            onClick={() => handleDownloadInvoice(order)}
                                            title="Download Tax Invoice PDF"
                                        >
                                            📄 Download Invoice
                                        </button>
                                    </div>
                                </div>

                                {/* Order Stepper Progress Bar */}
                                <div className="order-live-tracker">
                                    <div className="tracker-steps">
                                        {[
                                            { label: 'Order Placed', icon: '📝' },
                                            { label: 'Confirmed', icon: '✅' },
                                            { label: 'Preparing', icon: '👨‍🍳' },
                                            { label: 'Out for Delivery', icon: '🛵' },
                                            { label: 'Delivered', icon: '🍽️' },
                                        ].map((step, idx) => (
                                            <div 
                                                key={step.label}
                                                className={`tracker-step-node ${statusIdx >= idx ? 'completed' : ''} ${statusIdx === idx ? 'current' : ''}`}
                                            >
                                                <div className="step-icon-circle">{step.icon}</div>
                                                <span className="step-text-label">{step.label}</span>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="tracker-progress-track">
                                        <div 
                                            className="tracker-progress-fill" 
                                            style={{ width: `${(statusIdx / 4) * 100}%` }}
                                        ></div>
                                    </div>
                                </div>

                                {/* Middle: Items List */}
                                <div className="order-card-body">
                                    <div className="order-items-column">
                                        <h4>Ordered Items ({order.items?.length || 0})</h4>
                                        <div className="order-items-scroll">
                                            {order.items && order.items.map((item, index) => (
                                                <div key={index} className="order-dish-row">
                                                    <div className="dish-name-qty">
                                                        <span className="dish-name">{item.name || item.FoodName}</span>
                                                        <span className="dish-qty">× {item.quantity || 1}</span>
                                                    </div>
                                                    <span className="dish-price">
                                                        ₹{(parseFloat(item.price || 0) * (item.quantity || 1)).toFixed(0)}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Right: Delivery Address info */}
                                    <div className="order-address-box">
                                        <h4>Delivered To</h4>
                                        <div className="addr-content">
                                            <strong>{addr.fullName || user.name}</strong>
                                            <p>{addr.street || 'Local delivery location'}</p>
                                            {addr.landmark && <p>Landmark: {addr.landmark}</p>}
                                            <p>{addr.city || 'Bengaluru'} {addr.pincode ? `- ${addr.pincode}` : ''}</p>
                                            <p className="phone-line">📞 {addr.phone || 'Contact provided at checkout'}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Footer Bar */}
                                <div className="order-card-footer">
                                    <div className="order-payment-info">
                                        <div className="total-label">Total Amount Paid</div>
                                        <div className="total-val">₹{parseFloat(order.total_amount).toFixed(0)}</div>
                                        <span className="pay-method-tag">
                                            {order.payment_method === 'COD' ? '💵 Cash on Delivery' : '📱 Paid Online / UPI'}
                                        </span>
                                    </div>

                                    <div className="order-footer-actions">
                                        <button 
                                            className="reorder-action-btn"
                                            onClick={() => handleReorder(order)}
                                        >
                                            🔁 Order Again
                                        </button>
                                        {order.order_status === 'delivered' && (
                                            <button 
                                                className="review-action-btn"
                                                onClick={() => handleOpenReview(order)}
                                            >
                                                ⭐ Rate & Review
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )
                    })}
                </div>
            )}

            {/* Rate & Review Modal */}
            {reviewModalOrder && (
                <div className="review-modal-overlay" onClick={() => setReviewModalOrder(null)}>
                    <div className="review-modal-box" onClick={(e) => e.stopPropagation()}>
                        <button className="review-close-btn" onClick={() => setReviewModalOrder(null)}>✕</button>
                        
                        {reviewSubmitted ? (
                            <div className="review-success">
                                <span>🎉</span>
                                <h3>Thank you for your feedback!</h3>
                                <p>Your review helps us keep serving you the best food in town.</p>
                            </div>
                        ) : (
                            <>
                                <h3>Rate Your Experience</h3>
                                <p className="review-ord-note">Order #{reviewModalOrder.order_id}</p>

                                <div className="star-rating-row">
                                    {[1, 2, 3, 4, 5].map((star) => (
                                        <button 
                                            key={star} 
                                            type="button"
                                            className={`star-btn ${ratingVal >= star ? 'active' : ''}`}
                                            onClick={() => setRatingVal(star)}
                                        >
                                            ★
                                        </button>
                                    ))}
                                </div>

                                <textarea 
                                    placeholder="Write a quick comment about the taste, temperature, or delivery..."
                                    value={reviewText}
                                    onChange={(e) => setReviewText(e.target.value)}
                                    className="review-textarea"
                                    rows="4"
                                />

                                <button className="submit-review-btn" onClick={handleSaveReview}>
                                    Submit Review
                                </button>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}

export default OrdersPage