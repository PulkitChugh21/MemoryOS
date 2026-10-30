/**
 * MemoryOS — Chat Page
 * Premium design with markdown rendering, animated backgrounds, and memory stats.
 * Phase 2: File upload button, facts sidebar section, navigation to Files/Timeline.
 */

import { useState, useEffect, useRef } from 'react';
import type { FormEvent } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { useChatStore } from '../store/chatStore';
import { useAuthStore } from '../store/authStore';
import { projectsApi, memoryApi, factsApi, filesApi } from '../api/client';

interface Project {
  id: string;
  name: string;
  description: string;
  tech_stack: string[];
  project_type: string;
}

interface Fact {
  id: string;
  fact_type: string;
  key: string;
  value: string;
  confidence: number;
  is_stale: boolean;
}

/** Cycling status messages shown while the AI is generating */
const THINKING_PHRASES = [
  { icon: '🔍', text: 'Searching memory...' },
  { icon: '🧠', text: 'Recalling relevant context...' },
  { icon: '⚡', text: 'Connecting the dots...' },
  { icon: '✨', text: 'Crafting response...' },
  { icon: '📡', text: 'Retrieving knowledge...' },
  { icon: '🔗', text: 'Cross-referencing sessions...' },
  { icon: '💭', text: 'Thinking deeply...' },
  { icon: '🧬', text: 'Weaving memories together...' },
];

const FACT_TYPE_ICONS: Record<string, string> = {
  decision: '⚖️',
  preference: '💡',
  entity: '🏷️',
  tech_stack: '🔧',
  goal: '🎯',
  milestone: '🏁',
  open_question: '❓',
  file_fact: '📄',
};

function ThinkingIndicator() {
  const [phraseIndex, setPhraseIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPhraseIndex((prev) => (prev + 1) % THINKING_PHRASES.length);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  const phrase = THINKING_PHRASES[phraseIndex];

  return (
    <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '18px', animation: 'slide-up 0.3s ease-out' }}>
      {/* Avatar */}
      <div style={{ width: '32px', height: '32px', borderRadius: '10px', background: 'var(--color-surface)', border: '1px solid rgba(79, 209, 197, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px', flexShrink: 0, marginRight: '10px', marginTop: '2px' }}>
        🧠
      </div>
      {/* Bubble */}
      <div
        style={{
          background: 'var(--color-surface)',
          border: '1px solid rgba(79, 209, 197, 0.08)',
          borderRadius: '18px',
          borderBottomLeftRadius: '4px',
          padding: '14px 20px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          minWidth: '220px',
        }}
      >
        <div style={{
          width: '8px', height: '8px', borderRadius: '50%',
          background: 'var(--color-recall)',
          animation: 'pulse-glow 1.5s ease-in-out infinite',
          flexShrink: 0,
        }} />
        <span
          key={phraseIndex}
          style={{
            fontSize: '14px',
            color: 'var(--color-text-muted)',
            fontWeight: 500,
            fontStyle: 'italic',
            animation: 'fade-in 0.4s ease-out',
          }}
        >
          {phrase.icon} {phrase.text}
        </span>
      </div>
    </div>
  );
}

