/**
 * MemoryOS — Projects List Page
 * Explicit inline styles for proper text alignment and containment.
 */

import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { projectsApi } from '../api/client';

interface Project {
  id: string;
  name: string;
  description: string;
  tech_stack: string[];
  project_type: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newType, setNewType] = useState('software_dev');
  const [isLoading, setIsLoading] = useState(true);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => { loadProjects(); }, []);

  const loadProjects = async () => {
    try {
      const { data } = await projectsApi.list();
      setProjects(data.projects);
    } catch (err) {
      console.error('Failed to load projects', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await projectsApi.create({ name: newName, description: newDesc, project_type: newType });
      setShowCreate(false);
      setNewName('');
      setNewDesc('');
      loadProjects();
    } catch (err) {
      console.error('Failed to create project', err);
    }
  };

  const projectTypeLabel: Record<string, string> = {
    software_dev: '💻 Software',
    research: '🔬 Research',
    business: '📊 Business',
  };

  const labelStyle: React.CSSProperties = {
    display: 'block',
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
    <div style={{ minHeight: '100vh', background: 'var(--color-ink)' }}>
      {/* Header */}
      <header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '16px 24px',
          borderBottom: '1px solid rgba(79, 209, 197, 0.08)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div className="pulse pulse--recall" style={{ width: '10px', height: '10px' }}></div>
          <span
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '20px',
              lineHeight: '28px',
              fontWeight: 600,
              color: 'var(--color-text-primary)',
            }}
          >
            MemoryOS
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>{user?.name}</span>
          <button
            id="logout-button"
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

      <main style={{ maxWidth: '1024px', margin: '0 auto', padding: '32px 24px' }}>
        {/* Title Row */}
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            marginBottom: '32px',
          }}
        >
          <div>
            <h1
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '28px',
                lineHeight: '36px',
                fontWeight: 600,
                color: 'var(--color-text-primary)',
                margin: '0 0 4px 0',
              }}
            >
              Projects
            </h1>
            <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: 0 }}>
              {projects.length} project{projects.length !== 1 ? 's' : ''} with persistent AI memory
            </p>
          </div>
          <button
            id="create-project-button"
            onClick={() => setShowCreate(true)}
            className="btn-primary"
            style={{ padding: '10px 20px', fontSize: '15px', flexShrink: 0 }}
          >
            + New Project
          </button>
        </div>

        {/* Create Project Modal */}
        {showCreate && (
          <div
            style={{
              position: 'fixed',
              inset: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: 'rgba(0,0,0,0.7)',
              backdropFilter: 'blur(4px)',
              zIndex: 50,
              padding: '24px',
            }}
          >
            <div
              style={{
                width: '100%',
                maxWidth: '480px',
                background: 'var(--color-surface)',
                border: '1px solid rgba(79, 209, 197, 0.08)',
                borderRadius: '16px',
                padding: '28px',
                boxShadow: '0 16px 48px rgba(0,0,0,0.5)',
              }}
            >
              <h2
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '20px',
                  lineHeight: '28px',
                  fontWeight: 600,
                  color: 'var(--color-text-primary)',
                  margin: '0 0 24px 0',
                }}
              >
                New Project
              </h2>
              <form onSubmit={handleCreate}>
                <div style={{ marginBottom: '20px' }}>
                  <label htmlFor="project-name-input" style={labelStyle}>Project Name</label>
                  <input id="project-name-input" type="text" value={newName} onChange={(e) => setNewName(e.target.value)} required placeholder="My Awesome Project" style={inputStyle} />
                </div>
                <div style={{ marginBottom: '20px' }}>
                  <label htmlFor="project-desc-input" style={labelStyle}>Description</label>
                  <textarea id="project-desc-input" value={newDesc} onChange={(e) => setNewDesc(e.target.value)} rows={3} placeholder="What is this project about?" style={{ ...inputStyle, resize: 'none' as const }} />
                </div>
                <div style={{ marginBottom: '24px' }}>
                  <label htmlFor="project-type-select" style={labelStyle}>Type</label>
                  <select id="project-type-select" value={newType} onChange={(e) => setNewType(e.target.value)} style={inputStyle}>
                    <option value="software_dev">💻 Software Development</option>
                    <option value="research">🔬 Research & Data Science</option>
                    <option value="business">📊 Business / Product</option>
                  </select>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <button type="button" onClick={() => setShowCreate(false)} style={{ flex: 1, padding: '12px', fontSize: '15px', background: 'var(--color-surface-raised)', color: 'var(--color-text-muted)', border: '1px solid rgba(139, 150, 172, 0.2)', borderRadius: '10px', cursor: 'pointer' }}>
                    Cancel
                  </button>
                  <button id="project-create-submit" type="submit" className="btn-primary" style={{ flex: 1, padding: '12px', fontSize: '15px' }}>
                    Create Project
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Project Grid */}
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '64px 0', color: 'var(--color-text-muted)', fontSize: '13px' }}>
            Loading projects...
          </div>
        ) : projects.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              padding: '60px 24px',
              background: 'var(--color-surface)',
              border: '1px solid rgba(79, 209, 197, 0.08)',
              borderRadius: '16px',
            }}
          >
            <div className="pulse pulse--recall" style={{ width: '20px', height: '20px', margin: '0 auto 20px' }}></div>
            <p style={{ fontFamily: 'var(--font-display)', fontSize: '20px', fontWeight: 600, color: 'var(--color-text-primary)', margin: '0 0 8px 0' }}>No projects yet</p>
            <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: '0 0 24px 0' }}>Create your first project to start building persistent AI memory.</p>
            <button onClick={() => setShowCreate(true)} className="btn-primary" style={{ padding: '10px 24px', fontSize: '15px' }}>+ Create First Project</button>
          </div>
        ) : (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: '16px',
            }}
          >
            {projects.map((project) => (
              <button
                key={project.id}
                id={`project-card-${project.id}`}
                onClick={() => navigate(`/chat/${project.id}`)}
                style={{
                  textAlign: 'left',
                  display: 'flex',
                  flexDirection: 'column',
                  padding: '20px',
                  background: 'var(--color-surface)',
                  border: '1px solid rgba(79, 209, 197, 0.08)',
                  borderRadius: '12px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(79, 209, 197, 0.2)';
                  e.currentTarget.style.background = 'var(--color-surface-raised)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(79, 209, 197, 0.08)';
                  e.currentTarget.style.background = 'var(--color-surface)';
                }}
              >
                {/* Project Name */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <div className="pulse pulse--healthy"></div>
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
                    {project.name}
                  </span>
                </div>

                {/* Description */}
                {project.description && (
                  <p
                    style={{
                      fontSize: '13px',
                      lineHeight: '20px',
                      color: 'var(--color-text-muted)',
                      margin: '0 0 12px 0',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                    }}
                  >
                    {project.description}
                  </p>
                )}

                {/* Tech Stack Tags */}
                {project.tech_stack && project.tech_stack.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '12px' }}>
                    {project.tech_stack.slice(0, 4).map((tech) => (
                      <span
                        key={tech}
                        style={{
                          background: 'rgba(79, 209, 197, 0.08)',
                          color: 'var(--color-recall)',
                          border: '1px solid rgba(79, 209, 197, 0.15)',
                          borderRadius: '6px',
                          padding: '2px 10px',
                          fontSize: '12px',
                          fontWeight: 500,
                        }}
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                )}

                {/* Footer */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginTop: 'auto',
                    paddingTop: '12px',
                    borderTop: '1px solid rgba(79, 209, 197, 0.06)',
                  }}
                >
                  <span style={{ fontSize: '12px', fontWeight: 500, color: 'var(--color-text-muted)', letterSpacing: '0.02em' }}>
                    {projectTypeLabel[project.project_type] || project.project_type}
                  </span>
                  <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
                    {new Date(project.updated_at).toLocaleDateString()}
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
