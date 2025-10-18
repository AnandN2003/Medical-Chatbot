import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import LandingPage from './components/LandingPage';
import MainPage from './components/MainPage';
import ChatPage from './components/ChatPage';
import DocumentUpload from './components/DocumentUpload_GOTHIC';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/" />;
};

function App() {
  return (
    <Router>
      <div className="App">
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/main" element={<MainPage />} />
            {/* Free chat - no authentication required, uses medical_book.pdf */}
            <Route path="/chat" element={<ChatPage />} />
            {/* Documents page - requires authentication */}
            <Route 
              path="/documents" 
              element={
                <ProtectedRoute>
                  <DocumentUpload />
                </ProtectedRoute>
              } 
            />
            {/* Authenticated chat - requires login, uses user's documents */}
            <Route 
              path="/my-chat" 
              element={
                <ProtectedRoute>
                  <ChatPage isAuthenticated={true} />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </AnimatePresence>
      </div>
    </Router>
  );
}

export default App;
