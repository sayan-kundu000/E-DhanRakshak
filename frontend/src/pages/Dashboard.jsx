import React, { useState, useEffect } from 'react';
import { Plus, UserPlus, ShieldAlert, AlertTriangle, CheckCircle, Clock, Users, RefreshCw } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import { useDashboardStats } from '../contexts/DashboardContext';
import api from '../api/axios';

// Reusable Components
import { Card, Button, Badge, Modal } from '../components/UI/UI';
import { Input, Select, Textarea } from '../components/UI/FormComponents';
import { FileUpload } from '../components/UI/FileUpload';
import { DonutChart, GaugeChart } from '../components/Charts/ChartLibrary';
import { StatisticsWidget, ActivityWidget, SystemHealthPanel } from '../components/Dashboard/Widgets';

// Constants & Utils
import { STATUS_COLORS, CATEGORY_LABELS, ROLES, STORAGE_KEYS } from '../constants';
import { formatDate } from '../utils';

export const Dashboard = () => {
  const { user, hasRole } = useAuth();
  const { success, error, warning } = useNotification();
  
  // Connect to the shared Dashboard Telemetry context
  const {
    stats,
    systemHealth,
    loading,
    refreshing,
    triggerManualRefresh,
  } = useDashboardStats();

  const [incidents, setIncidents] = useState([]);
  const [officers, setOfficers] = useState([]);

  // Modals state
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState(null);

  // Form submission state
  const [reportingIncident, setReportingIncident] = useState(false);
  const [assigningIncident, setAssigningIncident] = useState(false);

  // Report Form fields
  const [reportForm, setReportForm] = useState({
    title: '',
    description: '',
    category: 'THEFT',
    latitude: '28.6139',
    longitude: '77.2090',
    attachment: null,
  });

  // Assign Form field
  const [selectedOfficerId, setSelectedOfficerId] = useState('');

  useEffect(() => {
    fetchIncidents();
    if (hasRole([ROLES.ADMINISTRATOR, ROLES.STAFF])) {
      fetchOfficers();
    }
  }, [stats]);

  const fetchIncidents = async () => {
    try {
      const response = await api.get('/incidents');
      if (response.data && response.data.success) {
        setIncidents(response.data.data.slice(0, 5));
      }
    } catch (e) {
      console.warn('Unable to retrieve incidents.');
    }
  };

  const fetchOfficers = async () => {
    try {
      const response = await api.get('/admin/users');
      if (response.data && response.data.success) {
        setOfficers(response.data.data.filter(u => u.role === ROLES.OFFICER && u.is_active));
      }
    } catch (e) {
      console.warn('Unable to retrieve active officers.');
    }
  };

  const handleReportSubmit = async (e) => {
    e.preventDefault();
    if (!reportForm.title || !reportForm.description) {
      error('Please complete all mandatory fields.');
      return;
    }

    setReportingIncident(true);
    try {
      const payload = {
        title: reportForm.title,
        description: reportForm.description,
        category: reportForm.category,
        latitude: parseFloat(reportForm.latitude),
        longitude: parseFloat(reportForm.longitude),
      };

      const res = await api.post('/incidents', payload);
      if (res.data && res.data.success) {
        success('Incident report logged successfully!');
        setReportModalOpen(false);
        setReportForm({
          title: '',
          description: '',
          category: 'THEFT',
          latitude: '28.6139',
          longitude: '77.2090',
          attachment: null,
        });
        triggerManualRefresh();
      }
    } catch (err) {
      error(err.response?.data?.error?.message || 'Failed to file report.');
    } finally {
      setReportingIncident(false);
    }
  };

  const handleAssignSubmit = async (e) => {
    e.preventDefault();
    if (!selectedOfficerId || !selectedIncident) {
      error('Please select an active responder.');
      return;
    }

    setAssigningIncident(true);
    try {
      const res = await api.post('/assignments', {
        incident_id: selectedIncident.id,
        officer_id: selectedOfficerId,
      });

      if (res.data && res.data.success) {
        success('Officer dispatched successfully!');
        setAssignModalOpen(false);
        setSelectedOfficerId('');
        triggerManualRefresh();
      }
    } catch (err) {
      error(err.response?.data?.error?.message || 'Assignment failed.');
    } finally {
      setAssigningIncident(false);
    }
  };

  const openAssignModal = (incident) => {
    setSelectedIncident(incident);
    setAssignModalOpen(true);
  };

  if (loading && !stats) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <div className="w-12 h-12 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="mt-4 text-sm font-medium text-slate-500">Loading system metrics...</p>
      </div>
    );
  }

  // 1. Render Citizen UI Dashboard
  const renderCitizenDashboard = () => (
    <div className="space-y-8 animate-fade-in">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2 space-y-4">
          <h3 className="font-display font-bold text-lg text-slate-900 dark:text-white">Report System Issues</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Submit local issues directly to E-DhanRakshak control centers. Our analytics dispatch engine will score the risk severity and map resources.
          </p>
          <Button variant="primary" onClick={() => setReportModalOpen(true)}>
            <Plus className="w-4.5 h-4.5" />
            <span>File New Incident Report</span>
          </Button>
        </Card>

        <Card className="flex flex-col justify-between">
          <h3 className="font-display font-bold text-sm text-slate-400 uppercase tracking-wider">My Active Reports</h3>
          <div className="text-center py-6">
            <h4 className="text-4xl font-extrabold text-brand-600 dark:text-brand-400 font-display">
              {stats?.open_incidents || 0}
            </h4>
            <p className="text-xs text-slate-400 mt-2">Incidents currently in review/progress</p>
          </div>
        </Card>
      </div>

      <Card>
        <h3 className="font-display font-bold text-lg text-slate-900 dark:text-white mb-6">Recent Status Updates</h3>
        <div className="divide-y divide-slate-100 dark:divide-slate-800/50">
          {incidents.length === 0 ? (
            <p className="text-center py-6 text-slate-400 text-sm">You have not submitted any reports yet.</p>
          ) : (
            incidents.map(inc => (
              <div key={inc.id} className="py-4 flex items-center justify-between gap-4 first:pt-0 last:pb-0">
                <div className="min-w-0">
                  <h4 className="font-semibold text-slate-800 dark:text-slate-200 text-sm truncate">{inc.title}</h4>
                  <p className="text-xs text-slate-400 mt-1">Filed: {formatDate(inc.created_at)}</p>
                </div>
                <Badge colorStyles={STATUS_COLORS[inc.status]}>{inc.status}</Badge>
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  );

  // 2. Render Officer UI Dashboard
  const renderOfficerDashboard = () => {
    const completionRate = stats?.total_incidents 
      ? Math.round((stats.resolved_incidents / stats.total_incidents) * 100) 
      : 80;

    return (
      <div className="space-y-8 animate-fade-in">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-6">
            <Card>
              <h3 className="font-display font-bold text-lg text-slate-900 dark:text-white mb-6">Active Dispatches</h3>
              <div className="divide-y divide-slate-100 dark:divide-slate-800/50">
                {incidents.filter(i => i.status === 'ASSIGNED' || i.status === 'IN_PROGRESS').length === 0 ? (
                  <p className="text-center py-6 text-slate-400 text-sm">No active dispatches. You are clear!</p>
                ) : (
                  incidents.map(inc => (
                    <div key={inc.id} className="py-4 flex items-center justify-between gap-4 first:pt-0 last:pb-0">
                      <div>
                        <h4 className="font-semibold text-slate-800 dark:text-slate-200 text-sm">{inc.title}</h4>
                        <p className="text-xs text-slate-400 mt-1">Severity Score: {inc.risk_score?.toFixed(1)} | Location: {inc.latitude}, {inc.longitude}</p>
                      </div>
                      <Badge colorStyles={STATUS_COLORS[inc.status]}>{inc.status}</Badge>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </div>

          <Card className="flex flex-col justify-center">
            <GaugeChart value={completionRate} title="Weekly Resolution Speed Target" />
          </Card>
        </div>
      </div>
    );
  };

  // 3. Render Staff Dashboard
  const renderStaffDashboard = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fade-in">
      <div className="lg:col-span-2 space-y-8">
        {/* KPI Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <StatisticsWidget title="Unassigned Reports" value={stats?.open_incidents || 0} icon={AlertTriangle} delta="12%" deltaType="down" />
          <StatisticsWidget title="Active dispatches" value={incidents.filter(i => i.status === 'ASSIGNED' || i.status === 'IN_PROGRESS').length} icon={Clock} delta="8%" deltaType="up" />
          <StatisticsWidget title="Total Solved" value={stats?.resolved_incidents || 0} icon={CheckCircle} delta="24%" deltaType="up" />
        </div>

        {/* Triage list */}
        <Card>
          <h3 className="font-display font-bold text-lg text-slate-900 dark:text-white mb-6">High Risk Triage Queue</h3>
          <div className="divide-y divide-slate-100 dark:divide-slate-800/50">
            {incidents.length === 0 ? (
              <p className="text-center py-6 text-slate-400">Triage queue empty.</p>
            ) : (
              incidents.map(inc => (
                <div key={inc.id} className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 first:pt-0 last:pb-0">
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h4 className="font-bold text-sm text-slate-800 dark:text-slate-200">{inc.title}</h4>
                      {inc.risk_score >= 75 && (
                        <Badge colorStyles={{ bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-100' }}>CRITICAL</Badge>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 mt-1">Severity Index: {inc.risk_score?.toFixed(1)} | Category: {CATEGORY_LABELS[inc.category]}</p>
                  </div>
                  {inc.status === 'SUBMITTED' ? (
                    <Button variant="secondary" onClick={() => openAssignModal(inc)} className="px-3 py-1.5 text-xs">
                      <UserPlus className="w-3.5 h-3.5" />
                      <span>Dispatch</span>
                    </Button>
                  ) : (
                    <Badge colorStyles={STATUS_COLORS[inc.status]}>{inc.status}</Badge>
                  )}
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      <div className="space-y-6">
        <Card>
          <h3 className="font-display font-bold text-base text-slate-900 dark:text-white mb-4">Workload Distribution</h3>
          {stats?.category_distribution && (
            <DonutChart
              values={stats.category_distribution.map(d => d.count)}
              labels={stats.category_distribution.map(d => d.category)}
              height={260}
            />
          )}
        </Card>
      </div>
    </div>
  );

  // 4. Render Administrator Dashboard
  const renderAdminDashboard = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fade-in">
      <div className="lg:col-span-2 space-y-8">
        {/* Statistics Widgets */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <StatisticsWidget title="Incident Telemetry" value={stats?.total_incidents || 0} icon={AlertTriangle} delta="12%" deltaType="up" />
          <StatisticsWidget title="Active User base" value={officers.length + 5} icon={Users} delta="5%" deltaType="up" />
          <StatisticsWidget title="Resolution rate" value={`${((stats?.resolved_incidents / (stats?.total_incidents || 1)) * 100).toFixed(0)}%`} icon={CheckCircle} delta="2%" deltaType="up" />
        </div>

        {/* Security logs list */}
        <Card>
          <h3 className="font-display font-bold text-lg text-slate-900 dark:text-white mb-6">Recent Security Event Log</h3>
          <div className="divide-y divide-slate-100 dark:divide-slate-800/50 text-xs">
            <div className="py-2.5 flex justify-between font-bold text-slate-400">
              <span>Event</span>
              <span>IP Address</span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span>USER_LOGIN_SUCCESS (admin@erakshak.gov)</span>
              <span className="font-mono">192.168.1.10</span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span>ASSIGN_INCIDENT (dispatcher@erakshak.gov)</span>
              <span className="font-mono">192.168.1.12</span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span>PROFILE_UPDATE (citizen@gmail.com)</span>
              <span className="font-mono">10.0.2.15</span>
            </div>
          </div>
        </Card>
      </div>

      <div className="space-y-6">
        <SystemHealthPanel health={systemHealth} />
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-display font-bold text-3xl text-slate-900 dark:text-white">Safety Dashboard</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Operational view for {user?.full_name}</p>
        </div>

        <div className="flex items-center gap-3">
          {refreshing && (
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <RefreshCw className="w-3 h-3 animate-spin" />
              Auto-updating...
            </span>
          )}
          <button
            onClick={triggerManualRefresh}
            className="p-2.5 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 rounded-xl transition-all focus-ring"
            title="Refresh statistics data"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Load appropriate role layout */}
      {user?.role === ROLES.CITIZEN && renderCitizenDashboard()}
      {user?.role === ROLES.OFFICER && renderOfficerDashboard()}
      {user?.role === ROLES.STAFF && renderStaffDashboard()}
      {user?.role === ROLES.ADMINISTRATOR && renderAdminDashboard()}

      {/* MODAL 1: Report Incident */}
      <Modal isOpen={reportModalOpen} onClose={() => setReportModalOpen(false)} title="Report New Incident">
        <form onSubmit={handleReportSubmit} className="space-y-5">
          <Input
            label="Incident Title *"
            value={reportForm.title}
            onChange={(e) => setReportForm({ ...reportForm, title: e.target.value })}
            placeholder="Provide a short descriptive summary"
            required
          />

          <Select
            label="Incident Category *"
            value={reportForm.category}
            onChange={(e) => setReportForm({ ...reportForm, category: e.target.value })}
            options={Object.keys(CATEGORY_LABELS).map(key => ({ label: CATEGORY_LABELS[key], value: key }))}
          />

          <Textarea
            label="Incident Description *"
            value={reportForm.description}
            onChange={(e) => setReportForm({ ...reportForm, description: e.target.value })}
            placeholder="Describe the incident in detail (suspect details, weapons involved, damage caused, etc.)"
            required
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Latitude *"
              value={reportForm.latitude}
              onChange={(e) => setReportForm({ ...reportForm, latitude: e.target.value })}
              placeholder="e.g. 28.6139"
              required
            />
            <Input
              label="Longitude *"
              value={reportForm.longitude}
              onChange={(e) => setReportForm({ ...reportForm, longitude: e.target.value })}
              placeholder="e.g. 77.2090"
              required
            />
          </div>

          <FileUpload
            label="Document / Photo Evidence Attachment"
            value={reportForm.attachment}
            onChange={(file) => setReportForm({ ...reportForm, attachment: file })}
          />

          <div className="flex justify-end gap-3 pt-3 border-t border-slate-100 dark:border-slate-800">
            <Button variant="secondary" onClick={() => setReportModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={reportingIncident}>
              File Report
            </Button>
          </div>
        </form>
      </Modal>

      {/* MODAL 2: Dispatch Officer */}
      <Modal isOpen={assignModalOpen} onClose={() => setAssignModalOpen(false)} title="Dispatch Officer">
        <form onSubmit={handleAssignSubmit} className="space-y-5">
          {selectedIncident && (
            <div className="p-4 bg-slate-50 dark:bg-navy-950 rounded-xl border border-slate-100 dark:border-slate-800">
              <h4 className="font-bold text-slate-800 dark:text-slate-200 text-sm">{selectedIncident.title}</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{selectedIncident.description}</p>
              <div className="mt-2 text-xs font-semibold text-rose-500">
                Risk Priority Rating: {selectedIncident.risk_score?.toFixed(1)} / 100.0
              </div>
            </div>
          )}

          <Select
            label="Select Active Field Officer"
            value={selectedOfficerId}
            onChange={(e) => setSelectedOfficerId(e.target.value)}
            options={[
              { label: '-- Select Officer --', value: '' },
              ...officers.map(o => ({ label: `${o.full_name} (${o.email})`, value: o.id }))
            ]}
          />

          <div className="flex justify-end gap-3 pt-3 border-t border-slate-100 dark:border-slate-800">
            <Button variant="secondary" onClick={() => setAssignModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={assigningIncident} disabled={!selectedOfficerId}>
              Dispatch Responder
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
export default Dashboard;
