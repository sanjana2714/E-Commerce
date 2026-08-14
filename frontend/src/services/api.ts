import { Product, Cart, Order, User, Category, DeadLetterEvent } from '../types';

const API_BASE = '/api/v1';

const getHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
};

export const api = {
  // Auth
  register: async (data: any) => {
    const res = await fetch(`${API_BASE}/auth/register`, { method: 'POST', headers: getHeaders(), body: JSON.stringify(data) });
    if (!res.ok) throw new Error((await res.json())?.error?.message || 'Registration failed');
    return res.json();
  },

  login: async (data: any) => {
    const res = await fetch(`${API_BASE}/auth/login`, { method: 'POST', headers: getHeaders(), body: JSON.stringify(data) });
    if (!res.ok) throw new Error((await res.json())?.error?.message || 'Login failed');
    return res.json();
  },

  getMe: async (): Promise<User> => {
    const res = await fetch(`${API_BASE}/auth/me`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch profile');
    return res.json();
  },

  // Products & Search
  getCategories: async (): Promise<Category[]> => {
    const res = await fetch(`${API_BASE}/products/categories`, { headers: getHeaders() });
    return res.json();
  },

  searchProducts: async (params: { q?: string; category_id?: number; min_price?: number; max_price?: number; sort_by?: string; page?: number }) => {
    const query = new URLSearchParams();
    if (params.q) query.append('q', params.q);
    if (params.category_id) query.append('category_id', params.category_id.toString());
    if (params.min_price) query.append('min_price', params.min_price.toString());
    if (params.max_price) query.append('max_price', params.max_price.toString());
    if (params.sort_by) query.append('sort_by', params.sort_by);
    if (params.page) query.append('page', params.page.toString());

    const res = await fetch(`${API_BASE}/products/search?${query.toString()}`, { headers: getHeaders() });
    return res.json();
  },

  // Cart
  getCart: async (): Promise<Cart> => {
    const res = await fetch(`${API_BASE}/cart`, { headers: getHeaders() });
    return res.json();
  },

  addToCart: async (productId: number, quantity: number = 1) => {
    const res = await fetch(`${API_BASE}/cart/items`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ product_id: productId, quantity })
    });
    return res.json();
  },

  // Orders with Idempotency Key
  createOrder: async (items: { product_id: number; quantity: number }[], idempotencyKey: string): Promise<Order> => {
    const headers = {
      ...getHeaders(),
      'Idempotency-Key': idempotencyKey
    };
    const res = await fetch(`${API_BASE}/orders`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ items })
    });
    if (!res.ok) throw new Error((await res.json())?.error?.message || 'Order creation failed');
    return res.json();
  },

  getOrders: async (): Promise<Order[]> => {
    const res = await fetch(`${API_BASE}/orders`, { headers: getHeaders() });
    return res.json();
  },

  processPayment: async (orderId: number, simulateFailure: boolean = false) => {
    const res = await fetch(`${API_BASE}/payments/${orderId}/process`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ simulate_failure: simulateFailure })
    });
    return res.json();
  },

  // Admin DLQ Inspector
  getDeadLetterEvents: async (): Promise<DeadLetterEvent[]> => {
    const res = await fetch(`${API_BASE}/admin/dead-letter-events`, { headers: getHeaders() });
    return res.json();
  },

  retryDeadLetterEvent: async (eventId: string) => {
    const res = await fetch(`${API_BASE}/admin/outbox-events/${eventId}/retry`, {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to retry event');
    return res.json();
  },

  getTopProducts: async (k: number = 10) => {
    const res = await fetch(`${API_BASE}/analytics/top-products?k=${k}`, { headers: getHeaders() });
    return res.json();
  }
};
