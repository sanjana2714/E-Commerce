import React, { useState, useEffect } from 'react';
import { Order } from '../types';
import { api } from '../services/api';

export const OrdersPage: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      const res = await api.getOrders();
      setOrders(res || []);
    } catch (e) {
      console.error(e);
    }
  };

  const getBadgeClass = (status: string) => {
    switch (status) {
      case 'CONFIRMED':
      case 'DELIVERED':
        return 'badge-active';
      case 'PENDING':
      case 'PROCESSING':
      case 'SHIPPED':
        return 'badge-pending';
      default:
        return 'badge-failed';
    }
  };

  return (
    <div className="container" style={{ maxWidth: '900px' }}>
      <div className="glass-panel">
        <h2 style={{ marginBottom: '1.5rem' }}>📦 Order History & State Machine</h2>
        {orders.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)' }}>No orders placed yet.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {orders.map((order) => (
              <div key={order.id} className="glass-panel" style={{ background: 'rgba(15, 23, 42, 0.6)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.1rem' }}>Order #{order.id}</h3>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      Idempotency Key: <code>{order.idempotency_key}</code>
                    </p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span className={`badge ${getBadgeClass(order.status)}`}>{order.status}</span>
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-emerald)', marginTop: '0.25rem' }}>
                      ${order.total_amount.toFixed(2)}
                    </div>
                  </div>
                </div>

                <div>
                  <h4 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Order Items:</h4>
                  {order.items.map((item) => (
                    <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', margin: '0.25rem 0' }}>
                      <span>Product #{item.product_id} x {item.quantity}</span>
                      <span>${item.subtotal.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
