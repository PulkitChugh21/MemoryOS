/**
 * MemoryOS — Files Page (Phase 2)
 * File management with drag-and-drop upload, file list, and version history.
 * Follows the Synaptic Recall design system.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectsApi, filesApi } from '../api/client';

interface FileItem {
  id: string;
  project_id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  version: number;
  chunk_count: number;
  is_current: boolean;
  diff_summary: string | null;
  uploaded_at: string;
}

interface UploadResult {
  file: FileItem;
  facts_extracted: number;
  chunks_embedded: number;
  is_new_version: boolean;
  diff_summary: string | null;
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  });
}

function getFileIcon(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase() || '';
  const icons: Record<string, string> = {
    py: '🐍', js: '⚡', ts: '💠', tsx: '⚛️', jsx: '⚛️',
    json: '📋', md: '📄', txt: '📝', csv: '📊', html: '🌐',
    css: '🎨', sql: '🗄️', yaml: '⚙️', yml: '⚙️', toml: '⚙️',
    go: '🔵', java: '☕', rs: '🦀', c: '©️', cpp: '➕',
    sh: '🖥️', xml: '📰', env: '🔒',
  };
  return icons[ext] || '📁';
}

export default function FilesPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<any>(null);
  const [files, setFiles] = useState<FileItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState('');
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (projectId) { loadProject(); loadFiles(); }
  }, [projectId]);

  const loadProject = async () => {
    try { const { data } = await projectsApi.get(projectId!); setProject(data); }
    catch { navigate('/projects'); }
  };

  const loadFiles = async () => {
    setIsLoading(true);
    try {
      const { data } = await filesApi.list(projectId!);
      setFiles(data.files || []);
    } catch (e: any) {
      setError('Failed to load files');
    }
    setIsLoading(false);
  };

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    setUploadProgress(`Uploading ${file.name}...`);
    setUploadResult(null);
    setError('');

    try {
      const { data } = await filesApi.upload(projectId!, file);
      setUploadResult(data);
      setUploadProgress('');
      loadFiles();
    } catch (e: any) {
      const msg = e.response?.data?.error?.message || 'Upload failed';
      setError(msg);
      setUploadProgress('');
    }
    setIsUploading(false);
  };

  const handleDelete = async (fileId: string) => {
    try {
      await filesApi.delete(projectId!, fileId);
      setDeleteConfirm(null);
      loadFiles();
    } catch {
      setError('Failed to delete file');
    }
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  }, [projectId]);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback(() => setIsDragging(false), []);

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
            <span style={{ fontSize: '20px' }}>📁</span>
            <span style={{ fontFamily: 'var(--font-display)', fontSize: '18px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
              {project?.name || 'Loading...'} — Files
            </span>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button onClick={() => navigate(`/timeline/${projectId}`)} className="btn-ghost"
            style={{ padding: '8px 14px', fontSize: '13px' }}>📅 Timeline</button>
          <button onClick={() => navigate(`/chat/${projectId}`)} className="btn-ghost"
            style={{ padding: '8px 14px', fontSize: '13px' }}>💬 Chat</button>
        </div>
      </header>

      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '32px 24px' }}>
        {/* Upload Zone */}
        <div
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onClick={() => !isUploading && fileInputRef.current?.click()}
          className="upload-zone"
          style={{
            border: `2px dashed ${isDragging ? 'var(--color-recall)' : 'rgba(79, 209, 197, 0.15)'}`,
            borderRadius: '16px',
            padding: '40px',
            textAlign: 'center',
            cursor: isUploading ? 'wait' : 'pointer',
            background: isDragging ? 'rgba(79, 209, 197, 0.04)' : 'var(--color-surface)',
            transition: 'all 0.3s ease',
            marginBottom: '28px',
            animation: isDragging ? 'border-pulse 1.5s ease-in-out infinite' : 'none',
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            style={{ display: 'none' }}
            onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
          />
          {isUploading ? (
            <>
              <div style={{ fontSize: '36px', marginBottom: '12px' }}>⏳</div>
              <div style={{ fontSize: '15px', color: 'var(--color-recall)', fontWeight: 500 }}>{uploadProgress}</div>
              <div className="loading-dots" style={{ marginTop: '8px' }}><span /><span /><span /></div>
            </>
          ) : (
            <>
              <div style={{ fontSize: '36px', marginBottom: '12px' }}>{isDragging ? '📥' : '📤'}</div>
              <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '6px' }}>
                {isDragging ? 'Drop file here' : 'Drag & drop or click to upload'}
              </div>
              <div style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>
                Text and code files up to 10MB. Re-uploading the same filename creates a new version.
              </div>
            </>
          )}
        </div>

        {/* Upload Result */}
        {uploadResult && (
          <div style={{
            padding: '16px 20px', borderRadius: '12px', marginBottom: '20px',
            background: 'rgba(79, 209, 197, 0.06)', border: '1px solid rgba(79, 209, 197, 0.15)',
            animation: 'slide-up 0.3s ease-out',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <div className="pulse pulse--healthy" />
              <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--color-healthy)' }}>
                {uploadResult.is_new_version ? 'File Updated' : 'File Uploaded'} — {uploadResult.file.filename}
              </span>
            </div>
            <div style={{ fontSize: '13px', color: 'var(--color-text-muted)', display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
              <span>📦 {uploadResult.chunks_embedded} chunks embedded</span>
              <span>🧠 {uploadResult.facts_extracted} facts extracted</span>
              {uploadResult.is_new_version && <span>📋 v{uploadResult.file.version}</span>}
            </div>
            {uploadResult.diff_summary && (
              <div style={{ fontSize: '13px', color: 'var(--color-text-muted)', marginTop: '8px', fontStyle: 'italic' }}>
                {uploadResult.diff_summary}
              </div>
            )}
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{
            padding: '12px 18px', borderRadius: '12px', marginBottom: '20px',
            background: 'rgba(232, 97, 123, 0.06)', border: '1px solid rgba(232, 97, 123, 0.15)',
            color: 'var(--color-conflict)', fontSize: '13px',
          }}>
            ⚠️ {error}
            <button onClick={() => setError('')} style={{ marginLeft: '12px', background: 'none', border: 'none', color: 'var(--color-conflict)', cursor: 'pointer', fontWeight: 600 }}>✕</button>
          </div>
        )}

        {/* File List */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '16px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
            Project Files ({files.length})
          </h2>
        </div>

        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div className="loading-dots"><span /><span /><span /></div>
          </div>
        ) : files.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--color-text-muted)' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📂</div>
            <div style={{ fontSize: '16px', fontWeight: 500, marginBottom: '8px' }}>No files yet</div>
            <div style={{ fontSize: '13px' }}>Upload files to add them to your project's memory</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {files.map((file) => (
              <div
                key={file.id}
                className="glass-card"
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '14px 18px', borderRadius: '12px',
                  background: 'var(--color-surface)', border: '1px solid rgba(79, 209, 197, 0.06)',
                  transition: 'border-color 0.2s ease',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0 }}>
                  <span style={{ fontSize: '22px', flexShrink: 0 }}>{getFileIcon(file.filename)}</span>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--color-text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {file.filename}
                    </div>
                    <div style={{ display: 'flex', gap: '12px', fontSize: '12px', color: 'var(--color-text-muted)', marginTop: '3px' }}>
                      <span>{formatBytes(file.size_bytes)}</span>
                      <span>{file.chunk_count} chunks</span>
                      <span>v{file.version}</span>
                      <span>{formatDate(file.uploaded_at)}</span>
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexShrink: 0 }}>
                  {file.version > 1 && (
                    <span style={{
                      padding: '2px 8px', borderRadius: '6px', fontSize: '11px', fontWeight: 600,
                      background: 'rgba(139, 92, 246, 0.1)', color: 'var(--color-purple)',
                    }}>
                      v{file.version}
                    </span>
                  )}
                  {deleteConfirm === file.id ? (
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <button onClick={() => handleDelete(file.id)} className="btn-ghost"
                        style={{ padding: '4px 10px', fontSize: '12px', color: 'var(--color-conflict)' }}>Delete</button>
                      <button onClick={() => setDeleteConfirm(null)} className="btn-ghost"
                        style={{ padding: '4px 10px', fontSize: '12px' }}>Cancel</button>
                    </div>
                  ) : (
                    <button onClick={() => setDeleteConfirm(file.id)} className="btn-ghost"
                      style={{ padding: '4px 8px', fontSize: '14px', opacity: 0.5 }}>🗑️</button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
