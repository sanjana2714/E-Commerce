import React, { useState, useEffect } from 'react';
import { Cart } from '../types';
import { api } from '../services/api';

interface CartPageProps {
  onOrderCreated: () => void;
}

export const CartPage: React.FC<CartPageProps> = ({ onOrderCreated }) => {
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(false);
  const [checkoutStatus, setCheckoutStatus] = useState<string | null>(null);

  useEffect(() => {
    loadCart();
  }, []);

  const loadCart = async () => {
    try {
      const res = await api.getCart();
      setCart(res);
    } catch (e) {
      console.error(e);
    }
  };

  const handleCheckout = async () => {
    if (!cart || !cart.items || cart.items.length === 0) return;
    setLoading(true);
    setCheckoutStatus(null);

    // Generate unique Idempotency Key
    const idempotencyKey = `IDEM-UI-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

    try {
      const items = cart.items.map(item => ({ product_id: item.product_id, quantity: item.quantity }));
      const order = await api.createOrder(items, idempotencyKey);
      
      // Process payment automatically
      await api.processPayment(order.id, false);

      setCheckoutStatus(`Order #${order.id} placed successfully with Idempotency Key ${idempotencyKey}!`);
      loadCart();
      onOrderCreated();
    } catch (e: any) {
      setCheckoutStatus(`Checkout Error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (!cart) return <div className="container">Loading cart...</div>;

  return (
    <div className="container" style={{ maxWidth: '800px' }}>
      <div className="glass-panel">
        <h2 style={{ marginBottom: '1.5rem' }}>🛒 Shopping Cart</h2>

        {checkoutStatus && (
          <div style={{ padding: '1rem', marginBottom: '1.5rem', borderRadius: '8px', background: checkoutStatus.includes('Error') ? 'rgba(244,63,94,0.2)' : 'rgba(16,185,129,0.2)', color: checkoutStatus.includes('Error') ? '#f87171' : '#34d399' }}>
            {checkoutStatus}
          </div>
        )}

        {cart.items.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)' }}>Your cart is empty.</p>
        ) : (
          <div>
            {cart.items.map((item) => (
              <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 0', borderBottom: '1px solid var(--border-color)' }}>
                <div>
                  <h4 style={{ fontSize: '1rem' }}>{item.product?.name || `Product #${item.product_id}`}</h4>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>${item.unit_price.toFixed(2)} x {item.quantity}</p>
                </div>
                <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>
                  ${(item.unit_price * item.quantity).toFixed(2)}
                </div>
              </div>
            ))}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '2rem', paddingTop: '1rem', borderTop: '2px solid var(--border-color)' }}>
              <h3>Total Amount: <span style={{ color: 'var(--accent-emerald)' }}>${cart.total_amount.toFixed(2)}</span></h3>
              <button className="btn-success" onClick={handleCheckout} disabled={loading}>
                {loading ? 'Executing Idempotent Order...' : '⚡ Place Idempotent Order'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
