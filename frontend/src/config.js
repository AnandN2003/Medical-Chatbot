// API Configuration
// Centralized API URL management

// Hardcoded for production deployment - change this when backend URL changes
const API_URL = "https://medical-chatbot-backend-wzll.onrender.com";
// For local development, use: const API_URL = "http://localhost:8000";

export const config = {
  apiUrl: API_URL,
  endpoints: {
    // Auth endpoints
    login: `${API_URL}/api/v1/auth/login`,
    signup: `${API_URL}/api/v1/auth/signup`,
    
    // Chat endpoints
    chat: `${API_URL}/api/v1/chat/query`,
    loadData: `${API_URL}/api/v1/chat/load-data`,
    checkDocuments: `${API_URL}/api/v1/chat/check-user-documents`,
    
    // Document endpoints
    uploadDocuments: `${API_URL}/api/v1/documents/upload`,
    getDocuments: `${API_URL}/api/v1/documents/`,
    checkExisting: `${API_URL}/api/v1/documents/check-existing`,
    deleteDocument: (id) => `${API_URL}/api/v1/documents/${id}`,
    
    // Health endpoint
    health: `${API_URL}/api/v1/health`,
  },
};

export default config;