export default function ChatPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [input, setInput] = useState('');
  const [stats, setStats] = useState<any>(null);
  const [facts, setFacts] = useState<Fact[]>([]);
  const [isUploadingFile, setIsUploadingFile] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { messages, isLoading, error, sendMessage, clearChat } = useChatStore();
  const { user } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (projectId) { loadProject(); loadStats(); loadFacts(); }
    return () => clearChat();
  }, [projectId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const loadProject = async () => {
    try { const { data } = await projectsApi.get(projectId!); setProject(data); }
    catch { navigate('/projects'); }
  };

  const loadStats = async () => {
    try { const { data } = await memoryApi.stats(projectId!); setStats(data); }
    catch { /* silent */ }
  };

  const loadFacts = async () => {
    try {
      const { data } = await factsApi.list(projectId!, { limit: 20 });
      setFacts(data.facts || []);
    } catch { /* silent — facts may not exist yet */ }
  };

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    const msg = input;
    setInput('');
    await sendMessage(projectId!, msg);
    loadStats();
    loadFacts(); // Refresh facts after each message (extraction may have added new ones)
  };

  const handleFileUpload = async (file: File) => {
    setIsUploadingFile(true);
    setUploadStatus(`Uploading ${file.name}...`);
    try {
      const { data } = await filesApi.upload(projectId!, file);
      setUploadStatus(`✅ ${file.name} — ${data.chunks_embedded} chunks, ${data.facts_extracted} facts`);
      loadStats();
      loadFacts();
      setTimeout(() => setUploadStatus(''), 5000);
    } catch (e: any) {
      const msg = e.response?.data?.error?.message || 'Upload failed';
      setUploadStatus(`❌ ${msg}`);
      setTimeout(() => setUploadStatus(''), 5000);
    }
    setIsUploadingFile(false);
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--color-ink)', overflow: 'hidden' }}>
      {/* Top Bar */}
      <header
        style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '12px 24px', borderBottom: '1px solid rgba(79, 209, 197, 0.06)',
          flexShrink: 0, backdropFilter: 'blur(12px)', background: 'rgba(10, 15, 28, 0.85)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', minWidth: 0 }}>
          <button
            onClick={() => navigate('/projects')}
            className="btn-ghost"
            style={{ padding: '8px 14px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <span style={{ fontSize: '16px' }}>←</span> Projects
          </button>
          <div style={{ width: '1px', height: '24px', background: 'rgba(79, 209, 197, 0.08)', flexShrink: 0 }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
            <div className="pulse pulse--recall" style={{ flexShrink: 0 }} />
            <span style={{ fontFamily: 'var(--font-display)', fontSize: '18px', fontWeight: 600, color: 'var(--color-text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {project?.name || 'Loading...'}
            </span>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
          {/* Phase 2: Navigation links */}
          <button onClick={() => navigate(`/files/${projectId}`)} className="btn-ghost"
            style={{ padding: '6px 12px', fontSize: '12px' }}>📁 Files</button>
          <button onClick={() => navigate(`/timeline/${projectId}`)} className="btn-ghost"
            style={{ padding: '6px 12px', fontSize: '12px' }}>📅 Timeline</button>
          <div style={{ width: '1px', height: '24px', background: 'rgba(79, 209, 197, 0.08)' }} />
          <div style={{ width: '28px', height: '28px', borderRadius: '8px', background: 'linear-gradient(135deg, var(--color-recall), var(--color-purple))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '12px', color: 'var(--color-ink)' }}>
            {user?.name?.charAt(0).toUpperCase() || '?'}
          </div>
          <span style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>{user?.name}</span>
        </div>
      </header>

      {/* Main Content */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Chat Area */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '28px 24px' }}>
            {messages.length === 0 ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                <div style={{ textAlign: 'center', maxWidth: '500px', padding: '0 16px' }}>
                  <div style={{ fontSize: '48px', marginBottom: '20px' }}>🧠</div>
                  <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '28px', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 12px' }}>
                    Start a Conversation
                  </h2>
                  <p style={{ fontSize: '15px', lineHeight: '24px', color: 'var(--color-text-muted)', margin: '0 0 24px' }}>
                    Ask anything about your project. MemoryOS will remember everything across sessions — no need to re-explain.
                  </p>
                  {project?.tech_stack && project.tech_stack.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center' }}>
                      {project.tech_stack.map((tech) => (
                        <span key={tech} className="tech-tag">{tech}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div style={{ maxWidth: '760px', margin: '0 auto' }}>
                {messages.map((msg, i) => (
                  <div
                    key={msg.id}
                    style={{
                      display: 'flex',
                      justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      marginBottom: '18px',
                      animation: `slide-up 0.3s ease-out ${i * 0.02}s both`,
                    }}
                  >
                    {/* Assistant avatar */}
                    {msg.role === 'assistant' && (
                      <div style={{ width: '32px', height: '32px', borderRadius: '10px', background: 'var(--color-surface)', border: '1px solid rgba(79, 209, 197, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px', flexShrink: 0, marginRight: '10px', marginTop: '2px' }}>
                        🧠
                      </div>
                    )}

                    <div
                      style={{
                        maxWidth: '80%',
                        padding: msg.role === 'user' ? '12px 18px' : '16px 20px',
                        borderRadius: '18px',
                        ...(msg.role === 'user'
                          ? {
                              background: 'linear-gradient(135deg, var(--color-recall), #38b2ac)',
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
                      {msg.role === 'user' ? (
                        <div style={{ fontSize: '15px', lineHeight: '24px', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                          {msg.content}
                        </div>
                      ) : (
                        <div className="markdown-content">
                          <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
                            {msg.content}
                          </ReactMarkdown>
                        </div>
                      )}

                      {/* Memory sources */}
                      {msg.role === 'assistant' && msg.sourcesUsed !== undefined && msg.sourcesUsed > 0 && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '10px', paddingTop: '10px', borderTop: '1px solid rgba(79, 209, 197, 0.08)' }}>
                          <div className="pulse pulse--recall" style={{ width: '6px', height: '6px' }} />
                          <span style={{ fontSize: '12px', color: 'var(--color-text-muted)', fontWeight: 500 }}>
                            {msg.sourcesUsed} memory source{msg.sourcesUsed > 1 ? 's' : ''} recalled
                          </span>
                        </div>
                      )}

                      {/* Loading */}
                      {msg.isStreaming && (
                        <div className="loading-dots" style={{ marginTop: '10px' }}>
                          <span /><span /><span />
                        </div>
                      )}
                    </div>

                    {/* User avatar */}
                    {msg.role === 'user' && (
                      <div style={{ width: '32px', height: '32px', borderRadius: '10px', background: 'linear-gradient(135deg, var(--color-recall), var(--color-purple))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '13px', color: 'var(--color-ink)', flexShrink: 0, marginLeft: '10px', marginTop: '2px' }}>
                        {user?.name?.charAt(0).toUpperCase() || '?'}
                      </div>
                    )}
                  </div>
                ))}
                {isLoading && <ThinkingIndicator />}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Upload status banner */}
          {uploadStatus && (
            <div style={{
              margin: '0 24px 8px', padding: '10px 18px', borderRadius: '12px', fontSize: '13px',
              background: uploadStatus.startsWith('❌') ? 'rgba(232, 97, 123, 0.06)' : 'rgba(79, 209, 197, 0.06)',
              border: `1px solid ${uploadStatus.startsWith('❌') ? 'rgba(232, 97, 123, 0.15)' : 'rgba(79, 209, 197, 0.15)'}`,
              color: uploadStatus.startsWith('❌') ? 'var(--color-conflict)' : 'var(--color-recall)',
              animation: 'slide-up 0.2s ease-out',
            }}>
              {uploadStatus}
            </div>
          )}

          {/* Error */}
          {error && (
            <div style={{ margin: '0 24px 8px', padding: '12px 18px', borderRadius: '12px', fontSize: '13px', background: 'rgba(232, 97, 123, 0.06)', border: '1px solid rgba(232, 97, 123, 0.15)', color: 'var(--color-conflict)' }}>
              ⚠️ {error}
            </div>
          )}

          {/* Input */}
          <form onSubmit={handleSend} style={{ padding: '12px 24px 24px', flexShrink: 0 }}>
            <div style={{ maxWidth: '760px', margin: '0 auto', display: 'flex', gap: '8px', background: 'var(--color-surface)', border: '1px solid rgba(79, 209, 197, 0.08)', borderRadius: '18px', padding: '6px 6px 6px 14px', alignItems: 'center' }}>
              {/* File upload button */}
              <input
                ref={fileInputRef}
                type="file"
                style={{ display: 'none' }}
                onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploadingFile}
                title="Upload file to memory"
                style={{
                  background: 'none', border: 'none', cursor: 'pointer', fontSize: '18px',
                  padding: '4px 6px', borderRadius: '8px', opacity: isUploadingFile ? 0.4 : 0.6,
                  transition: 'opacity 0.2s',
                  flexShrink: 0,
                }}
                onMouseEnter={(e) => (e.currentTarget.style.opacity = '1')}
                onMouseLeave={(e) => (e.currentTarget.style.opacity = '0.6')}
              >
                {isUploadingFile ? '⏳' : '📎'}
              </button>

              <input
                id="chat-input"
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about your project..."
                disabled={isLoading}
                autoFocus
                style={{
                  flex: 1, padding: '10px 0', fontSize: '15px', fontFamily: 'var(--font-body)',
                  background: 'transparent', color: 'var(--color-text-primary)',
                  border: 'none', outline: 'none', minWidth: 0,
                }}
              />
              <button
                id="chat-send-button"
                type="submit"
                disabled={isLoading || !input.trim()}
                className="btn-primary"
                style={{ padding: '10px 22px', fontSize: '14px', borderRadius: '14px', flexShrink: 0, fontWeight: 600 }}
              >
                {isLoading ? (
                  <span className="loading-dots"><span /><span /><span /></span>
                ) : 'Send'}
              </button>
            </div>
          </form>
        </div>

        {/* Right Sidebar — Memory Stats + Facts */}
        <aside
          style={{
            width: '280px', borderLeft: '1px solid rgba(79, 209, 197, 0.06)',
            background: 'rgba(17, 24, 39, 0.5)', backdropFilter: 'blur(12px)',
            overflowY: 'auto', padding: '24px', flexShrink: 0,
          }}
        >
          <h3 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--color-text-muted)', margin: '0 0 18px' }}>
            Memory Stats
          </h3>

          {stats ? (
            <div>
              {[
                { label: 'Episodes', value: stats.episodic?.total_episodes ?? 0, icon: '📝' },
                { label: 'Sessions', value: stats.episodic?.total_sessions ?? 0, icon: '🔗' },
                { label: 'Vectors', value: stats.semantic?.points_count ?? 0, icon: '🧮' },
                { label: 'Facts', value: stats.structured?.total_facts ?? 0, icon: '🧠' },
                { label: 'Files', value: stats.files?.total_files ?? 0, icon: '📁' },
              ].map((s) => (
                <div key={s.label} className="stat-card" style={{ marginBottom: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--color-text-muted)', marginBottom: '4px' }}>
                        {s.icon} {s.label}
                      </div>
                      <div style={{ fontFamily: 'var(--font-display)', fontSize: '26px', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                        {s.value}
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              <div className="divider" style={{ margin: '18px 0' }} />

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div className="pulse pulse--healthy" />
                <span style={{ fontSize: '13px', color: 'var(--color-healthy)', fontWeight: 500 }}>Memory Active</span>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '20px 0' }}>
              <div className="loading-dots"><span /><span /><span /></div>
            </div>
          )}

          {/* Phase 2: Structured Facts */}
          {facts.length > 0 && (
            <div style={{ marginTop: '28px' }}>
              <div className="divider" style={{ marginBottom: '18px' }} />
              <h3 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--color-text-muted)', margin: '0 0 12px' }}>
                🧠 Known Facts ({facts.length})
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {facts.slice(0, 10).map((fact) => (
                  <div
                    key={fact.id}
                    style={{
                      padding: '8px 12px', borderRadius: '8px',
                      background: 'rgba(79, 209, 197, 0.03)',
                      border: '1px solid rgba(79, 209, 197, 0.06)',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '5px', marginBottom: '3px' }}>
                      <span style={{ fontSize: '12px' }}>{FACT_TYPE_ICONS[fact.fact_type] || '📌'}</span>
                      <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-recall)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        {fact.fact_type.replace('_', ' ')}
                      </span>
                      {fact.is_stale && (
                        <div className="pulse pulse--stale" style={{ width: '5px', height: '5px', marginLeft: '4px' }} />
                      )}
                    </div>
                    <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-primary)', lineHeight: '16px' }}>
                      {fact.key}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', lineHeight: '16px', marginTop: '2px', overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as const }}>
                      {fact.value}
                    </div>
                  </div>
                ))}
              </div>
              {facts.length > 10 && (
                <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginTop: '8px', textAlign: 'center' }}>
                  +{facts.length - 10} more facts
                </div>
              )}
            </div>
          )}

          {project?.description && (
            <div style={{ marginTop: '28px' }}>
              <div className="divider" style={{ marginBottom: '18px' }} />
              <h3 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--color-text-muted)', margin: '0 0 10px' }}>About</h3>
              <p style={{ fontSize: '13px', lineHeight: '20px', color: 'var(--color-text-primary)', margin: 0, wordBreak: 'break-word' }}>
                {project.description}
              </p>
            </div>
          )}

          {project?.tech_stack && project.tech_stack.length > 0 && (
            <div style={{ marginTop: '18px' }}>
              <h3 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--color-text-muted)', margin: '0 0 10px' }}>Stack</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {project.tech_stack.map((tech) => (
                  <span key={tech} className="tech-tag">{tech}</span>
                ))}
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
