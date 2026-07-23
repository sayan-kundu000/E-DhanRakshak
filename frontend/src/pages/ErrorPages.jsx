import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldX, AlertTriangle, FileQuestion } from 'lucide-react';
import { Button } from '../components/UI/UI';
import { ROUTES } from '../constants';

export const Unauthorized = () => {
  return (
    <div className="flex flex-col items-center justify-center p-6 text-center space-y-4">
      <ShieldX className="w-16 h-16 text-rose-500 animate-bounce" />
      <h2 className="font-display font-bold text-2xl text-slate-900 dark:text-white">403 - Access Denied</h2>
      <p className="text-slate-500 dark:text-slate-400 max-w-sm">
        You do not have the required Role-Based Access privileges to inspect this command page.
      </p>
      <div className="pt-2">
        <Link to={ROUTES.DASHBOARD}>
          <Button variant="primary">Return to Dashboard</Button>
        </Link>
      </div>
    </div>
  );
};

export const NotFound = () => {
  return (
    <div className="flex flex-col items-center justify-center p-6 text-center space-y-4">
      <FileQuestion className="w-16 h-16 text-brand-500 animate-pulse" />
      <h2 className="font-display font-bold text-2xl text-slate-900 dark:text-white">404 - Page Not Found</h2>
      <p className="text-slate-500 dark:text-slate-400 max-w-sm">
        The safety gateway resource or directory route you requested could not be located.
      </p>
      <div className="pt-2">
        <Link to={ROUTES.DASHBOARD}>
          <Button variant="primary">Return to Dashboard</Button>
        </Link>
      </div>
    </div>
  );
};

export const ErrorPage = () => {
  return (
    <div className="flex flex-col items-center justify-center p-6 text-center space-y-4">
      <AlertTriangle className="w-16 h-16 text-amber-500" />
      <h2 className="font-display font-bold text-2xl text-slate-900 dark:text-white">500 - Server Error</h2>
      <p className="text-slate-500 dark:text-slate-400 max-w-sm">
        An unexpected telemetry boundary exception occurred inside the application factory.
      </p>
      <div className="pt-2">
        <Link to={ROUTES.DASHBOARD}>
          <Button variant="primary">Return to Dashboard</Button>
        </Link>
      </div>
    </div>
  );
};
