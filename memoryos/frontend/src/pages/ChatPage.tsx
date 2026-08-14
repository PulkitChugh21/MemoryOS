/**
 * MemoryOS — Chat Page
 * Explicit inline styles for proper containment. No Tailwind class conflicts.
 */

import { useState, useEffect, useRef } from 'react';
import type { FormEvent } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useChatStore } from '../store/chatStore';
import { useAuthStore } from '../store/authStore';
import { projectsApi, memoryApi } from '../api/client';

interface Project {
  id: string;
  name: string;
  description: string;
  tech_stack: string[];
  project_type: string;
}

export default function ChatPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [input, setInput] = useState('');
  const [stats, setStats] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, isLoading, error, sendMessage, clearChat } = useChatStore();
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (projectId) { loadProject(); loadStats(); }
    return () => clearChat();
  }, [projectId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadProject = async () => {
    try { const { data } = await projectsApi.get(projectId!); setProject(data); }
    catch { navigate('/projects'); }
  };

  const loadStats = async () => {
    try { const { data } = await memoryApi.stats(projectId!); setStats(data); }
    catch { /* silent */ }
  };

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    const msg = input;
    setInput('');
    await sendMessage(projectId!, msg);
    loadStats();
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--color-ink)', overflow: 'hidden' }}>
      {/* Top Bar */}
      <header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 20px',
          borderBottom: '1px solid rgba(79, 209, 197, 0.08)',
          flexShrink: 0,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0 }}>
          <button
            onClick={() => navigate('/projects')}
            style={{
              padding: '6px 12px',
              fontSize: '13px',
              color: 'var(--color-text-muted)',
              background: 'transparent',
              border: '1px solid rgba(139, 150, 172, 0.2)',
              borderRadius: '8px',
              cursor: 'pointer',
              flexShrink: 0,
            }}
          >
            ← Projects
          </button>
          <div style={{ width: '1px', height: '20px', background: 'rgba(79, 209, 197, 0.1)', flexShrink: 0 }}></div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
            <div className="pulse pulse--recall" style={{ flexShrink: 0 }}></div>
            <span
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '18px',
                lineHeight: '24px',
                fontWeight: 600,
                color: 'var(--color-text-primary)',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {project?.name || 'Loading...'}
            </span>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexShrink: 0 }}>
          <span style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>{user?.name}</span>
          <button
            onClick={logout}
            style={{
              padding: '6px 14px',
              fontSize: '13px',
              color: 'var(--color-text-muted)',
              background: 'transparent',
              border: '1px solid rgba(139, 150, 172, 0.2)',
              borderRadius: '8px',
              cursor: 'pointer',
            }}
          >
            Sign Out
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Chat Area */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '24px 20px' }}>
            {messages.length === 0 ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                <div style={{ textAlign: 'center', maxWidth: '480px', padding: '0 16px' }}>
                  <div className="pulse pulse--recall" style={{ width: '24px', height: '24px', margin: '0 auto 20px' }}></div>
                  <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '28px', lineHeight: '36px', fontWeight: 600, color: 'var(--color-text-primary)', margin: '0 0 12px 0' }}>
                    Start a Conversation
                  </h2>
                  <p style={{ fontSize: '15px', lineHeight: '24px', color: 'var(--color-text-muted)', margin: '0 0 20px 0' }}>
                    Ask anything about your project. MemoryOS will remember everything across sessions — no need to re-explain.
                  </p>
                  {project?.tech_stack && project.tech_stack.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center' }}>
                      {project.tech_stack.map((tech) => (
                        <span key={tech} style={{ background: 'rgba(79, 209, 197, 0.08)', color: 'var(--color-recall)', border: '1px solid rgba(79, 209, 197, 0.15)', borderRadius: '6px', padding: '2px 10px', fontSize: '12px', fontWeight: 500 }}>
                          {tech}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div style={{ maxWidth: '720px', margin: '0 auto' }}>
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    style={{
                      display: 'flex',
                      justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      marginBottom: '16px',
                    }}
                  >
                    <div
                      style={{
                        maxWidth: '80%',
                        padding: '12px 16px',
                        borderRadius: '16px',
                        ...(msg.role === 'user'
                          ? {
                              background: 'linear-gradient(135deg, var(--color-recall), #3abfb3)',
                              color: 'var(--color-ink)',
                              borderBottomRightRadius: '4px',
                            }
                          : {
                              background: 'var(--color-surface)',
                              color: 'var(--color-text-primary)',
                              border: '1px solid rgba(79, 209, 197, 0.06)',
                              borderBottomLeftRadius: '4px',
                            }),
                      }}
                    >
                      <div style={{ fontSize: '15px', lineHeight: '24px', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                        {msg.content}
                      </div>

                      {/* Memory sources */}
                      {msg.role === 'assistant' && msg.sourcesUsed !== undefined && msg.sourcesUsed > 0 && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '8px', paddingTop: '8px', borderTop: '1px solid rgba(79, 209, 197, 0.08)' }}>
                          <div className="pulse pulse--recall" style={{ width: '6px', height: '6px' }}></div>
                          <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
                            {msg.sourcesUsed} memory source{msg.sourcesUsed > 1 ? 's' : ''} recalled
                          </span>
                        </div>
                      )}

                      {/* Loading */}
                      {msg.isStreaming && (
                        <div className="loading-dots" style={{ marginTop: '8px' }}>
                          <span></span><span></span><span></span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Error */}
          {error && (
            <div style={{ margin: '0 20px 8px', padding: '12px 16px', borderRadius: '8px', fontSize: '13px', background: 'rgba(232, 97, 123, 0.08)', border: '1px solid rgba(232, 97, 123, 0.2)', color: 'var(--color-conflict)' }}>
              {error}
            </div>
          )}

          {/* Input */}
          <form onSubmit={handleSend} style={{ padding: '8px 20px 20px', flexShrink: 0 }}>
            <div style={{ maxWidth: '720px', margin: '0 auto', display: 'flex', gap: '12px' }}>
              <input
                id="chat-input"
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about your project..."
                disabled={isLoading}
                autoFocus
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  borderRadius: '14px',
                  fontSize: '15px',
                  lineHeight: '24px',
                  fontFamily: 'var(--font-body)',
                  background: 'var(--color-surface)',
                  color: 'var(--color-text-primary)',
                  border: '1px solid rgba(139, 150, 172, 0.15)',
                  outline: 'none',
                  boxSizing: 'border-box',
                  minWidth: 0,
                }}
              />
              <button
                id="chat-send-button"
                type="submit"
                disabled={isLoading || !input.trim()}
                className="btn-primary"
                style={{ padding: '12px 24px', fontSize: '15px', borderRadius: '14px', flexShrink: 0 }}
              >
                {isLoading ? '...' : 'Send'}
              </button>
            </div>
          </form>
        </div>

        {/* Right Sidebar — Memory Stats */}
        <aside
          style={{
            width: '260px',
            borderLeft: '1px solid rgba(79, 209, 197, 0.08)',
            background: 'var(--color-surface)',
            overflowY: 'auto',
            padding: '20px',
            flexShrink: 0,
          }}
        >
          <h3 style={{ fontSize: '12px', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--color-text-muted)', margin: '0 0 16px 0' }}>
            Memory Stats
          </h3>

          {stats ? (
            <div>
              {/* Stat cards */}
              {[
                { label: 'Episodes', value: stats.episodic?.total_episodes ?? 0 },
                { label: 'Sessions', value: stats.episodic?.total_sessions ?? 0 },
                { label: 'Vectors', value: stats.semantic?.points_count ?? 0 },
              ].map((s) => (
                <div
                  key={s.label}
                  style={{
                    background: 'rgba(30, 42, 69, 0.6)',
                    border: '1px solid rgba(79, 209, 197, 0.06)',
                    borderRadius: '10px',
                    padding: '12px 16px',
                    marginBottom: '10px',
                  }}
                >
                  <div style={{ fontSize: '12px', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--color-text-muted)', marginBottom: '4px' }}>
                    {s.label}
                  </div>
                  <div style={{ fontFamily: 'var(--font-display)', fontSize: '24px', lineHeight: '32px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                    {s.value}
                  </div>
                </div>
              ))}

              {/* Divider */}
              <div style={{ height: '1px', margin: '16px 0', background: 'linear-gradient(90deg, transparent, rgba(79, 209, 197, 0.15), transparent)' }}></div>

              {/* Status */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div className="pulse pulse--healthy"></div>
                <span style={{ fontSize: '13px', color: 'var(--color-healthy)' }}>Memory Active</span>
              </div>
            </div>
          ) : (
            <p style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>Loading...</p>
          )}

          {/* Project Info */}
          {project?.description && (
            <div style={{ marginTop: '24px' }}>
              <div style={{ height: '1px', marginBottom: '16px', background: 'linear-gradient(90deg, transparent, rgba(79, 209, 197, 0.15), transparent)' }}></div>
              <h3 style={{ fontSize: '12px', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--color-text-muted)', margin: '0 0 8px 0' }}>
                About
              </h3>
              <p style={{ fontSize: '13px', lineHeight: '20px', color: 'var(--color-text-primary)', margin: 0, wordBreak: 'break-word' }}>
                {project.description}
              </p>
            </div>
          )}

          {project?.tech_stack && project.tech_stack.length > 0 && (
            <div style={{ marginTop: '16px' }}>
              <h3 style={{ fontSize: '12px', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--color-text-muted)', margin: '0 0 8px 0' }}>
                Stack
              </h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {project.tech_stack.map((tech) => (
                  <span key={tech} style={{ background: 'rgba(79, 209, 197, 0.08)', color: 'var(--color-recall)', border: '1px solid rgba(79, 209, 197, 0.15)', borderRadius: '6px', padding: '2px 10px', fontSize: '12px', fontWeight: 500 }}>
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
