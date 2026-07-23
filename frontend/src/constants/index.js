export const ROUTES = {
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  INCIDENTS: '/incidents',
  ANALYTICS: '/analytics',
  AUDIT_LOGS: '/audit-logs',
  UNAUTHORIZED: '/403-unauthorized',
  NOT_FOUND: '*',
};

export const ROLES = {
  ADMINISTRATOR: 'ADMINISTRATOR',
  STAFF: 'STAFF',
  OFFICER: 'OFFICER',
  CITIZEN: 'CITIZEN',
  GUEST: 'GUEST',
};

export const INCIDENT_CATEGORIES = {
  THEFT: 'THEFT',
  ASSAULT: 'ASSAULT',
  FIRE: 'FIRE',
  ACCIDENT: 'ACCIDENT',
  VANDALISM: 'VANDALISM',
  OTHER: 'OTHER',
};

export const INCIDENT_STATUSES = {
  DRAFT: 'DRAFT',
  SUBMITTED: 'SUBMITTED',
  ASSIGNED: 'ASSIGNED',
  IN_PROGRESS: 'IN_PROGRESS',
  RESOLVED: 'RESOLVED',
  CLOSED: 'CLOSED',
};

export const ASSIGNMENT_STATUSES = {
  ASSIGNED: 'ASSIGNED',
  ACCEPTED: 'ACCEPTED',
  REJECTED: 'REJECTED',
  RESOLVED: 'RESOLVED',
};

export const STATUS_COLORS = {
  // Incident Status
  [INCIDENT_STATUSES.DRAFT]: { bg: 'bg-slate-100', text: 'text-slate-700', border: 'border-slate-200' },
  [INCIDENT_STATUSES.SUBMITTED]: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  [INCIDENT_STATUSES.ASSIGNED]: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
  [INCIDENT_STATUSES.IN_PROGRESS]: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
  [INCIDENT_STATUSES.RESOLVED]: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  [INCIDENT_STATUSES.CLOSED]: { bg: 'bg-slate-200', text: 'text-slate-800', border: 'border-slate-300' },
  
  // Assignment Status
  [ASSIGNMENT_STATUSES.ASSIGNED]: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
  [ASSIGNMENT_STATUSES.ACCEPTED]: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  [ASSIGNMENT_STATUSES.REJECTED]: { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' },
  [ASSIGNMENT_STATUSES.RESOLVED]: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
};

export const CATEGORY_LABELS = {
  THEFT: 'Theft Loss Claim',
  ASSAULT: 'Personal Injury Claim',
  FIRE: 'Fire & Property Damage Claim',
  ACCIDENT: 'Auto Collision Claim',
  VANDALISM: 'Vandalism Loss Claim',
  OTHER: 'Other Loss Claim',
};

export const CATEGORY_COLORS = {
  THEFT: 'bg-slate-100 text-slate-800 border-slate-200',
  ASSAULT: 'bg-rose-100 text-rose-800 border-rose-200',
  FIRE: 'bg-orange-100 text-orange-800 border-orange-200',
  ACCIDENT: 'bg-amber-100 text-amber-800 border-amber-200',
  VANDALISM: 'bg-violet-100 text-violet-800 border-violet-200',
  OTHER: 'bg-gray-100 text-gray-800 border-gray-200',
};

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'auth_user',
  THEME: 'theme',
  PREFERENCES: 'user_preferences',
};
