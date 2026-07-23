import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { Shield, LayoutDashboard, FileText, PieChart, History, Settings, Users, LogOut, X } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { ROUTES, ROLES } from '../../constants';

export const Sidebar = ({ isOpen, onClose }) => {
  const { user, logout, hasRole } = useAuth();

  const getNavLinks = () => {
    const links = [
      { to: ROUTES.DASHBOARD, label: 'Dashboard', icon: LayoutDashboard },
      { to: ROUTES.INCIDENTS, label: 'Incidents Directory', icon: FileText },
    ];

    if (hasRole([ROLES.ADMINISTRATOR, ROLES.STAFF])) {
      links.push({ to: ROUTES.ANALYTICS, label: 'Analytics Panel', icon: PieChart });
      links.push({ to: ROUTES.AUDIT_LOGS, label: 'System Audit Logs', icon: History });
    }

    return links;
  };

  const navLinks = getNavLinks();

  const activeClass = 'flex items-center gap-3 px-4 py-3 rounded-lg text-white bg-brand-600 shadow-md transition-all font-medium duration-200';
  const inactiveClass = 'flex items-center gap-3 px-4 py-3 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all duration-200';

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-navy-900 border-r border-slate-200/50 dark:border-slate-800/50 flex flex-col transform transition-transform duration-300 md:relative md:transform-none ${
        isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-6 border-b border-slate-200/50 dark:border-slate-800/50">
        <Link to="/" className="flex items-center gap-3">
          <Shield className="w-6 h-6 text-brand-600 dark:text-brand-400" />
          <span className="font-display font-bold text-lg text-brand-800 dark:text-white">E-DhanRakshak</span>
        </Link>
        <button onClick={onClose} className="md:hidden p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Nav List */}
      <nav className="flex-grow px-4 py-6 space-y-1.5 overflow-y-auto">
        {navLinks.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.to}
              to={link.to}
              onClick={() => {
                if (window.innerWidth < 768) onClose();
              }}
              className={({ isActive }) => (isActive ? activeClass : inactiveClass)}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              <span>{link.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Profile Footer */}
      {user && (
        <div className="p-4 border-t border-slate-200/50 dark:border-slate-800/50 bg-slate-50 dark:bg-navy-950/50">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-brand-100 dark:bg-brand-950 flex items-center justify-center rounded-full border border-brand-200/50 dark:border-brand-800/50 text-brand-700 dark:text-brand-300 font-bold font-display uppercase">
              {user.full_name?.charAt(0)}
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate">{user.full_name}</p>
              <span className="inline-block text-[10px] font-bold px-1.5 py-0.5 mt-0.5 rounded bg-brand-50 dark:bg-brand-900/50 text-brand-600 dark:text-brand-400 border border-brand-100 dark:border-brand-800 uppercase tracking-wider">
                {user.role}
              </span>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 text-xs font-semibold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/20 border border-rose-200 dark:border-rose-900/50 rounded-lg transition-colors focus-ring"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>
      )}
    </aside>
  );
};
