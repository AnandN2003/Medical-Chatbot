import { motion } from 'framer-motion';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthModal from './AuthModal';
import './MainPage.css';

const MainPage = () => {
  const navigate = useNavigate();
  const [isRotating, setIsRotating] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  const handleChatbotClick = () => {
    setIsRotating(true);
    setTimeout(() => setIsRotating(false), 800);
  };

  const handleTryForFree = () => {
    // Navigate directly to chat without authentication
    navigate('/chat');
  };

  const openAuthModal = () => {
    setIsAuthModalOpen(true);
  };

  const closeAuthModal = () => {
    setIsAuthModalOpen(false);
  };

  return (
    <div className="main-container">
      {/* Background Gradient Effect */}
      <div className="bg-gradient" />
      
      {/* Animated Grid Background */}
      <div className="grid-background" />

      <motion.div
        className="main-content"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        {/* Header */}
        <motion.header
          className="header"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <div className="logo">
            <svg viewBox="0 0 40 40" className="logo-svg">
              <circle cx="20" cy="20" r="18" stroke="#00d4ff" strokeWidth="2" fill="none" />
              <path
                d="M 20 8 L 20 20 M 12 20 L 28 20"
                stroke="#00d4ff"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
            </svg>
            <span>MediChat</span>
          </div>
          <nav className="nav">
            <a href="#features">Features</a>
            <a href="#about">About</a>
            <a href="#contact">Contact</a>
          </nav>
        </motion.header>

        {/* Main Section */}
        <div className="hero-section">
          {/* Left Side - Content */}
          <motion.div
            className="hero-content"
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <motion.h1
              className="hero-title"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
            >
              Your AI-Powered
              <br />
              <span className="highlight">Health Companion</span>
            </motion.h1>
            
            <motion.p
              className="hero-description"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
            >
              Get instant medical insights, symptom analysis, and health guidance powered by advanced AI technology. Available 24/7 to support your health journey.
            </motion.p>

            <motion.div
              className="cta-buttons"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 1 }}
            >
              <motion.button
                className="btn btn-primary"
                onClick={handleTryForFree}
                whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(0, 212, 255, 0.6)" }}
                whileTap={{ scale: 0.95 }}
              >
                <span>Try it out for free</span>
                <svg viewBox="0 0 24 24" className="btn-icon">
                  <path
                    fill="currentColor"
                    d="M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z"
                  />
                </svg>
              </motion.button>

              <motion.button
                className="btn btn-secondary"
                onClick={openAuthModal}
                whileHover={{ scale: 1.05, borderColor: "#00d4ff" }}
                whileTap={{ scale: 0.95 }}
              >
                <span>Login / Signup</span>
                <svg viewBox="0 0 24 24" className="btn-icon">
                  <path
                    fill="currentColor"
                    d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z"
                  />
                </svg>
              </motion.button>
            </motion.div>

            {/* Features List */}
            <motion.div
              className="features-list"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2 }}
            >
              <div className="feature-item">
                <span className="feature-icon">⚡</span>
                <span>Instant AI Response</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🔒</span>
                <span>100% Private & Secure</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🌐</span>
                <span>Available 24/7</span>
              </div>
            </motion.div>
          </motion.div>

          {/* Right Side - Chatbot Image */}
          <motion.div
            className="hero-image"
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <motion.div
              className="chatbot-container"
              animate={{
                y: [0, -20, 0],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              <motion.div
                className="chatbot-image clickable"
                onClick={handleChatbotClick}
                animate={isRotating ? { rotateY: 360 } : { rotateY: 0 }}
                transition={{ duration: 0.8 }}
              >
                {/* Chatbot SVG Illustration */}
                <svg viewBox="0 0 200 200" className="chatbot-svg">
                  {/* Glow Effect */}
                  <defs>
                    <radialGradient id="glow" cx="50%" cy="50%">
                      <stop offset="0%" stopColor="#00d4ff" stopOpacity="0.8" />
                      <stop offset="100%" stopColor="#0099ff" stopOpacity="0" />
                    </radialGradient>
                    <filter id="shadow">
                      <feDropShadow dx="0" dy="4" stdDeviation="8" floodColor="#00d4ff" floodOpacity="0.5"/>
                    </filter>
                  </defs>
                  
                  {/* Background Glow */}
                  <circle cx="100" cy="100" r="80" fill="url(#glow)" opacity="0.3" />
                  
                  {/* Robot Head */}
                  <rect x="60" y="60" width="80" height="70" rx="10" fill="#0a1929" stroke="#00d4ff" strokeWidth="3" filter="url(#shadow)" />
                  
                  {/* Antenna */}
                  <line x1="100" y1="60" x2="100" y2="40" stroke="#00d4ff" strokeWidth="3" strokeLinecap="round" />
                  <circle cx="100" cy="35" r="5" fill="#00d4ff">
                    <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite" />
                  </circle>
                  
                  {/* Eyes */}
                  <circle cx="80" cy="85" r="8" fill="#00d4ff">
                    <animate attributeName="opacity" values="1;0.2;1" dur="3s" repeatCount="indefinite" />
                  </circle>
                  <circle cx="120" cy="85" r="8" fill="#00d4ff">
                    <animate attributeName="opacity" values="1;0.2;1" dur="3s" repeatCount="indefinite" />
                  </circle>
                  
                  {/* Medical Cross */}
                  <g transform="translate(100, 110)">
                    <rect x="-3" y="-12" width="6" height="24" fill="#00d4ff" rx="2" />
                    <rect x="-12" y="-3" width="24" height="6" fill="#00d4ff" rx="2" />
                  </g>
                  
                  {/* Chat Bubbles */}
                  <circle cx="40" cy="70" r="8" fill="#00d4ff" opacity="0.6">
                    <animate attributeName="cy" values="70;60;70" dur="2s" repeatCount="indefinite" />
                  </circle>
                  <circle cx="160" cy="90" r="6" fill="#0099ff" opacity="0.6">
                    <animate attributeName="cy" values="90;80;90" dur="2.5s" repeatCount="indefinite" />
                  </circle>
                  <circle cx="30" cy="110" r="5" fill="#7dd3fc" opacity="0.6">
                    <animate attributeName="cy" values="110;100;110" dur="3s" repeatCount="indefinite" />
                  </circle>
                </svg>

                {/* Rotating Ring */}
                <motion.div
                  className="rotating-ring"
                  animate={{ rotate: 360 }}
                  transition={{
                    duration: 20,
                    repeat: Infinity,
                    ease: "linear"
                  }}
                />
              </motion.div>

              {/* Floating Info Cards */}
              <motion.div
                className="info-card card-1"
                animate={{
                  y: [0, -10, 0],
                  opacity: [0.8, 1, 0.8]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <div className="card-icon">💊</div>
                <span>Medicine Info</span>
              </motion.div>

              <motion.div
                className="info-card card-2"
                animate={{
                  y: [0, -10, 0],
                  opacity: [0.8, 1, 0.8]
                }}
                transition={{
                  duration: 2.5,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 0.5
                }}
              >
                <div className="card-icon">🩺</div>
                <span>Symptom Check</span>
              </motion.div>

              <motion.div
                className="info-card card-3"
                animate={{
                  y: [0, -10, 0],
                  opacity: [0.8, 1, 0.8]
                }}
                transition={{
                  duration: 2.2,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 1
                }}
              >
                <div className="card-icon">📊</div>
                <span>Health Reports</span>
              </motion.div>
            </motion.div>
          </motion.div>
        </div>
      </motion.div>

      {/* Auth Modal */}
      <AuthModal isOpen={isAuthModalOpen} onClose={closeAuthModal} />
    </div>
  );
};

export default MainPage;
