import React from 'react';
import { AlertCircle, HelpCircle } from 'lucide-react';

// Reusable Primitive Button
export const Button = ({ children, variant = 'primary', loading = false, disabled = false, type = 'button', className = '', ...props }) => {
  const baseStyle = 'inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all focus-ring select-none active:scale-[0.98]';
  
  const variants = {
    primary: 'bg-brand-600 hover:bg-brand-700 text-white shadow-sm border border-brand-700/20 disabled:bg-brand-300 dark:disabled:bg-brand-900/50',
    secondary: 'bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-50',
    danger: 'bg-rose-600 hover:bg-rose-700 text-white shadow-sm border border-rose-700/20 disabled:bg-rose-300',
    ghost: 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-50',
  };

  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={`${baseStyle} ${variants[variant]} ${className}`}
      {...props}
    >
      {loading && (
        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
      )}
      {children}
    </button>
  );
};

// Reusable Primitive Card
export const Card = ({ children, className = '', ...props }) => {
  return (
    <div className={`bg-white dark:bg-navy-900 border border-slate-200/60 dark:border-slate-800/60 shadow-premium rounded-2xl p-6 ${className}`} {...props}>
      {children}
    </div>
  );
};

// Reusable Primitive Badge / Status Label
export const Badge = ({ children, colorStyles = { bg: 'bg-slate-100', text: 'text-slate-700', border: 'border-slate-200' }, className = '' }) => {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border uppercase tracking-wider ${colorStyles.bg} ${colorStyles.text} ${colorStyles.border} ${className}`}>
      {children}
    </span>
  );
};

// Reusable Primitive Table Structure
export const Table = ({ headers = [], children, className = '' }) => {
  return (
    <div className={`overflow-x-auto border border-slate-200/60 dark:border-slate-800/60 rounded-xl bg-white dark:bg-navy-900 ${className}`}>
      <table className="w-full text-left border-collapse text-sm">
        <thead>
          <tr className="bg-slate-50 dark:bg-navy-950 border-b border-slate-200/60 dark:border-slate-800/60 text-slate-500 dark:text-slate-400 font-semibold select-none">
            {headers.map((h, i) => (
              <th key={i} className="px-6 py-4.5 font-display tracking-wider font-semibold uppercase text-xs">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800/50">
          {children}
        </tbody>
      </table>
    </div>
  );
};

// Reusable Skeleton Placeholder loader
export const Skeleton = ({ className = '', variant = 'text' }) => {
  const shapes = {
    text: 'h-4 w-full rounded-md',
    avatar: 'w-10 h-10 rounded-full',
    rect: 'h-32 w-full rounded-2xl',
  };
  
  return (
    <div className={`bg-slate-200/80 dark:bg-slate-800/80 shimmer ${shapes[variant]} ${className}`} />
  );
};

// Reusable Modal Component
export const Modal = ({ isOpen, onClose, title, children, maxWidthClass = 'max-w-xl' }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-fade-in">
      {/* Background click to close */}
      <div onClick={onClose} className="fixed inset-0" />
      
      <div className={`relative bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xl w-full ${maxWidthClass} max-h-[90vh] flex flex-col z-10 overflow-hidden animate-scale-up`}>
        {/* Header */}
        <div className="px-6 py-4.5 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <h3 className="font-display font-bold text-lg text-slate-900 dark:text-white">{title}</h3>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-600 dark:hover:text-slate-350 rounded-lg transition-colors focus-ring"
          >
            ❌
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto flex-grow">
          {children}
        </div>
      </div>
    </div>
  );
};

// Reusable Empty State panel
export const EmptyState = ({ title = 'No data available', description = 'No matching entries were found.', className = '' }) => {
  return (
    <div className={`flex flex-col items-center justify-center p-12 text-center bg-white dark:bg-navy-900 border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl ${className}`}>
      <HelpCircle className="w-12 h-12 text-slate-400 dark:text-slate-600 mb-3" />
      <h4 className="text-base font-bold text-slate-800 dark:text-slate-200 font-display">{title}</h4>
      <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-sm">{description}</p>
    </div>
  );
};

// Reusable Tabs sheets
export const Tabs = ({ tabs = [], activeTab, onChange, className = '' }) => {
  return (
    <div className={`flex border-b border-slate-200 dark:border-slate-800 overflow-x-auto ${className}`}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`px-5 py-3 border-b-2 text-sm font-semibold tracking-wide whitespace-nowrap transition-colors focus-ring ${
            activeTab === tab.id
              ? 'border-brand-600 text-brand-600 dark:border-brand-400 dark:text-brand-400'
              : 'border-transparent text-slate-550 dark:text-slate-400 hover:text-slate-850 dark:hover:text-slate-250'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
};
