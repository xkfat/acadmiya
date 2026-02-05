import { createContext, useState, useEffect, useContext } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // 1. Check if user is already logged in on refresh
  useEffect(() => {
    const checkUser = async () => {
      const token = localStorage.getItem('access_token');
      const role = localStorage.getItem('user_role'); // Simple hack for speed
      if (token && role) {
        setUser({ role }); // Restore session
      }
      setLoading(false);
    };
    checkUser();
  }, []);

  // 2. Login Function (Used by Person 2)
  const login = async (email, password) => {
    // Call Django API
    const response = await api.post('/auth/login/', { email, password });
    
    // Save Data
    const { access, role } = response.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('user_role', role);
    
    // Update State
    setUser({ role });
    return role; // Return role to redirect correctly
  };

  // 3. Logout Function
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);