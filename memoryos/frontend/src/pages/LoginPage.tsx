/**
 * MemoryOS — Login Page
 * Premium glassmorphism design with animated gradient background.
 */

import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading, error, clearError } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await login(email, password);
    if (useAuthStore.getState().user) {
      navigate('/projects');
    }
  };

  const labelStyle: React.CSSProperties = {
    display: 'block',
    fontSize: '12px',
    fontWeight: 500,
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
    color: 'var(--color-text-muted)',
    marginBottom: '8px',
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '13px 16px',
    borderRadius: '12px',
    fontSize: '15px',
    lineHeight: '24px',
    fontFamily: 'var(--font-body)',
    background: 'var(--color-surface-raised)',
    color: 'var(--color-text-primary)',
    border: '1px solid rgba(139, 150, 172, 0.12)',
    outline: 'none',
    boxSizing: 'border-box' as const,
    transition: 'border-color 0.25s, box-shadow 0.25s',
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', position: 'relative', overflow: 'hidden' }}>
      {/* Animated background */}
      <div className="bg-gradient-animated" />
      <div className="bg-grid" />

      {/* Left hero panel */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          padding: '60px',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <div style={{ maxWidth: '480px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '32px' }}>
            <div className="pulse pulse--recall" style={{ width: '16px', height: '16px' }} />
            <span style={{ fontFamily: 'var(--font-display)', fontSize: '24px', fontWeight: 700, color: 'var(--color-recall)' }}>
              MemoryOS
            </span>
          </div>
          <h1
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '44px',
              lineHeight: '52px',
              fontWeight: 700,
              color: 'var(--color-text-primary)',
              marginBottom: '20px',
            }}
          >
            AI that{' '}
            <span style={{ background: 'linear-gradient(135deg, var(--color-recall), var(--color-recall-bright))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              remembers
            </span>{' '}
            everything.
          </h1>
          <p style={{ fontSize: '17px', lineHeight: '28px', color: 'var(--color-text-muted)', marginBottom: '40px' }}>
            Persistent semantic memory for every project. No more re-explaining context — your AI partner remembers across every session.
          </p>
          <div style={{ display: 'flex', gap: '24px' }}>
            {[
              { icon: '🧠', label: 'Episodic Memory', desc: 'Remembers conversations' },
              { icon: '🔍', label: 'Semantic Search', desc: 'Finds relevant context' },
              { icon: '🔗', label: 'Cross-Session', desc: 'Never forgets' },
            ].map((f) => (
              <div key={f.label} style={{ flex: 1 }}>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>{f.icon}</div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '14px', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '4px' }}>{f.label}</div>
                <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>{f.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right login form */}
      <div
        style={{
          width: '480px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <div
          style={{
            width: '100%',
            maxWidth: '380px',
            background: 'var(--color-surface)',
            border: '1px solid rgba(79, 209, 197, 0.1)',
            borderRadius: '20px',
            padding: '40px 32px',
            boxShadow: '0 16px 64px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(79, 209, 197, 0.05)',
          }}
        >
          <h2
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '24px',
              fontWeight: 600,
              color: 'var(--color-text-primary)',
              marginBottom: '4px',
            }}
          >
            Welcome back
          </h2>
          <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', marginBottom: '28px' }}>
            Sign in to your workspace
          </p>

          {error && (
            <div
              style={{
                marginBottom: '20px',
                padding: '12px 16px',
                borderRadius: '10px',
                fontSize: '13px',
                background: 'rgba(232, 97, 123, 0.08)',
                border: '1px solid rgba(232, 97, 123, 0.25)',
                color: 'var(--color-conflict)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <span>{error}</span>
              <button onClick={clearError} style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', opacity: 0.6, fontSize: '14px', padding: '0 0 0 8px' }}>✕</button>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '20px' }}>
              <label htmlFor="login-email" style={labelStyle}>Email</label>
              <input
                id="login-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
                style={inputStyle}
                onFocus={(e) => { e.target.style.borderColor = 'var(--color-recall)'; e.target.style.boxShadow = '0 0 0 3px rgba(79, 209, 197, 0.1)'; }}
                onBlur={(e) => { e.target.style.borderColor = 'rgba(139, 150, 172, 0.12)'; e.target.style.boxShadow = 'none'; }}
              />
            </div>

            <div style={{ marginBottom: '28px' }}>
              <label htmlFor="login-password" style={labelStyle}>Password</label>
              <input
                id="login-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                placeholder="••••••••"
                style={inputStyle}
                onFocus={(e) => { e.target.style.borderColor = 'var(--color-recall)'; e.target.style.boxShadow = '0 0 0 3px rgba(79, 209, 197, 0.1)'; }}
                onBlur={(e) => { e.target.style.borderColor = 'rgba(139, 150, 172, 0.12)'; e.target.style.boxShadow = 'none'; }}
              />
            </div>

            <button
              id="login-submit"
              type="submit"
              disabled={isLoading}
              className="btn-primary"
              style={{ width: '100%', padding: '13px', fontSize: '15px' }}
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div style={{ height: '1px', margin: '24px 0', background: 'linear-gradient(90deg, transparent, rgba(79, 209, 197, 0.15), transparent)' }} />

          <p style={{ textAlign: 'center', fontSize: '14px', color: 'var(--color-text-muted)' }}>
            Don't have an account?{' '}
            <Link to="/register" style={{ color: 'var(--color-recall)', textDecoration: 'none', fontWeight: 500 }}>
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
