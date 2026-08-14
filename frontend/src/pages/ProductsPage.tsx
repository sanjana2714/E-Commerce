import React, { useState, useEffect } from 'react';
import { Product, Category } from '../types';
import { api } from '../services/api';

interface ProductsPageProps {
  onAddToCart: (productId: number) => void;
}

export const ProductsPage: React.FC<ProductsPageProps> = ({ onAddToCart }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [query, setQuery] = useState('');
  const [categoryId, setCategoryId] = useState<number | undefined>();
  const [minPrice, setMinPrice] = useState<number | undefined>();
  const [maxPrice, setMaxPrice] = useState<number | undefined>();
  const [sortBy, setSortBy] = useState('relevance');
  const [totalHits, setTotalHits] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCategories();
    handleSearch();
  }, []);

  const loadCategories = async () => {
    try {
      const cats = await api.getCategories();
      setCategories(cats);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      const res = await api.searchProducts({
        q: query || undefined,
        category_id: categoryId,
        min_price: minPrice,
        max_price: maxPrice,
        sort_by: sortBy
      });
      setProducts(res.items || []);
      setTotalHits(res.total || 0);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      {/* OpenSearch Search Header */}
      <div className="glass-panel" style={{ marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          🔍 OpenSearch Product Engine ({totalHits} Products)
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <input
            className="input-field"
            type="text"
            placeholder="Search laptop, phone, brand..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <select className="input-field" value={categoryId || ''} onChange={(e) => setCategoryId(e.target.value ? Number(e.target.value) : undefined)}>
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          <input className="input-field" type="number" placeholder="Min Price ($)" value={minPrice || ''} onChange={(e) => setMinPrice(e.target.value ? Number(e.target.value) : undefined)} />
          <input className="input-field" type="number" placeholder="Max Price ($)" value={maxPrice || ''} onChange={(e) => setMaxPrice(e.target.value ? Number(e.target.value) : undefined)} />
          <select className="input-field" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="relevance">Relevance</option>
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
            <option value="rating_desc">Highest Rated</option>
          </select>
          <button className="btn-primary" onClick={handleSearch} disabled={loading}>
            {loading ? 'Searching...' : 'Execute Search'}
          </button>
        </div>
      </div>

      {/* Product Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.5rem' }}>
        {products.map((product) => (
          <div key={product.id} className="glass-panel" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                <span className="badge badge-active">{product.brand}</span>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>⭐ {product.rating}</span>
              </div>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>{product.name}</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>{product.description}</p>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                SKU: <code>{product.sku}</code>
              </div>
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem' }}>
                <span style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--accent-emerald)' }}>${product.price.toFixed(2)}</span>
                <button className="btn-primary" onClick={() => onAddToCart(product.id)}>+ Add to Cart</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
