import React, { useState } from 'react';
import { api } from '../services/api';

interface LoginPageProps {
  onLoginSuccess: () => void;
  onNavigateRegister: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess, onNavigateRegister }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await api.login({ email, password });
      localStorage.setItem('access_token', res.access_token);
      onLoginSuccess();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '420px', marginTop: '3rem' }}>
      <div className="glass-panel">
        <h2 style={{ marginBottom: '1.5rem', textAlign: 'center' }}>Sign In</h2>
        {error && (
          <div style={{ padding: '0.75rem', marginBottom: '1rem', background: 'rgba(244,63,94,0.2)', color: '#f87171', borderRadius: '8px', fontSize: '0.85rem' }}>
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Email</label>
            <input className="input-field" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Password</label>
            <input className="input-field" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button className="btn-primary" type="submit" style={{ justifyContent: 'center', marginTop: '0.5rem' }}>Login</button>
        </form>
        <p style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Don't have an account? <span style={{ color: 'var(--accent-primary)', cursor: 'pointer' }} onClick={onNavigateRegister}>Register</span>
        </p>
      </div>
    </div>
  );
};
