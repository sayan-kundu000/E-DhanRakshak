import React from 'react';
import { Outlet } from 'react-router-dom';

export const ErrorLayout = () => {
  return (
    <div className="flex min-h-screen items-center justify-center p-4 bg-slate-50 dark:bg-navy-950 transition-colors duration-300">
      <div className="w-full max-w-md text-center bg-white dark:bg-navy-900 border border-slate-200/50 dark:border-slate-800/50 shadow-premium p-8 rounded-2xl animate-scale-up">
        <Outlet />
      </div>
    </div>
  );
};
