/**
 * MemoryOS — Register Page
 * Matching design system with LoginPage — explicit inline styles.
 */

import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export default function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { register, isLoading, error, clearError } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await register(email, name, password);
    if (useAuthStore.getState().user) {
      navigate('/projects');
    }
  };

  const labelStyle: React.CSSProperties = {
    display: 'block',
    fontFamily: 'var(--font-body)',
    fontSize: '12px',
    lineHeight: '16px',
    fontWeight: 500,
    textTransform: 'uppercase',
    letterSpacing: '0.04em',
    color: 'var(--color-text-muted)',
    marginBottom: '8px',
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '12px 16px',
    borderRadius: '10px',
    fontSize: '15px',
    lineHeight: '24px',
    fontFamily: 'var(--font-body)',
    background: 'var(--color-surface-raised)',
    color: 'var(--color-text-primary)',
    border: '1px solid rgba(139, 150, 172, 0.15)',
    outline: 'none',
    boxSizing: 'border-box',
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--color-ink)',
        padding: '24px',
      }}
    >
      <div style={{ width: '100%', maxWidth: '420px' }}>
        <div
          style={{
            background: 'var(--color-surface)',
            border: '1px solid rgba(79, 209, 197, 0.08)',
            borderRadius: '16px',
            padding: '40px 32px 32px',
            boxShadow: '0 8px 40px rgba(0,0,0,0.4)',
          }}
        >
          {/* Logo */}
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <div className="pulse pulse--recall" style={{ width: '14px', height: '14px' }}></div>
              <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '28px', lineHeight: '36px', fontWeight: 600, color: 'var(--color-text-primary)', margin: 0 }}>
                MemoryOS
              </h1>
            </div>
            <p style={{ fontSize: '13px', lineHeight: '20px', color: 'var(--color-text-muted)', margin: 0 }}>
              Create your persistent AI workspace
            </p>
          </div>

          {/* Error */}
          {error && (
            <div style={{ marginBottom: '20px', padding: '12px 16px', borderRadius: '8px', fontSize: '13px', background: 'rgba(232, 97, 123, 0.08)', border: '1px solid rgba(232, 97, 123, 0.3)', color: 'var(--color-conflict)' }}>
              {error}
              <button onClick={clearError} style={{ float: 'right', background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', opacity: 0.6, fontSize: '14px' }}>✕</button>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '20px' }}>
              <label htmlFor="register-name" style={labelStyle}>Name</label>
              <input id="register-name" type="text" value={name} onChange={(e) => setName(e.target.value)} required placeholder="Your name" style={inputStyle} />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label htmlFor="register-email" style={labelStyle}>Email</label>
              <input id="register-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="you@example.com" style={inputStyle} />
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label htmlFor="register-password" style={labelStyle}>Password</label>
              <input id="register-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} placeholder="Min 8 characters" style={inputStyle} />
            </div>

            <button id="register-submit" type="submit" disabled={isLoading} className="btn-primary" style={{ width: '100%', padding: '12px', fontSize: '15px', lineHeight: '24px' }}>
              {isLoading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <div style={{ height: '1px', margin: '24px 0 20px', background: 'linear-gradient(90deg, transparent, rgba(79, 209, 197, 0.15), transparent)' }}></div>

          <p style={{ textAlign: 'center', fontSize: '13px', color: 'var(--color-text-muted)', margin: 0 }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: 'var(--color-recall)', textDecoration: 'none' }}>Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
