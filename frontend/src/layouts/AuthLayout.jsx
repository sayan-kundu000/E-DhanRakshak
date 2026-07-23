import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { Shield } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

export const AuthLayout = () => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 dark:bg-navy-950 transition-colors duration-300">
      {/* Top Banner Navigation */}
      <header className="p-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <Shield className="w-6 h-6 text-brand-600 dark:text-brand-400" />
          <span className="font-display font-bold text-lg tracking-tight text-brand-800 dark:text-white">E-Rakshak</span>
        </Link>
        <button
          onClick={toggleTheme}
          className="p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg focus-ring"
          aria-label="Toggle theme"
        >
          {isDark ? '☀️' : '🌙'}
        </button>
      </header>

      {/* Centered Glassmorphic Core Container */}
      <div className="flex-grow flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white dark:bg-navy-900 border border-slate-200/50 dark:border-slate-800/50 shadow-premium rounded-2xl overflow-hidden p-6 md:p-8 animate-scale-up">
          <div className="flex flex-col items-center mb-6">
            <div className="w-12 h-12 bg-brand-50 dark:bg-brand-950 flex items-center justify-center rounded-xl mb-4">
              <Shield className="w-6 h-6 text-brand-600 dark:text-brand-400" />
            </div>
            <h1 className="font-display font-bold text-2xl text-slate-900 dark:text-white text-center">E-Rakshak Portal</h1>
            <p className="text-slate-500 dark:text-slate-400 text-sm mt-1 text-center">Secure incident triage and public safety board</p>
          </div>

          <Outlet />
        </div>
      </div>
    </div>
  );
};
