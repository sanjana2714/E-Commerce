import React, { useState } from 'react';
import { api } from '../services/api';

interface RegisterPageProps {
  onRegisterSuccess: () => void;
  onNavigateLogin: () => void;
}

export const RegisterPage: React.FC<RegisterPageProps> = ({ onRegisterSuccess, onNavigateLogin }) => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('CUSTOMER');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await api.register({ full_name: fullName, email, password, role });
      onRegisterSuccess();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '420px', marginTop: '3rem' }}>
      <div className="glass-panel">
        <h2 style={{ marginBottom: '1.5rem', textAlign: 'center' }}>Create Account</h2>
        {error && (
          <div style={{ padding: '0.75rem', marginBottom: '1rem', background: 'rgba(244,63,94,0.2)', color: '#f87171', borderRadius: '8px', fontSize: '0.85rem' }}>
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Full Name</label>
            <input className="input-field" type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
          </div>
          <div>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Email</label>
            <input className="input-field" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Password</label>
            <input className="input-field" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <div>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Account Role</label>
            <select className="input-field" value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="CUSTOMER">Customer</option>
              <option value="ADMIN">System Admin</option>
              <option value="INVENTORY_MANAGER">Inventory Manager</option>
            </select>
          </div>
          <button className="btn-success" type="submit" style={{ justifyContent: 'center', marginTop: '0.5rem' }}>Register Account</button>
        </form>
        <p style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Already have an account? <span style={{ color: 'var(--accent-primary)', cursor: 'pointer' }} onClick={onNavigateLogin}>Login</span>
        </p>
      </div>
    </div>
  );
};
