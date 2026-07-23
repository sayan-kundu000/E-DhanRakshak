import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/axios';
import { STORAGE_KEYS } from '../constants';
import { storage } from '../utils';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Sync user profile from token at boot time
  useEffect(() => {
    const initAuth = async () => {
      const accessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
      const cachedUser = storage.get(STORAGE_KEYS.USER);

      if (accessToken) {
        try {
          if (cachedUser) {
            setUser(cachedUser);
          }
          // Verify & fetch fresh profile from /auth/me
          const response = await api.get('/auth/me');
          if (response.data && response.data.success) {
            const userData = response.data.data;
            setUser(userData);
            storage.set(STORAGE_KEYS.USER, userData);
          }
        } catch (e) {
          console.error('Session restoration failed:', e);
          logout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      if (response.data && response.data.success) {
        const { access_token, refresh_token, user: userData } = response.data.data;
        
        storage.set(STORAGE_KEYS.ACCESS_TOKEN, access_token);
        storage.set(STORAGE_KEYS.REFRESH_TOKEN, refresh_token);
        storage.set(STORAGE_KEYS.USER, userData);
        
        setUser(userData);
        return { success: true };
      }
      return { success: false, error: 'Failed to authenticate user.' };
    } catch (err) {
      const errorMsg = err.response?.data?.error?.message || 'Invalid email or password.';
      return { success: false, error: errorMsg };
    }
  };

  const register = async (payload) => {
    try {
      const response = await api.post('/auth/register', payload);
      if (response.data && response.data.success) {
        return { success: true };
      }
      return { success: false, error: 'Registration failed.' };
    } catch (err) {
      const errorMsg = err.response?.data?.error?.message || 'Email already registered or validation failed.';
      return { success: false, error: errorMsg };
    }
  };

  const logout = () => {
    storage.clearAuth();
    setUser(null);
  };

  const hasRole = (roles) => {
    if (!user) return false;
    if (Array.isArray(roles)) {
      return roles.includes(user.role);
    }
    return user.role === roles;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
