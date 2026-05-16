/**
 * Authentication context for Kavach AI frontend.
 * Manages user login state and token storage.
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { getBackendUrl } from '@/lib/api';

const API_BASE = getBackendUrl();

interface User {
  id: string;
  email: string;
  name: string;
  level: string;
  xp: number;
  security_score: number;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  getToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user from localStorage on mount
  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const apiBase = getBackendUrl();
          console.debug(`[AUTH] Loading user profile from: ${apiBase}/api/auth/me`);
          
          const response = await fetch(`${apiBase}/api/auth/me`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          
          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
            console.info(`[AUTH] User profile loaded on mount: ${userData.email}`);
          } else if (response.status === 401) {
            // Token invalid/expired
            console.warn(`[AUTH] Token expired (${response.status}), clearing storage`);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
          } else {
            console.error(`[AUTH] Failed to load user: ${response.status}`);
          }
        } catch (error) {
          console.error('[AUTH] Error loading user on mount:', error);
          // Don't clear storage on network errors, just clear on auth errors
        }
      }
      setIsLoading(false);
    };

    loadUser();
  }, []);

  const login = React.useCallback(async (email: string, password: string) => {
    const apiBase = getBackendUrl();
    const loginUrl = `${apiBase}/api/auth/login`;
    
    try {
      console.info(`[AUTH] Attempting login for: ${email}`);
      console.debug(`[AUTH] Login URL: ${loginUrl}`);
      
      const response = await fetch(loginUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Login failed' }));
        console.error(`[AUTH] Login failed: ${response.status}`, errData);
        throw new Error(errData.detail || errData.message || `Login failed (${response.status})`);
      }

      const { access_token, refresh_token } = await response.json();
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      console.info(`[AUTH] Login successful, token saved`);

      // Get user data
      const userResponse = await fetch(`${apiBase}/api/auth/me`, {
        headers: { Authorization: `Bearer ${access_token}` },
      });

      if (userResponse.ok) {
        const userData = await userResponse.json();
        setUser(userData);
        console.info(`[AUTH] User profile loaded: ${userData.email}`);
      } else {
        console.warn(`[AUTH] Failed to load user profile (${userResponse.status})`);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Login failed';
      console.error(`[AUTH ERROR] ${message}`);
      
      if (message.includes('Network') || message.includes('Failed to Fetch')) {
        console.error(`[AUTH] Backend unreachable. API Base: ${apiBase}`);
      }
      
      throw error;
    }
  }, []);

  const signup = React.useCallback(async (email: string, password: string, name: string) => {
    const apiBase = getBackendUrl();
    const signupUrl = `${apiBase}/api/auth/signup`;
    
    try {
      console.info(`[AUTH] Attempting signup for: ${email}`);
      console.debug(`[AUTH] Signup URL: ${signupUrl}`);
      
      const response = await fetch(signupUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Signup failed' }));
        console.error(`[AUTH] Signup failed: ${response.status}`, errData);
        throw new Error(errData.detail || errData.message || `Signup failed (${response.status})`);
      }

      const { access_token, refresh_token } = await response.json();
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      console.info(`[AUTH] Signup successful, token saved`);

      // Get user data
      const userResponse = await fetch(`${apiBase}/api/auth/me`, {
        headers: { Authorization: `Bearer ${access_token}` },
      });

      if (userResponse.ok) {
        const userData = await userResponse.json();
        setUser(userData);
        console.info(`[AUTH] User profile loaded: ${userData.email}`);
      } else {
        console.warn(`[AUTH] Failed to load user profile (${userResponse.status})`);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Signup failed';
      console.error(`[AUTH ERROR] ${message}`);
      
      if (message.includes('Network') || message.includes('Failed to Fetch')) {
        console.error(`[AUTH] Backend unreachable. API Base: ${apiBase}`);
      }
      
      throw error;
    }
  }, []);

  const logout = React.useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  }, []);

  const getToken = React.useCallback(() => localStorage.getItem('access_token'), []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        signup,
        logout,
        getToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
