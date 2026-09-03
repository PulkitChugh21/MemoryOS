/**
 * MemoryOS — Projects List Page
 * Premium design with project management (delete, rename) + user profile dropdown.
 */

import { useState, useEffect, useRef } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { projectsApi, authApi } from '../api/client';

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
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [editName, setEditName] = useState('');
  const [editDesc, setEditDesc] = useState('');
  const [profileName, setProfileName] = useState('');
  const [profileEmail, setProfileEmail] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [profileMsg, setProfileMsg] = useState('');
  const [showDeleteAccount, setShowDeleteAccount] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => { loadProjects(); }, []);
  useEffect(() => {
    if (user) { setProfileName(user.name); setProfileEmail(user.email); }
  }, [user]);

  // Close user menu on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setShowUserMenu(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const loadProjects = async () => {
    try {
      const { data } = await projectsApi.list();
      setProjects(data.projects);
    } catch (err) { console.error('Failed to load projects', err); }
    finally { setIsLoading(false); }
  };

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await projectsApi.create({ name: newName, description: newDesc, project_type: newType });
      setShowCreate(false); setNewName(''); setNewDesc('');
      loadProjects();
    } catch (err) { console.error('Failed to create project', err); }
  };

  const handleDelete = async (id: string) => {
    try {
      await projectsApi.delete(id);
      setShowDeleteConfirm(null);
      loadProjects();
    } catch (err) { console.error('Failed to delete project', err); }
  };

  const handleRename = async (e: FormEvent) => {
    e.preventDefault();
    if (!editingProject) return;
    try {
      await projectsApi.update(editingProject.id, { name: editName, description: editDesc });
      setEditingProject(null);
      loadProjects();
    } catch (err) { console.error('Failed to update project', err); }
  };

  const handleUpdateProfile = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await authApi.updateProfile({ name: profileName, email: profileEmail });
      setProfileMsg('Profile updated!');
      // Refresh user data
      const { data } = await authApi.me();
      useAuthStore.setState({ user: data });
      setTimeout(() => setProfileMsg(''), 3000);
    } catch (err: any) {
      setProfileMsg(err.response?.data?.detail?.error?.message || 'Update failed');
    }
  };

  const handleChangePassword = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await authApi.changePassword({ current_password: currentPassword, new_password: newPassword });
      setProfileMsg('Password changed!');
      setCurrentPassword(''); setNewPassword('');
      setTimeout(() => setProfileMsg(''), 3000);
    } catch (err: any) {
      setProfileMsg(err.response?.data?.detail?.error?.message || 'Password change failed');
    }
  };

  const handleDeleteAccount = async () => {
    try {
      await authApi.deleteAccount();
      logout();
    } catch (err) { console.error('Failed to delete account', err); }
  };

  const projectTypeLabel: Record<string, string> = {
    software_dev: '💻 Software',
    research: '🔬 Research',
    business: '📊 Business',
  };

  const labelStyle: React.CSSProperties = { display: 'block', fontSize: '12px', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--color-text-muted)', marginBottom: '8px' };
  const inputStyle: React.CSSProperties = { width: '100%', padding: '13px 16px', borderRadius: '12px', fontSize: '15px', fontFamily: 'var(--font-body)', background: 'var(--color-surface-raised)', color: 'var(--color-text-primary)', border: '1px solid rgba(139, 150, 172, 0.12)', outline: 'none', boxSizing: 'border-box' as const };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-ink)', position: 'relative' }}>
      <div className="bg-gradient-animated" />
      <div className="bg-grid" />

      {/* Header */}
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 28px', borderBottom: '1px solid rgba(79, 209, 197, 0.06)', position: 'relative', zIndex: 10, backdropFilter: 'blur(12px)', background: 'rgba(10, 15, 28, 0.8)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div className="pulse pulse--recall" style={{ width: '10px', height: '10px' }} />
          <span style={{ fontFamily: 'var(--font-display)', fontSize: '20px', fontWeight: 700, color: 'var(--color-text-primary)' }}>MemoryOS</span>
          <span className="badge badge--recall" style={{ marginLeft: '8px' }}>Phase 1</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', position: 'relative' }} ref={menuRef}>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            style={{
              display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 14px',
              background: showUserMenu ? 'var(--color-surface-raised)' : 'transparent',
              border: '1px solid rgba(139, 150, 172, 0.12)', borderRadius: '12px', cursor: 'pointer', transition: 'all 0.2s',
            }}
          >
            <div style={{ width: '32px', height: '32px', borderRadius: '10px', background: 'linear-gradient(135deg, var(--color-recall), var(--color-purple))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '14px', color: 'var(--color-ink)' }}>
              {user?.name?.charAt(0).toUpperCase() || '?'}
            </div>
            <span style={{ fontSize: '14px', color: 'var(--color-text-primary)', fontWeight: 500 }}>{user?.name}</span>
            <span style={{ fontSize: '10px', color: 'var(--color-text-muted)', transform: showUserMenu ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}>▼</span>
          </button>

          {showUserMenu && (
            <div style={{ position: 'absolute', top: '100%', right: 0, marginTop: '8px', width: '220px', background: 'var(--color-surface)', border: '1px solid rgba(79, 209, 197, 0.1)', borderRadius: '14px', padding: '6px', boxShadow: '0 16px 48px rgba(0,0,0,0.5)', zIndex: 50, animation: 'slide-up 0.2s ease-out' }}>
              <button onClick={() => { setShowProfile(true); setShowUserMenu(false); }} style={{ width: '100%', textAlign: 'left', padding: '10px 14px', background: 'transparent', border: 'none', color: 'var(--color-text-primary)', fontSize: '14px', cursor: 'pointer', borderRadius: '10px', transition: 'background 0.15s' }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'var(--color-surface-raised)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
                👤 Profile Settings
              </button>
              <div style={{ height: '1px', margin: '4px 10px', background: 'rgba(79, 209, 197, 0.06)' }} />
              <button onClick={() => { logout(); setShowUserMenu(false); }} style={{ width: '100%', textAlign: 'left', padding: '10px 14px', background: 'transparent', border: 'none', color: 'var(--color-conflict)', fontSize: '14px', cursor: 'pointer', borderRadius: '10px', transition: 'background 0.15s' }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(232, 97, 123, 0.06)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
                🚪 Sign Out
              </button>
            </div>
          )}
        </div>
      </header>

      <main style={{ maxWidth: '1080px', margin: '0 auto', padding: '40px 28px', position: 'relative', zIndex: 1 }}>
        {/* Title Row */}
        <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginBottom: '36px' }}>
          <div>
            <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '32px', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 6px 0' }}>Projects</h1>
            <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', margin: 0 }}>
              {projects.length} workspace{projects.length !== 1 ? 's' : ''} with persistent AI memory
            </p>
          </div>
          <button id="create-project-button" onClick={() => setShowCreate(true)} className="btn-primary" style={{ padding: '12px 24px', fontSize: '15px', flexShrink: 0 }}>
            + New Project
          </button>
        </div>

        {/* Project Grid */}
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '80px 0' }}>
            <div className="loading-dots"><span /><span /><span /></div>
            <p style={{ marginTop: '16px', color: 'var(--color-text-muted)', fontSize: '14px' }}>Loading projects...</p>
          </div>
        ) : projects.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '80px 24px', background: 'var(--color-surface)', border: '1px solid rgba(79, 209, 197, 0.08)', borderRadius: '20px' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🧠</div>
            <p style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 600, color: 'var(--color-text-primary)', margin: '0 0 8px' }}>No projects yet</p>
            <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', margin: '0 0 28px' }}>Create your first project to start building persistent AI memory.</p>
            <button onClick={() => setShowCreate(true)} className="btn-primary" style={{ padding: '12px 28px', fontSize: '15px' }}>+ Create First Project</button>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '18px' }}>
            {projects.map((project, i) => (
              <div
                key={project.id}
                className="card"
                style={{ display: 'flex', flexDirection: 'column', padding: '22px', cursor: 'pointer', animation: `slide-up 0.4s ease-out ${i * 0.05}s both` }}
                onClick={() => navigate(`/chat/${project.id}`)}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
                    <div className="pulse pulse--healthy" />
                    <span style={{ fontFamily: 'var(--font-display)', fontSize: '18px', fontWeight: 600, color: 'var(--color-text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {project.name}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: '4px', flexShrink: 0 }} onClick={(e) => e.stopPropagation()}>
                    <button
                      title="Rename"
                      onClick={() => { setEditingProject(project); setEditName(project.name); setEditDesc(project.description); }}
                      style={{ padding: '6px 8px', background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '14px', borderRadius: '8px', transition: 'background 0.15s', color: 'var(--color-text-muted)' }}
                      onMouseEnter={(e) => e.currentTarget.style.background = 'var(--color-surface-raised)'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                    >✏️</button>
                    <button
                      title="Delete"
                      onClick={() => setShowDeleteConfirm(project.id)}
                      style={{ padding: '6px 8px', background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '14px', borderRadius: '8px', transition: 'background 0.15s', color: 'var(--color-text-muted)' }}
                      onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(232, 97, 123, 0.08)'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                    >🗑️</button>
                  </div>
                </div>

                {project.description && (
                  <p style={{ fontSize: '13px', lineHeight: '20px', color: 'var(--color-text-muted)', margin: '0 0 12px', overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                    {project.description}
                  </p>
                )}

                {project.tech_stack?.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '14px' }}>
                    {project.tech_stack.slice(0, 4).map((tech) => (
                      <span key={tech} className="tech-tag">{tech}</span>
                    ))}
                  </div>
                )}

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 'auto', paddingTop: '14px', borderTop: '1px solid rgba(79, 209, 197, 0.04)' }}>
                  <span style={{ fontSize: '12px', fontWeight: 500, color: 'var(--color-text-muted)' }}>{projectTypeLabel[project.project_type] || project.project_type}</span>
                  <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>{new Date(project.updated_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Create Project Modal */}
      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '24px' }}>New Project</h2>
            <form onSubmit={handleCreate}>
              <div style={{ marginBottom: '18px' }}>
                <label htmlFor="project-name-input" style={labelStyle}>Project Name</label>
                <input id="project-name-input" type="text" value={newName} onChange={(e) => setNewName(e.target.value)} required placeholder="My Awesome Project" style={inputStyle} />
              </div>
              <div style={{ marginBottom: '18px' }}>
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
                <button type="button" onClick={() => setShowCreate(false)} className="btn-ghost" style={{ flex: 1, padding: '13px', fontSize: '15px' }}>Cancel</button>
                <button id="project-create-submit" type="submit" className="btn-primary" style={{ flex: 1, padding: '13px', fontSize: '15px' }}>Create Project</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Rename Project Modal */}
      {editingProject && (
        <div className="modal-overlay" onClick={() => setEditingProject(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '24px' }}>Edit Project</h2>
            <form onSubmit={handleRename}>
              <div style={{ marginBottom: '18px' }}>
                <label style={labelStyle}>Project Name</label>
                <input type="text" value={editName} onChange={(e) => setEditName(e.target.value)} required style={inputStyle} />
              </div>
              <div style={{ marginBottom: '24px' }}>
                <label style={labelStyle}>Description</label>
                <textarea value={editDesc} onChange={(e) => setEditDesc(e.target.value)} rows={3} style={{ ...inputStyle, resize: 'none' as const }} />
              </div>
              <div style={{ display: 'flex', gap: '12px' }}>
                <button type="button" onClick={() => setEditingProject(null)} className="btn-ghost" style={{ flex: 1, padding: '13px', fontSize: '15px' }}>Cancel</button>
                <button type="submit" className="btn-primary" style={{ flex: 1, padding: '13px', fontSize: '15px' }}>Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Project Confirm */}
      {showDeleteConfirm && (
        <div className="modal-overlay" onClick={() => setShowDeleteConfirm(null)}>
          <div className="modal-card" style={{ maxWidth: '400px' }} onClick={(e) => e.stopPropagation()}>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '20px', fontWeight: 600, color: 'var(--color-conflict)', marginBottom: '12px' }}>Delete Project?</h2>
            <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', marginBottom: '24px', lineHeight: '22px' }}>
              This will permanently delete this project, all conversations, and all stored memories. This action cannot be undone.
            </p>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button onClick={() => setShowDeleteConfirm(null)} className="btn-ghost" style={{ flex: 1, padding: '12px', fontSize: '14px' }}>Cancel</button>
              <button onClick={() => handleDelete(showDeleteConfirm)} className="btn-danger" style={{ flex: 1, padding: '12px', fontSize: '14px', fontWeight: 600 }}>Delete Forever</button>
            </div>
          </div>
        </div>
      )}

      {/* Profile Settings Modal */}
      {showProfile && (
        <div className="modal-overlay" onClick={() => setShowProfile(false)}>
          <div className="modal-card" style={{ maxWidth: '440px' }} onClick={(e) => e.stopPropagation()}>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '24px' }}>Profile Settings</h2>

            {profileMsg && (
              <div style={{ marginBottom: '16px', padding: '10px 14px', borderRadius: '10px', fontSize: '13px', background: profileMsg.includes('failed') || profileMsg.includes('incorrect') ? 'rgba(232, 97, 123, 0.08)' : 'rgba(74, 222, 128, 0.08)', color: profileMsg.includes('failed') || profileMsg.includes('incorrect') ? 'var(--color-conflict)' : 'var(--color-healthy)', border: '1px solid rgba(79, 209, 197, 0.1)' }}>
                {profileMsg}
              </div>
            )}

            {/* Update Profile */}
            <form onSubmit={handleUpdateProfile} style={{ marginBottom: '24px' }}>
              <div style={{ marginBottom: '14px' }}>
                <label style={labelStyle}>Name</label>
                <input type="text" value={profileName} onChange={(e) => setProfileName(e.target.value)} required style={inputStyle} />
              </div>
              <div style={{ marginBottom: '18px' }}>
                <label style={labelStyle}>Email</label>
                <input type="email" value={profileEmail} onChange={(e) => setProfileEmail(e.target.value)} required style={inputStyle} />
              </div>
              <button type="submit" className="btn-primary" style={{ padding: '10px 20px', fontSize: '14px' }}>Update Profile</button>
            </form>

            <div className="divider" style={{ margin: '0 0 24px' }} />

            {/* Change Password */}
            <form onSubmit={handleChangePassword} style={{ marginBottom: '24px' }}>
              <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '16px', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '16px' }}>Change Password</h3>
              <div style={{ marginBottom: '14px' }}>
                <label style={labelStyle}>Current Password</label>
                <input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} required style={inputStyle} />
              </div>
              <div style={{ marginBottom: '18px' }}>
                <label style={labelStyle}>New Password</label>
                <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required minLength={8} style={inputStyle} />
              </div>
              <button type="submit" className="btn-primary" style={{ padding: '10px 20px', fontSize: '14px' }}>Change Password</button>
            </form>

            <div className="divider" style={{ margin: '0 0 24px' }} />

            {/* Danger Zone */}
            <div>
              <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '16px', fontWeight: 600, color: 'var(--color-conflict)', marginBottom: '8px' }}>Danger Zone</h3>
              <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', marginBottom: '16px', lineHeight: '20px' }}>
                Permanently delete your account and all projects. This cannot be undone.
              </p>
              {!showDeleteAccount ? (
                <button onClick={() => setShowDeleteAccount(true)} className="btn-danger" style={{ padding: '10px 20px', fontSize: '14px' }}>Delete Account</button>
              ) : (
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                  <span style={{ fontSize: '13px', color: 'var(--color-conflict)', fontWeight: 500 }}>Are you sure?</span>
                  <button onClick={handleDeleteAccount} className="btn-danger" style={{ padding: '8px 16px', fontSize: '13px', fontWeight: 600 }}>Yes, Delete</button>
                  <button onClick={() => setShowDeleteAccount(false)} className="btn-ghost" style={{ padding: '8px 16px', fontSize: '13px' }}>Cancel</button>
                </div>
              )}
            </div>

            <div style={{ marginTop: '24px' }}>
              <button onClick={() => setShowProfile(false)} className="btn-ghost" style={{ width: '100%', padding: '12px', fontSize: '14px' }}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
