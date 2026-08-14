import React, { useState, useEffect } from 'react';
import { DeadLetterEvent } from '../types';
import { api } from '../services/api';

export const AdminPage: React.FC = () => {
  const [dlqEvents, setDlqEvents] = useState<DeadLetterEvent[]>([]);
  const [topProducts, setTopProducts] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'analytics' | 'dlq'>('analytics');
  const [retryingId, setRetryingId] = useState<string | null>(null);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async (): Promise<void> => {
    try {
      const dlq = await api.getDeadLetterEvents();
      setDlqEvents(dlq || []);
      const top = await api.getTopProducts(5);
      setTopProducts(top || []);
    } catch (e) {
      console.error('Failed to load admin data:', e);
    }
  };

  const handleRetryEvent = async (eventId: string): Promise<void> => {
    setRetryingId(eventId);
    try {
      await api.retryDeadLetterEvent(eventId);
      setDlqEvents((prev: DeadLetterEvent[]) => prev.filter((e: DeadLetterEvent) => e.event_id !== eventId));
    } catch (err) {
      console.error('Failed to retry event:', err);
    } finally {
      setRetryingId(null);
    }
  };

  return (
    <div className="container">
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
        <button
          onClick={() => setActiveTab('analytics')}
          style={{
            background: activeTab === 'analytics' ? 'var(--accent-blue)' : 'transparent',
            color: '#fff',
            border: 'none',
            padding: '0.6rem 1.2rem',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 600
          }}
        >
          📊 Heap Analytics (O(N log K))
        </button>
        <button
          onClick={() => setActiveTab('dlq')}
          style={{
            background: activeTab === 'dlq' ? 'var(--accent-rose)' : 'transparent',
            color: '#fff',
            border: 'none',
            padding: '0.6rem 1.2rem',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 600
          }}
        >
          🚨 DLQ Inspector ({dlqEvents.length})
        </button>
      </div>

      {activeTab === 'analytics' && (
        <div className="glass-panel">
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            📊 Top-K Sales Heap Analytics (O(N log K))
          </h3>
          {topProducts.length === 0 ? (
            <p style={{ color: 'var(--text-secondary)' }}>No sales analytics recorded yet.</p>
          ) : (
            <div>
              {topProducts.map((p: any, idx: number) => (
                <div key={p.id || idx} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem 0', borderBottom: '1px solid var(--border-color)' }}>
                  <span>
                    <strong>#{idx + 1}</strong> {p.name || 'Product'} {p.brand ? `(${p.brand})` : ''}
                  </span>
                  <span style={{ fontWeight: 600, color: 'var(--accent-emerald)' }}>
                    {p.sales_count || p.sales || 0} Units Sold
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'dlq' && (
        <div className="glass-panel">
          <h3 style={{ marginBottom: '1rem', color: 'var(--accent-rose)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            🚨 Dead Letter Queue (DLQ) Inspector & Outbox Event Bus
          </h3>
          {dlqEvents.length === 0 ? (
            <div style={{ padding: '1.25rem', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
              ✅ <strong>Healthy Pipeline:</strong> Zero failed events in Dead Letter Queue. All Kafka outbox messages delivered successfully.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {dlqEvents.map((evt: DeadLetterEvent) => (
                <div
                  key={evt.id || evt.event_id}
                  style={{
                    padding: '1rem',
                    background: 'rgba(244,63,94,0.08)',
                    border: '1px solid var(--accent-rose)',
                    borderRadius: '8px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.5rem'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fda4af' }}>
                      Event: {evt.event_type}
                    </span>
                    <button
                      onClick={() => handleRetryEvent(evt.event_id)}
                      disabled={retryingId === evt.event_id}
                      style={{
                        padding: '0.35rem 0.75rem',
                        fontSize: '0.8rem',
                        background: 'var(--accent-rose)',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                      }}
                    >
                      {retryingId === evt.event_id ? 'Replaying Event...' : '🔄 Replay to Kafka'}
                    </button>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    Event UUID: <code>{evt.event_id}</code> | Created: {evt.created_at || 'Recently'}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#f87171', background: 'rgba(0,0,0,0.3)', padding: '0.5rem', borderRadius: '4px' }}>
                    Reason: {evt.error_message || 'Kafka Broker Connection Exception / Consumer Max Retry Exhausted'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
