import axios from 'axios';
import { STORAGE_KEYS } from '../constants';
import { storage } from '../utils';

// Centralized Axios Instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Inject Access Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    // Note: stored string might be wrapped in quotes because of JSON.stringify in utility.
    // Clean it up if needed.
    const cleanToken = token ? token.replace(/"/g, '') : null;
    if (cleanToken) {
      config.headers.Authorization = `Bearer ${cleanToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Mock Database definition for standalone preview and unimplemented endpoints
const MOCK_DB = {
  users: [
    { id: '1', email: 'admin@erakshak.gov', full_name: 'Director Sharma (Admin)', role: 'ADMINISTRATOR', is_active: true },
    { id: '2', email: 'dispatcher@erakshak.gov', full_name: 'Officer Rawat (Staff)', role: 'STAFF', is_active: true },
    { id: '3', email: 'field.officer@erakshak.gov', full_name: 'Inspector Vijay (Officer)', role: 'OFFICER', is_active: true },
    { id: '4', email: 'citizen@gmail.com', full_name: 'Aarav Kumar (Citizen)', role: 'CITIZEN', is_active: true },
  ],
  incidents: [
    {
      id: 'i1',
      title: 'Structural Fire in Central Market',
      description: 'Massive fire break out near shop number 12. Multiple people trapped inside, smoke spreading rapidly.',
      category: 'FIRE',
      status: 'ASSIGNED',
      latitude: 28.6139,
      longitude: 77.2090,
      reporter_id: '4',
      reporter_name: 'Aarav Kumar',
      risk_score: 92.5,
      factors: { category_severity: 9, spatial_density: 8, temporal_weight: 5 },
      created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
      updated_at: new Date(Date.now() - 3600000 * 2).toISOString(),
      assignment: { id: 'a1', officer_name: 'Inspector Vijay', assigned_at: new Date(Date.now() - 3600000 * 1.5).toISOString() }
    },
    {
      id: 'i2',
      title: 'Aggravated Assault near Transit Hub',
      description: 'Two suspects armed with blunt force weapons attacking pedestrians outside platform 3 gate.',
      category: 'ASSAULT',
      status: 'IN_PROGRESS',
      latitude: 28.6250,
      longitude: 77.2200,
      reporter_id: '4',
      reporter_name: 'Aarav Kumar',
      risk_score: 87.0,
      factors: { category_severity: 8.5, spatial_density: 6.5, temporal_weight: 4 },
      created_at: new Date(Date.now() - 3600000 * 5).toISOString(),
      updated_at: new Date(Date.now() - 3600000 * 4).toISOString(),
      assignment: { id: 'a2', officer_name: 'Inspector Vijay', assigned_at: new Date(Date.now() - 3600000 * 4.5).toISOString() }
    },
    {
      id: 'i3',
      title: 'Traffic Collision on Ring Road',
      description: 'Multiple vehicle crash involving a transport truck and two sedans. Blocking three highway lanes.',
      category: 'ACCIDENT',
      status: 'SUBMITTED',
      latitude: 28.6400,
      longitude: 77.2500,
      reporter_id: '4',
      reporter_name: 'Aarav Kumar',
      risk_score: 64.2,
      factors: { category_severity: 6, spatial_density: 4, temporal_weight: 3.2 },
      created_at: new Date(Date.now() - 3600000 * 8).toISOString(),
      updated_at: new Date(Date.now() - 3600000 * 8).toISOString(),
    },
    {
      id: 'i4',
      title: 'Storefront Vandalism',
      description: 'Spraying gang tags and shattering display windows at commercial complex during midnight hours.',
      category: 'VANDALISM',
      status: 'RESOLVED',
      latitude: 28.5800,
      longitude: 77.1900,
      reporter_id: '4',
      reporter_name: 'Aarav Kumar',
      risk_score: 41.5,
      factors: { category_severity: 4, spatial_density: 3, temporal_weight: 2 },
      created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
      updated_at: new Date(Date.now() - 86400000 * 1.8).toISOString(),
    }
  ],
  auditLogs: [
    { id: 1, user_id: '1', email: 'admin@erakshak.gov', action: 'USER_REGISTRATION', ip_address: '192.168.1.10', logged_at: new Date(Date.now() - 86400000 * 3).toISOString(), payload_details: { email: 'citizen@gmail.com', role: 'CITIZEN' } },
    { id: 2, user_id: '2', email: 'dispatcher@erakshak.gov', action: 'ASSIGN_INCIDENT', ip_address: '192.168.1.12', logged_at: new Date(Date.now() - 3600000 * 5).toISOString(), payload_details: { incident_id: 'i1', officer_id: '3' } },
    { id: 3, user_id: '3', email: 'field.officer@erakshak.gov', action: 'UPDATE_ASSIGNMENT_STATUS', ip_address: '10.0.2.15', logged_at: new Date(Date.now() - 3600000 * 4).toISOString(), payload_details: { assignment_id: 'a2', status: 'ACCEPTED' } },
  ],
  settings: [
    { key: 'RISK_THRESHOLD_HIGH', value: '75.0', description: 'Priority alert trigger score bounds', category: 'RISK_ENGINE' },
    { key: 'MAX_DISPATCH_RADIUS_KM', value: '15.0', description: 'Workload assigner proximity radius', category: 'GEO_ROUTING' },
    { key: 'NOTIFY_CITIZENS_ON_ASSIGN', value: 'true', description: 'Enable automatic email dispatch notifications', category: 'NOTIFICATIONS' }
  ]
};

// Response Interceptor: Token Refresh & Mock Fallback Handler
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // 1. Handle Token Expired (401)
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
        const cleanRefresh = refreshToken ? refreshToken.replace(/"/g, '') : null;
        if (!cleanRefresh) throw new Error('No refresh token');

        // Request new access token
        const res = await axios.post(`${api.defaults.baseURL}/auth/refresh`, {}, {
          headers: { Authorization: `Bearer ${cleanRefresh}` }
        });

        if (res.data && res.data.success) {
          const newAccessToken = res.data.data.access_token;
          storage.set(STORAGE_KEYS.ACCESS_TOKEN, newAccessToken);
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return api(originalRequest);
        }
      } catch (refreshErr) {
        console.error('Session refresh failed. Forcing logout...', refreshErr);
        storage.clearAuth();
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }

    // 2. Mock Fallback Handler (Runs when local server is offline or returns 404/500 for unimplemented routes)
    const isOffline = !error.response || error.code === 'ERR_NETWORK';
    const isUnimplemented = error.response && (error.response.status === 404 || error.response.status === 500);

    if ((isOffline || isUnimplemented) && originalRequest) {
      console.warn(`Axios Request to ${originalRequest.url} failed. Deploying E-Rakshak Mock Fallback...`);
      const url = originalRequest.url;
      const method = originalRequest.method.toLowerCase();
      
      // Match Endpoints
      // GET /api/v1/auth/me
      if (url.includes('/auth/me') && method === 'get') {
        const user = storage.get(STORAGE_KEYS.USER);
        if (user) {
          return { data: { success: true, data: user, message: 'Mock Profile' } };
        }
        return Promise.reject({ response: { status: 401, data: { success: false, message: 'Unauthenticated' } } });
      }

      // POST /api/v1/auth/login
      if (url.includes('/auth/login') && method === 'post') {
        const payload = JSON.parse(originalRequest.data);
        const user = MOCK_DB.users.find(u => u.email === payload.email);
        if (user) {
          const authData = {
            access_token: 'mock_jwt_access_token',
            refresh_token: 'mock_jwt_refresh_token',
            user
          };
          return { data: { success: true, data: authData, message: 'Mock Login Successful' } };
        }
        return Promise.reject({ response: { status: 400, data: { success: false, error: { message: 'Invalid mock credentials' } } } });
      }

      // GET /api/v1/incidents
      if (url.includes('/incidents') && method === 'get' && !url.includes('/auto-assign')) {
        return {
          data: {
            success: true,
            data: MOCK_DB.incidents,
            pagination: { total_records: MOCK_DB.incidents.length, page: 1, limit: 10, total_pages: 1 }
          }
        };
      }

      // POST /api/v1/incidents
      if (url.includes('/incidents') && method === 'post') {
        const payload = JSON.parse(originalRequest.data);
        const newIncident = {
          id: `i${MOCK_DB.incidents.length + 1}`,
          ...payload,
          status: 'SUBMITTED',
          risk_score: Math.min(100.0, (payload.category === 'FIRE' ? 90 : 50) + Math.random() * 10),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        MOCK_DB.incidents.unshift(newIncident);
        return { data: { success: true, data: newIncident, message: 'Mock incident created' } };
      }

      // POST /api/v1/assignments
      if (url.includes('/assignments') && method === 'post') {
        const payload = JSON.parse(originalRequest.data);
        const incident = MOCK_DB.incidents.find(i => i.id === payload.incident_id);
        const officer = MOCK_DB.users.find(u => u.id === payload.officer_id);
        if (incident && officer) {
          incident.status = 'ASSIGNED';
          incident.assignment = { id: `a${Math.random()}`, officer_name: officer.full_name, assigned_at: new Date().toISOString() };
          return { data: { success: true, data: incident.assignment, message: 'Incident assigned successfully' } };
        }
      }

      // GET /api/v1/admin/users
      if (url.includes('/admin/users') && method === 'get') {
        return { data: { success: true, data: MOCK_DB.users, message: 'Mock Users list' } };
      }

      // GET /api/v1/admin/audit-logs
      if (url.includes('/admin/audit-logs') && method === 'get') {
        return { data: { success: true, data: MOCK_DB.auditLogs, message: 'Mock Audit Logs' } };
      }

      // GET /api/v1/analytics/dashboard
      if (url.includes('/analytics/dashboard') && method === 'get') {
        const role = storage.get(STORAGE_KEYS.USER)?.role || 'CITIZEN';
        const dashboardStats = {
          total_incidents: MOCK_DB.incidents.length,
          open_incidents: MOCK_DB.incidents.filter(i => i.status !== 'RESOLVED' && i.status !== 'CLOSED').length,
          resolved_incidents: MOCK_DB.incidents.filter(i => i.status === 'RESOLVED' || i.status === 'CLOSED').length,
          critical_alerts: MOCK_DB.incidents.filter(i => i.risk_score >= 75).length,
          response_metrics: { avg_dispatch_time: '12 mins', avg_resolution_time: '2.4 hours' },
          category_distribution: [
            { category: 'FIRE', count: MOCK_DB.incidents.filter(i => i.category === 'FIRE').length },
            { category: 'ASSAULT', count: MOCK_DB.incidents.filter(i => i.category === 'ASSAULT').length },
            { category: 'ACCIDENT', count: MOCK_DB.incidents.filter(i => i.category === 'ACCIDENT').length },
            { category: 'VANDALISM', count: MOCK_DB.incidents.filter(i => i.category === 'VANDALISM').length },
          ]
        };
        return { data: { success: true, data: dashboardStats, message: 'Mock dashboard stats compiled' } };
      }

      // GET /api/v1/analytics/trends
      if (url.includes('/analytics/trends') && method === 'get') {
        return {
          data: {
            success: true,
            data: {
              days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
              counts: [12, 19, 3, 5, 2, 3, 9]
            }
          }
        };
      }

      // GET /api/v1/analytics/charts/category
      if (url.includes('/analytics/charts/category') && method === 'get') {
        return {
          data: {
            success: true,
            data: {
              labels: ['Fire', 'Assault', 'Accident', 'Vandalism', 'Other'],
              values: [15, 25, 20, 10, 5]
            }
          }
        };
      }

      // GET /api/v1/analytics/charts/trend
      if (url.includes('/analytics/charts/trend') && method === 'get') {
        return {
          data: {
            success: true,
            data: {
              x: ['2026-07-17', '2026-07-18', '2026-07-19', '2026-07-20', '2026-07-21', '2026-07-22', '2026-07-23'],
              y: [40, 45, 30, 60, 55, 70, 65]
            }
          }
        };
      }

      // GET /api/v1/settings
      if (url.includes('/settings') && method === 'get') {
        return { data: { success: true, data: MOCK_DB.settings, message: 'Mock settings' } };
      }
    }

    return Promise.reject(error);
  }
);

export default api;
export { MOCK_DB };
