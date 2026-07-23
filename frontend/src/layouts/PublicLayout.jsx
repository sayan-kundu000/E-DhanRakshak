import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { Shield, PhoneCall } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

export const PublicLayout = () => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 dark:bg-navy-950 text-slate-900 dark:text-slate-100 transition-colors duration-300">
      {/* Top Banner Directory */}
      <header className="sticky top-0 z-40 bg-white/80 dark:bg-navy-900/80 backdrop-blur-md border-b border-slate-200/50 dark:border-slate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-brand-600 dark:text-brand-400" />
            <span className="font-display font-bold text-xl tracking-tight text-brand-800 dark:text-white">E-DhanRakshak</span>
          </div>
          
          <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600 dark:text-slate-300">
            <Link to="/" className="hover:text-brand-500 transition-colors">Helpline Directory</Link>
            <Link to="/login" className="px-4 py-2 text-white bg-brand-600 hover:bg-brand-700 rounded-lg shadow-sm transition-colors focus-ring">
              Portal Login
            </Link>
          </nav>

          <div className="flex items-center gap-3">
            <button
              onClick={toggleTheme}
              className="p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg focus-ring"
              aria-label="Toggle theme"
            >
              {isDark ? '☀️' : '🌙'}
            </button>
            <Link to="/login" className="md:hidden px-3 py-1.5 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-lg transition-colors">
              Login
            </Link>
          </div>
        </div>
      </header>

      {/* Main Grid View */}
      <main className="flex-grow">
        <Outlet />
      </main>

      {/* Footer System */}
      <footer className="bg-slate-100 dark:bg-navy-950 border-t border-slate-200/50 dark:border-slate-800/50 py-8 text-center text-xs text-slate-500 dark:text-slate-400">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© {new Date().getFullYear()} E-DhanRakshak. Enterprise Community Safety Platform.</p>
          <div className="flex gap-4">
            <a href="#" className="hover:underline">Privacy Policy</a>
            <a href="#" className="hover:underline">Terms of Service</a>
            <a href="#" className="hover:underline">Emergency Guidelines</a>
          </div>
        </div>
      </footer>
    </div>
  );
};
