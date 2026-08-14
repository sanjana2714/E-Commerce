export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'CUSTOMER' | 'ADMIN' | 'INVENTORY_MANAGER';
  is_active: boolean;
  created_at: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
}

export interface Product {
  id: number;
  sku: string;
  name: string;
  description?: string;
  category_id: number;
  brand: string;
  price: number;
  currency: string;
  rating: number;
  status: 'ACTIVE' | 'INACTIVE' | 'DISCONTINUED';
  stock_quantity?: number;
}

export interface CartItem {
  id: number;
  product_id: number;
  quantity: number;
  unit_price: number;
  product?: Product;
}

export interface Cart {
  id: number;
  user_id: number;
  total_amount: number;
  items: CartItem[];
}

export interface OrderItem {
  id: number;
  product_id: number;
  quantity: number;
  unit_price: number;
  subtotal: number;
  product?: Product;
}

export interface Order {
  id: number;
  user_id: number;
  idempotency_key: string;
  status: 'PENDING' | 'CONFIRMED' | 'PROCESSING' | 'SHIPPED' | 'DELIVERED' | 'FAILED' | 'CANCELLED';
  total_amount: number;
  currency: string;
  created_at: string;
  items: OrderItem[];
}

export interface DeadLetterEvent {
  id: number;
  event_id: string;
  aggregate_type: string;
  aggregate_id: string;
  event_type: string;
  payload: any;
  status: string;
  retry_count: number;
  error_message: string;
  created_at: string;
}
