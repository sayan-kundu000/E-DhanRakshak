import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import { DashboardProvider } from './contexts/DashboardContext';
import { AnalyticsProvider } from './contexts/AnalyticsContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { SettingsProvider } from './contexts/SettingsContext';
import { AppRoutes } from './routes';

export const App = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <NotificationProvider>
          <DashboardProvider>
            <AnalyticsProvider>
              <SettingsProvider>
                <BrowserRouter>
                  <AppRoutes />
                </BrowserRouter>
              </SettingsProvider>
            </AnalyticsProvider>
          </DashboardProvider>
        </NotificationProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};
export default App;
