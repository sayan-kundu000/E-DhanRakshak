import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/axios';
import { STORAGE_KEYS } from '../constants';
import { storage } from '../utils';
import { useAuth } from './AuthContext';

const SettingsContext = createContext();

export const SettingsProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [preferences, setPreferences] = useState(() => {
    return storage.get(STORAGE_KEYS.PREFERENCES) || {
      compactMode: false,
      enableSounds: true,
      emailAlerts: true,
      smsAlerts: false,
    };
  });
  const [systemSettings, setSystemSettings] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      fetchPreferences();
      fetchSystemSettings();
    }
  }, [isAuthenticated]);

  const fetchPreferences = async () => {
    try {
      const response = await api.get('/settings/preferences');
      if (response.data && response.data.success) {
        setPreferences(response.data.data);
        storage.set(STORAGE_KEYS.PREFERENCES, response.data.data);
      }
    } catch (e) {
      console.warn('Could not sync user preferences, falling back to local configurations.');
    }
  };

  const fetchSystemSettings = async () => {
    setLoading(true);
    try {
      const response = await api.get('/settings');
      if (response.data && response.data.success) {
        setSystemSettings(response.data.data);
      }
    } catch (e) {
      console.warn('Could not fetch system settings.');
    } finally {
      setLoading(false);
    }
  };

  const updatePreference = async (newPrefs) => {
    const updated = { ...preferences, ...newPrefs };
    setPreferences(updated);
    storage.set(STORAGE_KEYS.PREFERENCES, updated);

    if (isAuthenticated) {
      try {
        await api.put('/settings/preferences', updated);
      } catch (e) {
        console.warn('Preferences changes saved locally, sync with backend failed.');
      }
    }
  };

  return (
    <SettingsContext.Provider
      value={{
        preferences,
        systemSettings,
        loading,
        updatePreference,
        refreshSettings: fetchSystemSettings,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) throw new Error('useSettings must be used within a SettingsProvider');
  return context;
};
