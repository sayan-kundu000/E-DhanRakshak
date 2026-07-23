import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from './AuthContext';

const AnalyticsContext = createContext();

export const AnalyticsProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Interactive Cross Filtering States
  const [filters, setFilters] = useState({
    q: '',
    category: '',
    status: '',
    startDate: '',
    endDate: '',
  });

  const fetchTrends = async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    try {
      const res = await api.get('/analytics/trends');
      if (res.data && res.data.success) {
        setTrends(res.data.data);
      }
    } catch (e) {
      console.warn('Analytics API error. Loading trend simulation details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchTrends();
    } else {
      setTrends(null);
    }
  }, [isAuthenticated]);

  const updateFilters = (newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const resetFilters = () => {
    setFilters({
      q: '',
      category: '',
      status: '',
      startDate: '',
      endDate: '',
    });
  };

  return (
    <AnalyticsContext.Provider
      value={{
        trends,
        filters,
        loading,
        updateFilters,
        resetFilters,
        refreshTrends: fetchTrends,
      }}
    >
      {children}
    </AnalyticsContext.Provider>
  );
};

export const useAnalytics = () => {
  const context = useContext(AnalyticsContext);
  if (!context) throw new Error('useAnalytics must be used within an AnalyticsProvider');
  return context;
};
