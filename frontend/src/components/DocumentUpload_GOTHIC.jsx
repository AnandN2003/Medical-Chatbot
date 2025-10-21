import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import './DocumentUpload_GOTHIC.css';

const DocumentUpload = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [existingDocuments, setExistingDocuments] = useState(null);
  const [checkingDocuments, setCheckingDocuments] = useState(true);
  const fileInputRef = useRef(null);
  const canvasRef = useRef(null);
  const uploadButtonRef = useRef(null);
  const uploadZoneRef = useRef(null);
  const MAX_FILES = 4;

  useEffect(() => {
    console.log('🚀 DocumentUpload component mounted');
    console.log('🚀 FileInputRef:', fileInputRef);
    
    // Check authentication
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    console.log('🔐 Auth check:', { hasToken: !!token, hasUserData: !!userData });
    
    if (!token || !userData) {
      console.warn('⚠️ No auth, redirecting to home');
      navigate('/');
      return;
    }
    
    try {
      const parsedUser = JSON.parse(userData);
      console.log('👤 User logged in:', parsedUser);
      setUser(parsedUser);
      
      // Validate token format
      if (!token || token === 'null' || token === 'undefined') {
        console.error('❌ Invalid token, redirecting to login');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/');
        return;
      }
      
      // Check for existing documents
      checkExistingDocuments(token);
    } catch (error) {
      console.error('❌ Error parsing user data:', error);
      navigate('/');
    }

    // Initialize animated background
    console.log('🎨 Initializing canvas...');
    initializeCanvas();
    
    // Check upload button after a delay
    setTimeout(() => {
      console.log('🔍 Upload button ref:', uploadButtonRef.current);
      if (uploadButtonRef.current && uploadZoneRef.current) {
        console.log('✅ Upload button EXISTS in DOM');
        
        // Position the global button over the upload zone
        const updateButtonPosition = () => {
          if (!uploadZoneRef.current || !uploadButtonRef.current) {
            return; // Exit if refs aren't ready
          }
          const zoneRect = uploadZoneRef.current.getBoundingClientRect();
          if (uploadButtonRef.current) {
            uploadButtonRef.current.style.top = `${zoneRect.top}px`;
            uploadButtonRef.current.style.left = `${zoneRect.left}px`;
            uploadButtonRef.current.style.width = `${zoneRect.width}px`;
            uploadButtonRef.current.style.height = `${zoneRect.height}px`;
          }
        };
        
        updateButtonPosition();
        
        // Update on scroll and resize
        window.addEventListener('scroll', updateButtonPosition);
        window.addEventListener('resize', updateButtonPosition);
        
        return () => {
          window.removeEventListener('scroll', updateButtonPosition);
          window.removeEventListener('resize', updateButtonPosition);
        };
      } else {
        console.error('❌ Upload button or zone ref is NULL!');
      }
    }, 1000);
  }, [navigate]);

  const initializeCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) {
      console.error('❌ Canvas ref is null!');
      return;
    }

    console.log('✅ Canvas found, initializing particles...');
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = [];
    const particleCount = 80;

    // Create particles
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 3 + 1,
        speedX: Math.random() * 0.5 - 0.25,
        speedY: Math.random() * 0.5 - 0.25,
        opacity: Math.random() * 0.5 + 0.3
      });
    }

    console.log(`✅ Created ${particleCount} particles`);

    function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach(particle => {
        particle.x += particle.speedX;
        particle.y += particle.speedY;

        if (particle.x < 0 || particle.x > canvas.width) particle.speedX *= -1;
        if (particle.y < 0 || particle.y > canvas.height) particle.speedY *= -1;

        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0, 212, 255, ${particle.opacity})`;
        ctx.fill();
      });

      requestAnimationFrame(animate);
    }

    animate();

    // Resize handler
    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    return () => window.removeEventListener('resize', handleResize);
  };

  const checkExistingDocuments = async (token) => {
    setCheckingDocuments(true);
    console.log('🔍 Checking for existing documents...');
    console.log('🔑 Using token:', token ? 'Token exists' : 'No token');
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/documents/check-existing', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      console.log('📡 Response status:', response.status);
      console.log('📡 Response ok:', response.ok);

      if (response.ok) {
        const data = await response.json();
        console.log('📚 Existing documents check SUCCESS:', data);
        setExistingDocuments(data);
      } else {
        const errorData = await response.json();
        console.error('❌ Failed to check existing documents:', response.status, errorData);
        setExistingDocuments({ has_existing_documents: false, document_count: 0, documents: [] });
      }
    } catch (error) {
      console.error('❌ Error checking existing documents:', error);
      setExistingDocuments({ has_existing_documents: false, document_count: 0, documents: [] });
    } finally {
      setCheckingDocuments(false);
      console.log('✅ Check complete. Existing documents state:', existingDocuments);
    }
  };

  const handleUseExistingDocuments = () => {
    console.log('📖 Using existing documents, navigating to chat...');
    navigate('/my-chat');
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    setError('');
    setSuccess('');

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  const handleBrowseClick = (e) => {
    console.log('🔵 BROWSE CLICK TRIGGERED!', {
      event: e,
      fileInput: fileInputRef.current,
      hasFileInput: !!fileInputRef.current
    });
    e.preventDefault();
    e.stopPropagation();
    
    if (fileInputRef.current) {
      console.log('✅ Opening file picker...');
      fileInputRef.current.click();
    } else {
      console.error('❌ File input ref is null!');
    }
  };

  const handleUploadZoneMouseEnter = () => {
    console.log('🟢 Mouse ENTERED upload zone');
  };

  const handleUploadZoneMouseLeave = () => {
    console.log('🔴 Mouse LEFT upload zone');
  };

  const handleUploadZoneMouseMove = (e) => {
    console.log('🟡 Mouse MOVING over upload zone', { x: e.clientX, y: e.clientY });
  };

  const handleFiles = (files) => {
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'];
    const validFiles = files.filter(file => validTypes.includes(file.type));

    if (validFiles.length === 0) {
      setError('Please upload valid medical documents (PDF, DOC, DOCX, XLS, XLSX)');
      return;
    }

    const totalFiles = selectedFiles.length + validFiles.length;
    if (totalFiles > MAX_FILES) {
      setError(`You can only upload up to ${MAX_FILES} files. Currently selected: ${selectedFiles.length}`);
      return;
    }

    setSelectedFiles(prev => [...prev, ...validFiles]);
    setError('');
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one file');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');

    try {
      const formData = new FormData();
      selectedFiles.forEach((file) => {
        formData.append('files', file);
      });

      const token = localStorage.getItem('token');
      console.log('🔑 Token from localStorage:', token ? 'EXISTS' : 'NULL');
      console.log('🔑 Token value:', token);
      
      const response = await fetch('http://localhost:8000/api/v1/documents/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      console.log('📡 Response status:', response.status);
      console.log('📡 Response ok:', response.ok);

      if (response.ok) {
        const data = await response.json();
        setSuccess(`Successfully uploaded ${selectedFiles.length} file(s)!`);
        setTimeout(() => {
          navigate('/my-chat');
        }, 1500);
      } else {
        const errorData = await response.json();
        console.error('❌ Error response:', errorData);
        
        // Handle validation errors from FastAPI
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            // FastAPI validation errors are arrays of objects
            const errorMessages = errorData.detail.map(err => err.msg || JSON.stringify(err)).join(', ');
            setError(errorMessages);
          } else if (typeof errorData.detail === 'string') {
            setError(errorData.detail);
          } else {
            setError('Upload failed: ' + JSON.stringify(errorData.detail));
          }
        } else {
          setError('Upload failed. Please try again.');
        }
      }
    } catch (error) {
      console.error('Upload error:', error);
      setError('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  return (
    <div className="documents-page">
      {/* Particle Canvas Background */}
      <canvas ref={canvasRef} className="particle-canvas"></canvas>

      {/* GLOBAL UPLOAD TRIGGER - OUTSIDE ALL CONTAINERS */}
      <div
        ref={uploadButtonRef}
        onClick={(e) => {
          console.log('🔥 Upload zone clicked!');
          e.preventDefault();
          e.stopPropagation();
          if (fileInputRef.current) {
            fileInputRef.current.click();
          }
        }}
        className="invisible-upload-button"
        aria-label="Click to upload files"
      />

      {/* Floating Medical Organs - Spooky */}
      <div className="floating-organs">
        <div className="organ organ-1">💀</div>
        <div className="organ organ-2">🫀</div>
        <div className="organ organ-3">🧠</div>
        <div className="organ organ-4">🫁</div>
        <div className="organ organ-5">🦴</div>
        <div className="organ organ-6">💀</div>
        <div className="organ organ-7">🫀</div>
        <div className="organ organ-8">🧠</div>
      </div>

      {/* Header */}
      <header className="documents-header">
        <div className="header-content">
          <h1 className="brand-logo">Medical Chatbot</h1>
          <div className="user-info">
            <span className="user-name">👤 {user?.username || 'User'}</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div className="documents-container">
        <motion.div 
          className="medical-bible-section"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          {/* Title Above Book */}
          <div className="bible-header">
            <motion.h2 
              className="bible-main-title"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3, duration: 0.6 }}
            >
              The Medical Bible
            </motion.h2>
            <motion.p 
              className="bible-subtitle-text"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5, duration: 0.6 }}
            >
              Ancient Wisdom • Modern Medicine
            </motion.p>
          </div>

          {/* Existing Documents Notification */}
          {checkingDocuments && (
            <motion.div
              className="existing-docs-banner"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.5 }}
            >
              <div className="banner-content" style={{ textAlign: 'center' }}>
                <span className="spinner" style={{ display: 'inline-block' }}></span>
                <span style={{ marginLeft: '1rem' }}>Checking for existing documents...</span>
              </div>
            </motion.div>
          )}
          
          {!checkingDocuments && existingDocuments?.has_existing_documents && (
            <motion.div
              className="existing-docs-banner"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.5 }}
            >
              <div className="banner-content">
                <div className="banner-icon">📚</div>
                <div className="banner-text">
                  <h3>Knowledge Base Found</h3>
                  <p>You have {existingDocuments.document_count} processed document{existingDocuments.document_count > 1 ? 's' : ''} ready to use</p>
                  <div className="doc-list-compact">
                    {existingDocuments.documents.slice(0, 3).map((doc, index) => (
                      <span key={index} className="doc-badge">
                        📄 {doc.filename}
                      </span>
                    ))}
                    {existingDocuments.document_count > 3 && (
                      <span className="doc-badge">+{existingDocuments.document_count - 3} more</span>
                    )}
                  </div>
                </div>
                <button
                  className="use-existing-btn"
                  onClick={handleUseExistingDocuments}
                >
                  Use Existing Documents →
                </button>
              </div>
            </motion.div>
          )}
          
          {!checkingDocuments && existingDocuments && !existingDocuments.has_existing_documents && (
            <motion.div
              className="existing-docs-banner"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.5 }}
              style={{ marginBottom: '1rem' }}
            >
              <div className="banner-content" style={{ 
                background: 'linear-gradient(135deg, rgba(139, 139, 0, 0.15), rgba(0, 0, 0, 0.8))',
                borderColor: 'rgba(255, 215, 0, 0.3)'
              }}>
                <div className="banner-icon">📭</div>
                <div className="banner-text">
                  <h3 style={{ color: '#ffd700' }}>No Documents Yet</h3>
                  <p>Upload your first medical document to get started</p>
                </div>
              </div>
            </motion.div>
          )}

          {/* The Gothic Medical Book */}
          <motion.div 
            className="medical-bible"
            initial={{ opacity: 0, rotateY: -20 }}
            animate={{ opacity: 1, rotateY: 0 }}
            transition={{ delay: 0.4, duration: 1 }}
          >
            <div className="book-glow"></div>
            
            <div className="book-wrapper">
              {/* Book Spine */}
              <div className="book-spine">
                <div className="spine-text">MEDICAL BIBLE</div>
                <div className="spine-decoration">☠️</div>
              </div>

              {/* Open Book Pages */}
              <div className="book-pages">
                {/* Left Page - Decorative with Skull */}
                <div className="page left-page">
                  <div className="page-content">
                    <div className="skull-decoration">💀</div>
                    <div className="ornamental-border">
                      <p className="motivational-quote">
                        Own your pain, heal the world
                      </p>
                    </div>
                    <div className="page-text">
                      <p className="latin-text">Corpus Medicinae</p>
                      <div className="decorative-line"></div>
                      <p className="page-number">I</p>
                    </div>
                  </div>
                  <div className="page-shadow"></div>
                </div>

                {/* Right Page - Upload Zone */}
                <div className="page right-page">
                  <div className="page-content">
                    {/* Upload Zone Inside Book */}
                    <div
                      ref={uploadZoneRef}
                      className={`upload-zone-book ${dragActive ? 'drag-active' : ''}`}
                      onDragEnter={handleDrag}
                      onDragLeave={handleDrag}
                      onDragOver={handleDrag}
                      onDrop={handleDrop}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          handleBrowseClick(e);
                        }
                      }}
                    >
                      {/* Hidden File Input */}
                      <input
                        ref={fileInputRef}
                        type="file"
                        id="file-upload-input"
                        multiple
                        accept=".pdf,.doc,.docx,.xls,.xlsx"
                        onChange={handleFileInput}
                        style={{ display: 'none' }}
                      />
                      
                      <motion.div 
                        className="upload-icon-book"
                        animate={{ y: [0, -10, 0] }}
                        transition={{ repeat: Infinity, duration: 2 }}
                        style={{ pointerEvents: 'none' }}
                      >
                        📚
                      </motion.div>
                      <h3 className="upload-title-book">Drop Medical Texts</h3>
                      <p className="upload-subtitle-book">Up to 4 sacred documents</p>
                      <p className="upload-hint-book">PDF, DOC, DOCX, XLS, XLSX</p>
                      <p className="upload-browse">or click to browse</p>
                    </div>

                    {/* Selected Files List */}
                    {selectedFiles.length > 0 && (
                      <motion.div 
                        className="selected-files-book"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                      >
                        <h4 className="files-title-book">Selected Manuscripts ({selectedFiles.length}/{MAX_FILES})</h4>
                        <div className="files-list-book">
                          {selectedFiles.map((file, index) => (
                            <motion.div
                              key={index}
                              className="file-item-book"
                              initial={{ opacity: 0, x: -20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: index * 0.1 }}
                            >
                              <span className="file-icon-book">📄</span>
                              <div className="file-info-book">
                                <span className="file-name-book">{file.name}</span>
                                <span className="file-size-book">{formatFileSize(file.size)}</span>
                              </div>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  removeFile(index);
                                }}
                                className="remove-file-btn-book"
                              >
                                ✕
                              </button>
                            </motion.div>
                          ))}
                        </div>
                      </motion.div>
                    )}

                    <p className="page-number">II</p>
                  </div>
                  <div className="page-shadow"></div>
                </div>
              </div>

              {/* Book Shadow */}
              <div className="book-shadow-bottom"></div>
            </div>
          </motion.div>

          {/* Messages */}
          <AnimatePresence>
            {error && (
              <motion.div
                className="message error-message"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                {error}
              </motion.div>
            )}
            {success && (
              <motion.div
                className="message success-message"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                {success}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Upload Button */}
          {selectedFiles.length > 0 && (
            <motion.button
              className="upload-submit-btn"
              onClick={handleUpload}
              disabled={uploading}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {uploading ? (
                <>
                  <span className="spinner"></span>
                  Processing Ancient Texts...
                </>
              ) : (
                <>
                  📖 Add to Knowledge Base
                </>
              )}
            </motion.button>
          )}
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="documents-footer">
        <p>Add your medical documents to enhance the AI's knowledge</p>
      </footer>
    </div>
  );
};

export default DocumentUpload;
