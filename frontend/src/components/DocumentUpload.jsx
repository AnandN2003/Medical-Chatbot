import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import './DocumentUpload.css';

const DocumentUpload = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);
  const canvasRef = useRef(null);
  const MAX_FILES = 4;

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (!token || !userData) {
      navigate('/');
      return;
    }
    
    setUser(JSON.parse(userData));
    fetchDocuments();
    fetchStats();
  }, [navigate]);

  const fetchDocuments = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/documents/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      } else {
        console.error('Failed to fetch documents');
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/documents/stats/summary', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      if (!title) {
        setTitle(file.name);
      }
      setError('');
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('title', title);
      formData.append('category', category);
      formData.append('tags', tags);

      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/documents/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Upload successful:', data);
        
        // Reset form
        setSelectedFile(null);
        setTitle('');
        setCategory('');
        setTags('');
        document.getElementById('file-input').value = '';
        
        // Refresh documents list
        fetchDocuments();
        fetchStats();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setError('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/documents/${documentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        fetchDocuments();
        fetchStats();
      } else {
        console.error('Failed to delete document');
      }
    } catch (error) {
      console.error('Error deleting document:', error);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getStatusBadge = (status) => {
    const badges = {
      completed: { class: 'status-completed', text: 'Processed' },
      pending: { class: 'status-pending', text: 'Pending' },
      processing: { class: 'status-processing', text: 'Processing' },
      failed: { class: 'status-failed', text: 'Failed' }
    };
    return badges[status] || badges.pending;
  };

  const handleContinue = () => {
    navigate('/my-chat');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  return (
    <div className="document-upload-page">
      <nav className="upload-navbar">
        <div className="navbar-brand">
          <h2>🩺 Medical Chatbot</h2>
        </div>
        <div className="navbar-user">
          <span>Welcome, {user?.username}</span>
          <button onClick={handleLogout} className="btn-logout">Logout</button>
        </div>
      </nav>

      <div className="upload-container">
        <div className="upload-header">
          <h1>Upload Your Medical Resources</h1>
          <p>Upload medical textbooks, research papers, or documents to personalize your chatbot experience</p>
        </div>

        {/* Statistics Cards */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📚</div>
            <div className="stat-content">
              <div className="stat-value">{stats.total_documents}</div>
              <div className="stat-label">Total Documents</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <div className="stat-value">{stats.processed_count}</div>
              <div className="stat-label">Processed</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">⏳</div>
            <div className="stat-content">
              <div className="stat-value">{stats.pending_count + stats.processing_count}</div>
              <div className="stat-label">Processing</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">💾</div>
            <div className="stat-content">
              <div className="stat-value">{formatFileSize(stats.total_size)}</div>
              <div className="stat-label">Total Size</div>
            </div>
          </div>
        </div>

        {/* Upload Form */}
        <div className="upload-section">
          <form onSubmit={handleUpload} className="upload-form">
            <div className="file-input-wrapper">
              <input
                type="file"
                id="file-input"
                accept=".pdf,.docx,.doc,.xlsx,.xls,.txt"
                onChange={handleFileSelect}
                disabled={uploading}
              />
              <label htmlFor="file-input" className="file-input-label">
                <span className="file-icon">📎</span>
                <span>{selectedFile ? selectedFile.name : 'Choose a file...'}</span>
              </label>
            </div>

            {selectedFile && (
              <div className="upload-details">
                <div className="form-group">
                  <label>Document Title</label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Enter document title"
                    disabled={uploading}
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Category</label>
                    <select
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      disabled={uploading}
                    >
                      <option value="">Select category</option>
                      <option value="Anatomy">Anatomy</option>
                      <option value="Cardiology">Cardiology</option>
                      <option value="Neurology">Neurology</option>
                      <option value="Pharmacology">Pharmacology</option>
                      <option value="Surgery">Surgery</option>
                      <option value="Research">Research Paper</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Tags (comma-separated)</label>
                    <input
                      type="text"
                      value={tags}
                      onChange={(e) => setTags(e.target.value)}
                      placeholder="e.g., cardiology, heart, textbook"
                      disabled={uploading}
                    />
                  </div>
                </div>

                <button 
                  type="submit" 
                  className="btn-upload"
                  disabled={uploading}
                >
                  {uploading ? 'Uploading...' : 'Upload Document'}
                </button>
              </div>
            )}

            {error && <div className="error-message">{error}</div>}
          </form>
        </div>

        {/* Documents List */}
        <div className="documents-section">
          <div className="section-header">
            <h2>Your Documents</h2>
            {documents.length > 0 && (
              <button onClick={handleContinue} className="btn-continue">
                Continue to Chat →
              </button>
            )}
          </div>

          {documents.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <p>No documents uploaded yet</p>
              <small>Upload your first medical document to get started</small>
            </div>
          ) : (
            <div className="documents-grid">
              {documents.map((doc) => (
                <div key={doc._id} className="document-card">
                  <div className="document-icon">
                    {doc.file_type === 'pdf' && '📕'}
                    {doc.file_type === 'docx' && '📘'}
                    {doc.file_type === 'xlsx' && '📊'}
                    {doc.file_type === 'txt' && '📝'}
                  </div>
                  <div className="document-info">
                    <h3>{doc.metadata?.title || doc.original_filename}</h3>
                    <div className="document-meta">
                      <span>{formatFileSize(doc.file_size)}</span>
                      <span>•</span>
                      <span>{new Date(doc.upload_date).toLocaleDateString()}</span>
                    </div>
                    {doc.metadata?.category && (
                      <div className="document-category">{doc.metadata.category}</div>
                    )}
                    <div className={`document-status ${getStatusBadge(doc.processing_status).class}`}>
                      {getStatusBadge(doc.processing_status).text}
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(doc._id)}
                    className="btn-delete"
                    title="Delete document"
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentUpload;
