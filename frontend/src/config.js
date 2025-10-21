// API Configuration
// Centralized API URL management

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
    health: `${API_URL}/health`,
  },
};

export default config;
