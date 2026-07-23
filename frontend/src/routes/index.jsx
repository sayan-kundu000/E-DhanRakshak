import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Guards
import { AuthGuard } from '../guards/AuthGuard';
import { GuestGuard } from '../guards/GuestGuard';
import { RoleGuard } from '../guards/RoleGuard';

// Layouts
import { PublicLayout } from '../layouts/PublicLayout';
import { AuthLayout } from '../layouts/AuthLayout';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { ErrorLayout } from '../layouts/ErrorLayout';

// Pages
import { Login } from '../pages/Login';
import { Register } from '../pages/Register';
import { Dashboard } from '../pages/Dashboard';
import { IncidentsList } from '../pages/IncidentsList';
import { Analytics } from '../pages/Analytics';
import { AuditLogs } from '../pages/AuditLogs';
import { Unauthorized, NotFound, ErrorPage } from '../pages/ErrorPages';

// Constants
import { ROUTES, ROLES } from '../constants';
import { Card } from '../components/UI/UI';

// Simple guest helpline landing directory
const GuestLanding = () => {
  const helplines = [
    { name: 'National Emergency Response System', number: '112', desc: 'Single emergency helpline for immediate assistance.' },
    { name: 'Police Helpline Desk', number: '100', desc: 'Direct access to local police dispatch.' },
    { name: 'Fire Control Command', number: '101', desc: 'Emergency fire fighting service coordination.' },
    { name: 'Medical / Ambulance Dispatch', number: '102', desc: 'Fast ambulance deployment assistance.' },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 space-y-8 animate-fade-in">
      <div className="text-center space-y-2">
        <h2 className="font-display font-bold text-3xl text-slate-800 dark:text-white">Emergency Help Directories</h2>
        <p className="text-slate-500 dark:text-slate-400">Immediate citizen support links and public helpline directories</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {helplines.map((help, idx) => (
          <Card key={idx} className="flex flex-col justify-between hover:shadow-premium-hover transition-shadow duration-300">
            <div className="space-y-2">
              <h3 className="font-display font-semibold text-lg text-slate-850 dark:text-slate-200">{help.name}</h3>
              <p className="text-xs text-slate-500 dark:text-slate-450">{help.desc}</p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-baseline justify-between">
              <span className="text-[10px] uppercase font-bold text-slate-400">Emergency Number</span>
              <span className="text-2xl font-extrabold text-brand-600 dark:text-brand-400 font-display">{help.number}</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export const AppRoutes = () => {
  return (
    <Routes>
      {/* 1. Public Portal Pages */}
      <Route element={<PublicLayout />}>
        <Route path="/" element={<GuestLanding />} />
      </Route>

      {/* 2. Authentication Paths (Guest Checked) */}
      <Route element={<GuestGuard><AuthLayout /></GuestGuard>}>
        <Route path={ROUTES.LOGIN} element={<Login />} />
        <Route path={ROUTES.REGISTER} element={<Register />} />
      </Route>

      {/* 3. Secure Dashboard Paths (Auth Checked) */}
      <Route element={<AuthGuard><DashboardLayout /></AuthGuard>}>
        <Route path={ROUTES.DASHBOARD} element={<Dashboard />} />
        <Route path={ROUTES.INCIDENTS} element={<IncidentsList />} />
        
        {/* Staff/Admin Triage Routes */}
        <Route
          path={ROUTES.ANALYTICS}
          element={
            <RoleGuard allowedRoles={[ROLES.ADMINISTRATOR, ROLES.STAFF]}>
              <Analytics />
            </RoleGuard>
          }
        />
        
        {/* Administrator specific Audit Trail */}
        <Route
          path={ROUTES.AUDIT_LOGS}
          element={
            <RoleGuard allowedRoles={[ROLES.ADMINISTRATOR]}>
              <AuditLogs />
            </RoleGuard>
          }
        />
      </Route>

      {/* 4. Falling back to Error Templates */}
      <Route element={<ErrorLayout />}>
        <Route path={ROUTES.UNAUTHORIZED} element={<Unauthorized />} />
        <Route path="/500-error" element={<ErrorPage />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
};
export default AppRoutes;
