import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import './ChatPage.css';
import { config } from '../config';

const ChatPage = ({ isAuthenticated = false }) => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDataLoaded, setIsDataLoaded] = useState(false);
  const [dataLoadStatus, setDataLoadStatus] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [chatSessions, setChatSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(Date.now());
  const [vectorCount, setVectorCount] = useState(0);
  const [user, setUser] = useState(null);

  // Check if backend is running and data is loaded
  useEffect(() => {
    if (isAuthenticated) {
      const userData = localStorage.getItem('user');
      if (userData) {
        setUser(JSON.parse(userData));
      }
      // For authenticated users, automatically check their documents
      // Don't show "Checking data status..." - do it silently
      checkUserDocuments();
    } else {
      checkBackendStatus();
    }
  }, [isAuthenticated]);

  const checkUserDocuments = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setDataLoadStatus('Please upload documents to get started');
        return;
      }

      const response = await fetch(config.endpoints.checkExisting, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.has_existing_documents) {
          setIsDataLoaded(true);
          setDataLoadStatus(`✅ ${data.document_count} document(s) ready`);
        } else {
          setIsDataLoaded(false);
          setDataLoadStatus('📤 Upload documents to start chatting');
        }
      } else {
        setDataLoadStatus('Upload documents to get started');
      }
    } catch (error) {
      console.error('Error checking documents:', error);
      setDataLoadStatus('Upload documents to get started');
    }
  };

  const checkBackendStatus = async () => {
    try {
      // Quick health check with timeout to avoid hanging
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
      
      const response = await fetch(config.endpoints.health, {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        // For free users, check if data is already loaded in vector store
        const loaded = data.status === 'healthy' && data.vector_count > 0;
        setIsDataLoaded(loaded);
        
        if (loaded) {
          setVectorCount(data.vector_count || 0);
          setDataLoadStatus(`✅ Ready! ${data.vector_count} vectors loaded`);
        } else {
          setDataLoadStatus('Backend connected - click Load Data to start');
        }
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Backend health check timed out - it may be initializing');
        setDataLoadStatus('⏱️ Backend is starting up... Click Load Data in a moment');
      } else {
        console.error('Backend not available:', error);
        setDataLoadStatus('❌ Backend not connected - please start the backend server');
      }
      setIsDataLoaded(false);
    }
  };

  const handleLoadData = async () => {
    if (isLoading) return; // Prevent multiple simultaneous loads
    
    setIsLoading(true);
    setDataLoadStatus('Checking data status...');
    
    try {
      if (isAuthenticated) {
        // For authenticated users, check if they have uploaded documents
        const token = localStorage.getItem('token');
        
        if (!token) {
          setDataLoadStatus('❌ Please login first');
          setIsDataLoaded(false);
          setIsLoading(false);
          return;
        }
        
        const checkResponse = await fetch(config.endpoints.checkExisting, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (checkResponse.ok) {
          const data = await checkResponse.json();
          
          if (data.has_existing_documents) {
            setIsDataLoaded(true);
            setDataLoadStatus(`✅ ${data.document_count} document(s) loaded and ready!`);
          } else {
            setIsDataLoaded(false);
            setDataLoadStatus('📤 Please upload your medical documents to get started');
          }
        } else {
          setDataLoadStatus('❌ Could not check documents. Please try again.');
          setIsDataLoaded(false);
        }
      } else {
        // For free/unauthenticated users, check the default Medical_book.pdf via health
        const healthResponse = await fetch(config.endpoints.health, {
          signal: AbortSignal.timeout(5000) // 5 second timeout
        });
        
        if (healthResponse.ok) {
          const healthData = await healthResponse.json();
          const vectorCount = healthData.vector_count || 0;
          
          if (vectorCount > 0) {
            // Data is already loaded
            setIsDataLoaded(true);
            setVectorCount(vectorCount);
            setDataLoadStatus(`✅ Medical_book.pdf loaded! (${vectorCount} vectors)`);
          } else {
            // No data in vector store - backend needs restart or data loading
            setIsDataLoaded(false);
            setDataLoadStatus('❌ No data found. Please restart the backend to load medical_book.pdf');
          }
        } else {
          setDataLoadStatus('❌ Backend not responding');
          setIsDataLoaded(false);
        }
      }
    } catch (error) {
      console.error('Error checking data status:', error);
      
      if (error.name === 'TimeoutError') {
        setDataLoadStatus('⏱️ Backend is initializing... Please wait and try again in a moment');
      } else {
        setDataLoadStatus('❌ Error connecting to backend: ' + error.message);
      }
      setIsDataLoaded(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuery = async (e) => {
    e.preventDefault();
    
    if (!query.trim() || !isDataLoaded) return;
    
    setIsLoading(true);
    
    // Add user message to chat history
    const userMessage = { type: 'user', text: query };
    const newHistory = [...chatHistory, userMessage];
    setChatHistory(newHistory);
    
    try {
      // Prepare headers
      const headers = {
        'Content-Type': 'application/json',
      };
      
      // Add authentication token if user is logged in
      if (isAuthenticated) {
        const token = localStorage.getItem('token');
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
      }
      
      const response = await fetch(config.endpoints.chat, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          question: query,
          top_k: 3,
          return_sources: true
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Add bot response to chat history
        const botMessage = { 
          type: 'bot', 
          text: data.answer,
          sources: data.sources 
        };
        const updatedHistory = [...newHistory, botMessage];
        setChatHistory(updatedHistory);
        setResponse(data.answer);
        
        // Update chat sessions with the first query as title
        if (newHistory.length === 1) {
          const newSession = {
            id: currentSessionId,
            title: query.substring(0, 50) + (query.length > 50 ? '...' : ''),
            timestamp: new Date().toISOString(),
            messages: updatedHistory
          };
          setChatSessions(prev => [newSession, ...prev]);
        } else {
          // Update existing session
          setChatSessions(prev => prev.map(session => 
            session.id === currentSessionId 
              ? { ...session, messages: updatedHistory }
              : session
          ));
        }
      } else {
        const errorMessage = { 
          type: 'bot', 
          text: '❌ Sorry, I encountered an error processing your query.' 
        };
        setChatHistory(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error querying chatbot:', error);
      const errorMessage = { 
        type: 'bot', 
        text: '❌ Error: Unable to connect to the backend.' 
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setQuery('');
    }
  };

  const startNewChat = () => {
    setChatHistory([]);
    setCurrentSessionId(Date.now());
  };

  const loadSession = (session) => {
    setChatHistory(session.messages);
    setCurrentSessionId(session.id);
  };

  const handleBackButton = () => {
    navigate('/main');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  return (
    <motion.div 
      className="chat-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Background with blur effect */}
      <div className="chat-background"></div>

      {/* Left Sidebar - Chat History */}
      <motion.div 
        className="chat-sidebar"
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <div className="sidebar-header">
          <h2>MediChat</h2>
          <button className="new-chat-btn" onClick={startNewChat}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            New Chat
          </button>
        </div>

        <div className="chat-sessions">
          {chatSessions.length === 0 ? (
            <p className="no-sessions">No chat history yet</p>
          ) : (
            chatSessions.map((session) => (
              <motion.div
                key={session.id}
                className={`session-item ${session.id === currentSessionId ? 'active' : ''}`}
                onClick={() => loadSession(session)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <p className="session-title">{session.title}</p>
                <span className="session-time">
                  {new Date(session.timestamp).toLocaleDateString()}
                </span>
              </motion.div>
            ))
          )}
        </div>

        <div className="sidebar-footer">
          <button className="back-button-sidebar" onClick={handleBackButton}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Back to Home
          </button>
          {isAuthenticated && user && (
            <div className="user-info-sidebar">
              <span>👤 {user.username}</span>
              <button className="logout-btn-sidebar" onClick={handleLogout}>Logout</button>
            </div>
          )}
        </div>
      </motion.div>

      {/* Main Chat Area */}
      <div className="chat-main">
        {/* Header */}
        <motion.div 
          className="chat-header-main"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="header-info">
            <h1>{isAuthenticated ? 'My Medical Assistant' : 'Medical Assistant'}</h1>
            <p className="header-subtitle">
              {isAuthenticated ? 'AI-powered insights from your documents' : 'AI-powered health insights from Medical_book.pdf'}
            </p>
          </div>

          {/* Data Source Indicator */}
          <div className="data-source-compact">
            {isAuthenticated ? (
              // Clickable badge for authenticated users
              <button 
                className="pdf-badge clickable"
                onClick={() => navigate('/upload')}
                title="View and manage your documents"
                style={{ cursor: 'pointer', background: 'transparent', border: 'none' }}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="#00d4ff" strokeWidth="2"/>
                  <polyline points="14 2 14 8 20 8" stroke="#00d4ff" strokeWidth="2"/>
                </svg>
                <span>Your Documents</span>
              </button>
            ) : (
              // Non-clickable badge for free users
              <div className="pdf-badge">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="#00d4ff" strokeWidth="2"/>
                  <polyline points="14 2 14 8 20 8" stroke="#00d4ff" strokeWidth="2"/>
                </svg>
                <span>Medical_book.pdf</span>
              </div>
            )}
            
            {/* Show controls for both authenticated and free users */}
            <div className="load-data-controls">
              {isAuthenticated ? (
                // Authenticated users - show refresh button
                <button 
                  className={`load-btn-compact ${isDataLoaded ? 'loaded' : ''}`}
                  onClick={handleLoadData}
                  disabled={isLoading}
                  title="Check document status"
                >
                  {isLoading ? (
                    <span className="spinner-small"></span>
                  ) : (
                    '🔄 Refresh'
                  )}
                </button>
              ) : (
                // Free users - show load data button
                <button 
                  className={`load-btn-compact ${isDataLoaded ? 'loaded' : ''}`}
                  onClick={handleLoadData}
                  disabled={isLoading || isDataLoaded}
                >
                  {isLoading ? (
                    <span className="spinner-small"></span>
                  ) : isDataLoaded ? (
                    '✓ Loaded'
                  ) : (
                    'Load Data'
                  )}
                </button>
              )}
              
              {dataLoadStatus && (
                <span className="status-text">{dataLoadStatus}</span>
              )}
            </div>
          </div>
        </motion.div>

        {/* Chat Messages Area */}
        <div className="chat-messages-container">
          {chatHistory.length === 0 ? (
            <motion.div 
              className="empty-state"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <div className="empty-icon">💬</div>
              <h3>Start a conversation</h3>
              <p>Ask me anything about medical conditions, treatments, and health</p>
              {!isAuthenticated && !isDataLoaded && (
                <p className="warning-text">⚠️ Please load data first to start chatting</p>
              )}
              {isAuthenticated && (
                <p className="info-text">💡 Your personalized medical assistant is ready!</p>
              )}
            </motion.div>
          ) : (
            <div className="chat-messages">
              <AnimatePresence>
                {chatHistory.map((message, index) => (
                  <motion.div
                    key={index}
                    className={`message ${message.type}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <div className="message-bubble">
                      <p className="message-text">{message.text}</p>
                      {message.sources && message.sources.length > 0 && (
                        <div className="sources-compact">
                          {message.sources.map((source, idx) => (
                            <span key={idx} className="source-badge">
                              Page {source.page || idx + 1}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              {isLoading && (
                <motion.div
                  className="message bot"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <div className="message-bubble typing">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          )}
        </div>

        {/* Input Area */}
        <motion.div 
          className="chat-input-area"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <form onSubmit={handleQuery} className="input-form">
            <input
              type="text"
              className="chat-input"
              placeholder={
                isAuthenticated 
                  ? "Type your medical question..." 
                  : isDataLoaded 
                    ? "Type your medical question..." 
                    : "Load data to start..."
              }
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={(!isDataLoaded && !isAuthenticated) || isLoading}
            />
            <button 
              type="submit" 
              className="send-button"
              disabled={(!isDataLoaded && !isAuthenticated) || isLoading || !query.trim()}
            >
              {isLoading ? (
                <span className="spinner-small"></span>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              )}
            </button>
          </form>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default ChatPage;
