import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { ProductsPage } from './pages/ProductsPage';
import { CartPage } from './pages/CartPage';
import { OrdersPage } from './pages/OrdersPage';
import { AdminPage } from './pages/AdminPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { User, Cart } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [cart, setCart] = useState<Cart | null>(null);
  const [activeTab, setActiveTab] = useState('products');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      loadProfileAndCart();
    }
  }, []);

  const loadProfileAndCart = async () => {
    try {
      const u = await api.getMe();
      setUser(u);
      const c = await api.getCart();
      setCart(c);
    } catch (e) {
      localStorage.removeItem('access_token');
      setUser(null);
    }
  };

  const handleAddToCart = async (productId: number) => {
    if (!user) {
      setActiveTab('login');
      return;
    }
    try {
      await api.addToCart(productId, 1);
      const updatedCart = await api.getCart();
      setCart(updatedCart);
    } catch (e) {
      console.error(e);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    setCart(null);
    setActiveTab('products');
  };

  return (
    <div>
      <Navbar
        user={user}
        cart={cart}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onLogout={handleLogout}
      />

      <main>
        {activeTab === 'products' && <ProductsPage onAddToCart={handleAddToCart} />}
        {activeTab === 'cart' && <CartPage onOrderCreated={() => setActiveTab('orders')} />}
        {activeTab === 'orders' && <OrdersPage />}
        {activeTab === 'admin' && <AdminPage />}
        {activeTab === 'login' && <LoginPage onLoginSuccess={() => { loadProfileAndCart(); setActiveTab('products'); }} onNavigateRegister={() => setActiveTab('register')} />}
        {activeTab === 'register' && <RegisterPage onRegisterSuccess={() => setActiveTab('login')} onNavigateLogin={() => setActiveTab('login')} />}
      </main>
    </div>
  );
};
