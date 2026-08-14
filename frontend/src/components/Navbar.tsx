import React from 'react';
import { User, Cart } from '../types';

interface NavbarProps {
  user: User | null;
  cart: Cart | null;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ user, cart, activeTab, setActiveTab, onLogout }) => {
  const totalCartCount = cart?.items?.reduce((acc, item) => acc + item.quantity, 0) || 0;

  return (
    <nav className="glass-panel" style={{ borderRadius: 0, marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
        <h2 style={{ background: 'linear-gradient(135deg, #6366f1, #10b981)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', cursor: 'pointer' }} onClick={() => setActiveTab('products')}>
          ⚡ StoreScale Engine
        </h2>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className={`btn-primary ${activeTab === 'products' ? '' : 'glass-panel'}`} style={{ background: activeTab === 'products' ? undefined : 'transparent' }} onClick={() => setActiveTab('products')}>
            Products & Search
          </button>
          {user && (
            <>
              <button className={`btn-primary ${activeTab === 'cart' ? '' : 'glass-panel'}`} style={{ background: activeTab === 'cart' ? undefined : 'transparent' }} onClick={() => setActiveTab('cart')}>
                Cart ({totalCartCount})
              </button>
              <button className={`btn-primary ${activeTab === 'orders' ? '' : 'glass-panel'}`} style={{ background: activeTab === 'orders' ? undefined : 'transparent' }} onClick={() => setActiveTab('orders')}>
                My Orders
              </button>
            </>
          )}
          {user && (user.role === 'ADMIN' || user.role === 'INVENTORY_MANAGER') && (
            <button className={`btn-primary ${activeTab === 'admin' ? '' : 'glass-panel'}`} style={{ background: activeTab === 'admin' ? undefined : 'transparent' }} onClick={() => setActiveTab('admin')}>
              Admin & Metrics
            </button>
          )}
        </div>
      </div>

      <div>
        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span style={{ color: 'var(--text-secondary)' }}>
              {user.full_name} <span className="badge badge-active">{user.role}</span>
            </span>
            <button className="btn-danger" onClick={onLogout}>Logout</button>
          </div>
        ) : (
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className="btn-primary" onClick={() => setActiveTab('login')}>Login</button>
            <button className="btn-success" onClick={() => setActiveTab('register')}>Register</button>
          </div>
        )}
      </div>
    </nav>
  );
};
