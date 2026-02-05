/**
 * Complete API Service Layer for ACADEMIYA-Hub
 * 
 * USAGE:
 * import { authAPI, departementAPI, filiereAPI, moduleAPI, inscriptionAPI } from '@/services/api';
 * 
 * const data = await departementAPI.getAll();
 */

import axios from 'axios';

// ============================================
// BASE CONFIGURATION
// ============================================
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================
// REQUEST INTERCEPTOR - Auto-attach JWT Token
// ============================================
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ============================================
// RESPONSE INTERCEPTOR - Handle Token Refresh
// ============================================
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If token expired, try to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        const response = await axios.post(`${BASE_URL}/auth/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed - logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_role');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// ============================================
// AUTH API
// ============================================
export const authAPI = {
  /**
   * Login with email and password
   * @param {string} email
   * @param {string} password
   * @returns {Promise<{access: string, refresh: string, role: string, username: string}>}
   */
  login: async (email, password) => {
    const response = await axios.post(`${BASE_URL}/auth/login/`, { email, password });
    const { access, refresh, role, username } = response.data;
    
    // Store tokens
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user_role', role);
    localStorage.setItem('username', username);
    
    return response.data;
  },

  /**
   * Register new student account
   * @param {Object} userData - {username, email, password, first_name, last_name}
   */
  register: async (userData) => {
    const response = await axios.post(`${BASE_URL}/auth/register/`, userData);
    return response.data;
  },

  /**
   * Logout - clear tokens
   */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
  },

  /**
   * Get current user role
   */
  getCurrentRole: () => {
    return localStorage.getItem('user_role');
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
};

// ============================================
// DEPARTEMENT API
// ============================================
export const departementAPI = {
  /**
   * Get all departements
   */
  getAll: async () => {
    const response = await api.get('/departements/');
    return response.data;
  },

  /**
   * Get departement by ID
   */
  getById: async (id) => {
    const response = await api.get(`/departements/${id}/`);
    return response.data;
  },

  /**
   * Create new departement (ADMIN only)
   */
  create: async (data) => {
    const response = await api.post('/departements/', data);
    return response.data;
  },

  /**
   * Update departement (ADMIN only)
   */
  update: async (id, data) => {
    const response = await api.put(`/departements/${id}/`, data);
    return response.data;
  },

  /**
   * Delete departement (ADMIN only)
   */
  delete: async (id) => {
    const response = await api.delete(`/departements/${id}/`);
    return response.data;
  },
};

// ============================================
// FILIERE API
// ============================================
export const filiereAPI = {
  /**
   * Get all filieres
   * @param {Object} filters - {departement: id, niveau: string}
   */
  getAll: async (filters = {}) => {
    const response = await api.get('/filieres/', { params: filters });
    return response.data;
  },

  /**
   * Get filiere by ID
   */
  getById: async (id) => {
    const response = await api.get(`/filieres/${id}/`);
    return response.data;
  },

  /**
   * Create new filiere (ADMIN only)
   */
  create: async (data) => {
    const response = await api.post('/filieres/', data);
    return response.data;
  },

  /**
   * Update filiere (ADMIN only)
   */
  update: async (id, data) => {
    const response = await api.put(`/filieres/${id}/`, data);
    return response.data;
  },

  /**
   * Delete filiere (ADMIN only)
   */
  delete: async (id) => {
    const response = await api.delete(`/filieres/${id}/`);
    return response.data;
  },
};

// ============================================
// MODULE API
// ============================================
export const moduleAPI = {
  /**
   * Get all modules
   * @param {Object} filters - {filiere: id, semestre: number}
   */
  getAll: async (filters = {}) => {
    const response = await api.get('/modules/', { params: filters });
    return response.data;
  },

  /**
   * Get module by ID
   */
  getById: async (id) => {
    const response = await api.get(`/modules/${id}/`);
    return response.data;
  },

  /**
   * Create new module (ADMIN only)
   */
  create: async (data) => {
    const response = await api.post('/modules/', data);
    return response.data;
  },

  /**
   * Update module (ADMIN only)
   */
  update: async (id, data) => {
    const response = await api.put(`/modules/${id}/`, data);
    return response.data;
  },

  /**
   * Delete module (ADMIN only)
   */
  delete: async (id) => {
    const response = await api.delete(`/modules/${id}/`);
    return response.data;
  },
};

// ============================================
// INSCRIPTION API
// ============================================
export const inscriptionAPI = {
  /**
   * Get all inscriptions (ADMIN/DIRECTION only)
   */
  getAll: async () => {
    const response = await api.get('/inscriptions/');
    return response.data;
  },

  /**
   * Get inscription by ID
   */
  getById: async (id) => {
    const response = await api.get(`/inscriptions/${id}/`);
    return response.data;
  },

  /**
   * Create new inscription (STUDENT only)
   * @param {Object} data - {filiere: id, academic_year: string}
   */
  create: async (data) => {
    const response = await api.post('/inscriptions/', data);
    return response.data;
  },

  /**
   * Get current student's inscriptions
   * Endpoint: /inscriptions/my_inscriptions/
   */
  getMine: async () => {
    const response = await api.get('/inscriptions/my_inscriptions/');
    return response.data;
  },

  /**
   * Get pending inscriptions (ADMIN only)
   * Endpoint: /inscriptions/pending/
   */
  getPending: async () => {
    const response = await api.get('/inscriptions/pending/');
    return response.data;
  },

  /**
   * Validate or reject inscription (ADMIN only)
   * @param {number} id - Inscription ID
   * @param {string} status - 'VALIDATED' or 'REJECTED'
   * @param {string} rejection_reason - Required if status is REJECTED
   */
  validate: async (id, status, rejection_reason = '') => {
    const response = await api.post(`/inscriptions/${id}/validate/`, {
      status,
      rejection_reason,
    });
    return response.data;
  },

  /**
   * Update inscription
   */
  update: async (id, data) => {
    const response = await api.put(`/inscriptions/${id}/`, data);
    return response.data;
  },

  /**
   * Delete inscription
   */
  delete: async (id) => {
    const response = await api.delete(`/inscriptions/${id}/`);
    return response.data;
  },
};

// ============================================
// STATISTICS API (For Direction Dashboard)
// ============================================
export const statsAPI = {
  /**
   * Get dashboard statistics
   * Note: This endpoint needs to be implemented in backend
   */
  getDashboard: async () => {
    try {
      const response = await api.get('/statistics/dashboard/');
      return response.data;
    } catch (error) {
      // Fallback if endpoint not implemented yet
      console.warn('Statistics endpoint not implemented yet');
      return {
        total_inscriptions: 0,
        pending_inscriptions: 0,
        validated_inscriptions: 0,
        rejected_inscriptions: 0,
      };
    }
  },
};

// ============================================
// ERROR HANDLER UTILITY
// ============================================
export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    const status = error.response.status;
    const data = error.response.data;

    if (status === 400) {
      // Validation error
      return {
        message: 'Erreur de validation',
        details: data,
      };
    } else if (status === 401) {
      return {
        message: 'Non autorisé - veuillez vous reconnecter',
      };
    } else if (status === 403) {
      return {
        message: "Vous n'avez pas la permission d'effectuer cette action",
      };
    } else if (status === 404) {
      return {
        message: 'Ressource non trouvée',
      };
    } else if (status === 500) {
      return {
        message: 'Erreur serveur - veuillez réessayer plus tard',
      };
    }
  } else if (error.request) {
    // Request made but no response
    return {
      message: 'Impossible de contacter le serveur - vérifiez votre connexion',
    };
  }

  return {
    message: error.message || 'Une erreur est survenue',
  };
};



// Add this to frontend/src/services/api.js

// ============================================
// NOTE/GRADE API (For Teachers & Students)
// ============================================
export const noteAPI = {
  /**
   * Get all notes (filtered by role)
   */
  getAll: async () => {
    const response = await api.get('/notes/');
    return response.data;
  },

  /**
   * Get note by ID
   */
  getById: async (id) => {
    const response = await api.get(`/notes/${id}/`);
    return response.data;
  },

  /**
   * Create new note
   * @param {Object} data - {student, module, academic_year, note_controle, note_examen}
   */
  create: async (data) => {
    const response = await api.post('/notes/', data);
    return response.data;
  },

  /**
   * Update note
   */
  update: async (id, data) => {
    const response = await api.put(`/notes/${id}/`, data);
    return response.data;
  },

  /**
   * Partial update note
   */
  partialUpdate: async (id, data) => {
    const response = await api.patch(`/notes/${id}/`, data);
    return response.data;
  },

  /**
   * Delete note
   */
  delete: async (id) => {
    const response = await api.delete(`/notes/${id}/`);
    return response.data;
  },

  // ===== TEACHER-SPECIFIC ENDPOINTS =====

  /**
   * Get teacher's assigned modules
   * Endpoint: /notes/my_modules/
   */
  getMyModules: async () => {
    const response = await api.get('/notes/my_modules/');
    return response.data;
  },

  /**
   * Get students for a specific module
   * @param {number} moduleId
   * @param {string} academicYear - Format: "2024-2025"
   */
  getStudentsByModule: async (moduleId, academicYear = '2024-2025') => {
    const response = await api.get('/notes/students_by_module/', {
      params: { module_id: moduleId, academic_year: academicYear }
    });
    return response.data;
  },

  /**
   * Bulk update grades for multiple students
   * @param {number} moduleId
   * @param {string} academicYear
   * @param {Array} grades - [{student_id, note_controle, note_examen}, ...]
   */
  bulkUpdateGrades: async (moduleId, academicYear, grades) => {
    const response = await api.post('/notes/bulk_update_grades/', {
      module_id: moduleId,
      academic_year: academicYear,
      grades: grades
    });
    return response.data;
  },
};


// Export default API instance for custom calls
export default api;