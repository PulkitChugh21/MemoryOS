/**
 * MemoryOS — Timeline Page (Phase 2)
 * Chronological memory timeline merging conversations, file uploads, and extracted facts.
 * Follows the Synaptic Recall design system.
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectsApi, memoryApi } from '../api/client';

interface TimelineEvent {
  event_type: string;
  event_id: string;
  title: string;
  description: string;
  timestamp: string;
  metadata: Record<string, any>;
}

const EVENT_CONFIG: Record<string, { icon: string; color: string; label: string }> = {
  conversation: { icon: '💬', color: 'var(--color-recall)', label: 'Conversation' },
  file_upload: { icon: '📤', color: 'var(--color-purple)', label: 'File Upload' },
  file_update: { icon: '📝', color: 'var(--color-blue)', label: 'File Update' },
  fact_extracted: { icon: '🧠', color: 'var(--color-stale)', label: 'Fact Extracted' },
};

const FILTER_OPTIONS = [
  { key: '', label: 'All', icon: '🔮' },
  { key: 'conversation', label: 'Conversations', icon: '💬' },
  { key: 'file_upload', label: 'Files', icon: '📁' },
  { key: 'fact_extracted', label: 'Facts', icon: '🧠' },
];

function formatTimestamp(iso: string): string {
  const date = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function TimelinePage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<any>(null);
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    if (projectId) { loadProject(); }
  }, [projectId]);

  useEffect(() => {
    if (projectId) loadTimeline();
  }, [projectId, filter]);

  const loadProject = async () => {
    try { const { data } = await projectsApi.get(projectId!); setProject(data); }
    catch { navigate('/projects'); }
  };

  const loadTimeline = async () => {
    setIsLoading(true);
    try {
      const params: Record<string, any> = { limit: 100 };
      if (filter) params.event_type = filter;
      const { data } = await memoryApi.timeline(projectId!, params);
      setEvents(data.events || []);
    } catch {
      setEvents([]);
    }
    setIsLoading(false);
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-ink)' }}>
      {/* Header */}
      <header style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '12px 24px', borderBottom: '1px solid rgba(79, 209, 197, 0.06)',
        backdropFilter: 'blur(12px)', background: 'rgba(10, 15, 28, 0.85)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <button onClick={() => navigate(`/chat/${projectId}`)} className="btn-ghost"
            style={{ padding: '8px 14px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '16px' }}>←</span> Chat
          </button>
          <div style={{ width: '1px', height: '24px', background: 'rgba(79, 209, 197, 0.08)' }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '20px' }}>📅</span>
            <span style={{ fontFamily: 'var(--font-display)', fontSize: '18px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
              {project?.name || 'Loading...'} — Timeline
            </span>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button onClick={() => navigate(`/files/${projectId}`)} className="btn-ghost"
            style={{ padding: '8px 14px', fontSize: '13px' }}>📁 Files</button>
          <button onClick={() => navigate(`/chat/${projectId}`)} className="btn-ghost"
            style={{ padding: '8px 14px', fontSize: '13px' }}>💬 Chat</button>
        </div>
      </header>

      <div style={{ maxWidth: '700px', margin: '0 auto', padding: '32px 24px' }}>
        {/* Filter Chips */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '28px', flexWrap: 'wrap' }}>
          {FILTER_OPTIONS.map((opt) => (
            <button
              key={opt.key}
              onClick={() => setFilter(opt.key)}
              style={{
                padding: '7px 16px', borderRadius: '20px', fontSize: '13px', fontWeight: 500,
                border: '1px solid',
                borderColor: filter === opt.key ? 'var(--color-recall)' : 'rgba(79, 209, 197, 0.1)',
                background: filter === opt.key ? 'rgba(79, 209, 197, 0.1)' : 'var(--color-surface)',
                color: filter === opt.key ? 'var(--color-recall)' : 'var(--color-text-muted)',
                cursor: 'pointer', transition: 'all 0.2s ease',
                fontFamily: 'var(--font-body)',
              }}
            >
              {opt.icon} {opt.label}
            </button>
          ))}
        </div>

        {/* Timeline */}
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '60px' }}>
            <div className="loading-dots"><span /><span /><span /></div>
          </div>
        ) : events.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--color-text-muted)' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
            <div style={{ fontSize: '16px', fontWeight: 500, marginBottom: '8px' }}>No events yet</div>
            <div style={{ fontSize: '13px' }}>Start chatting or upload files to see your memory timeline</div>
          </div>
        ) : (
          <div style={{ position: 'relative' }}>
            {/* Vertical timeline line */}
            <div style={{
              position: 'absolute', left: '15px', top: '8px', bottom: '8px', width: '2px',
              background: 'linear-gradient(to bottom, var(--color-recall), rgba(79, 209, 197, 0.05))',
              borderRadius: '1px',
            }} />

            {events.map((event, i) => {
              const config = EVENT_CONFIG[event.event_type] || EVENT_CONFIG.conversation;
              const isExpanded = expandedId === event.event_id;

              return (
                <div
                  key={event.event_id + i}
                  style={{
                    position: 'relative', paddingLeft: '44px', paddingBottom: '24px',
                    animation: `slide-up 0.3s ease-out ${i * 0.03}s both`,
                  }}
                >
                  {/* Timeline node */}
                  <div style={{
                    position: 'absolute', left: '8px', top: '12px',
                    width: '16px', height: '16px', borderRadius: '50%',
                    background: 'var(--color-ink)',
                    border: `2px solid ${config.color}`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    zIndex: 1,
                  }}>
                    <div style={{
                      width: '6px', height: '6px', borderRadius: '50%',
                      background: config.color,
                    }} />
                  </div>

                  {/* Event card */}
                  <div
                    onClick={() => setExpandedId(isExpanded ? null : event.event_id)}
                    style={{
                      background: 'var(--color-surface)',
                      border: `1px solid ${isExpanded ? config.color : 'rgba(79, 209, 197, 0.06)'}`,
                      borderRadius: '12px',
                      padding: '14px 18px',
                      cursor: 'pointer',
                      transition: 'border-color 0.2s ease',
                    }}
                  >
                    {/* Top row */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
                        <span style={{ fontSize: '16px', flexShrink: 0 }}>{config.icon}</span>
                        <span style={{
                          fontSize: '13px', fontWeight: 600, color: 'var(--color-text-primary)',
                          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                        }}>
                          {event.title}
                        </span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
                        <span style={{
                          padding: '2px 8px', borderRadius: '6px', fontSize: '10px', fontWeight: 600,
                          background: `${config.color}15`, color: config.color,
                          textTransform: 'uppercase', letterSpacing: '0.04em',
                        }}>
                          {config.label}
                        </span>
                        <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
                          {formatTimestamp(event.timestamp)}
                        </span>
                      </div>
                    </div>

                    {/* Description */}
                    {event.description && (
                      <div style={{
                        fontSize: '13px', color: 'var(--color-text-muted)', marginTop: '6px',
                        lineHeight: '20px',
                        ...(!isExpanded ? { overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' } : {}),
                      }}>
                        {event.description}
                      </div>
                    )}

                    {/* Expanded metadata */}
                    {isExpanded && event.metadata && Object.keys(event.metadata).length > 0 && (
                      <div style={{
                        marginTop: '10px', paddingTop: '10px',
                        borderTop: '1px solid rgba(79, 209, 197, 0.06)',
                        display: 'flex', gap: '12px', flexWrap: 'wrap',
                      }}>
                        {Object.entries(event.metadata).map(([k, v]) => (
                          <span key={k} style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                            <span style={{ fontWeight: 600 }}>{k}:</span> {String(v)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
