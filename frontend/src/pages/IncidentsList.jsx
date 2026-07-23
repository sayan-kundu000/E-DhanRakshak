import React, { useState, useEffect } from 'react';
import { Search, Eye, CheckCircle2, XCircle, UserCheck, Trash2, ShieldAlert } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import api from '../api/axios';
import { Card, Button, Badge, Table, Modal } from '../components/UI/UI';
import { Input, Select } from '../components/UI/FormComponents';
import { STATUS_COLORS, CATEGORY_LABELS, ROLES, INCIDENT_STATUSES, ASSIGNMENT_STATUSES } from '../constants';
import { formatDate } from '../utils';

export const IncidentsList = () => {
  const { user, hasRole } = useAuth();
  const { success, error, warning } = useNotification();
  const [incidents, setIncidents] = useState([]);
  const [officers, setOfficers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  
  // Selected Incident Inspection
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const [submittingAction, setSubmittingAction] = useState(false);
  
  // Officer response form state
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectForm, setShowRejectForm] = useState(false);

  useEffect(() => {
    fetchIncidents();
    if (hasRole([ROLES.ADMINISTRATOR, ROLES.STAFF])) {
      fetchOfficers();
    }
  }, [categoryFilter, statusFilter]);

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      // Construct query string params
      const params = {};
      if (statusFilter) params.status = statusFilter;
      if (categoryFilter) params.category = categoryFilter;
      
      const response = await api.get('/incidents', { params });
      if (response.data && response.data.success) {
        setIncidents(response.data.data);
      }
    } catch (e) {
      console.error(e);
      warning('Failed to query active database. Serving mock cache.');
    } finally {
      setLoading(false);
    }
  };

  const fetchOfficers = async () => {
    try {
      const response = await api.get('/admin/users');
      if (response.data && response.data.success) {
        setOfficers(response.data.data.filter(u => u.role === ROLES.OFFICER && u.is_active));
      }
    } catch (e) {
      console.warn('Could not retrieve active officers list.');
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const params = { q: searchTerm };
      if (statusFilter) params.status = statusFilter;
      if (categoryFilter) params.category = categoryFilter;
      
      const response = await api.get('/search/incidents', { params });
      if (response.data && response.data.success) {
        setIncidents(response.data.data);
      }
    } catch (e) {
      console.error(e);
      error('Search query failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleInspect = async (id) => {
    try {
      const response = await api.get(`/incidents/${id}`);
      if (response.data && response.data.success) {
        setSelectedIncident(response.data.data);
        setInspectorOpen(true);
        setShowRejectForm(false);
        setRejectReason('');
      }
    } catch (e) {
      error('Could not fetch incident details.');
    }
  };

  const handleOfficerAction = async (status, reason = '') => {
    if (!selectedIncident || !selectedIncident.assignment) return;
    
    setSubmittingAction(true);
    try {
      const res = await api.put(`/assignments/${selectedIncident.assignment.id}/status`, {
        status,
        rejection_reason: reason,
      });

      if (res.data && res.data.success) {
        success(`Assignment status updated to ${status}!`);
        setInspectorOpen(false);
        fetchIncidents();
      }
    } catch (err) {
      error(err.response?.data?.error?.message || 'Action update failed.');
    } finally {
      setSubmittingAction(false);
    }
  };

  const handleAutoAssign = async (incidentId) => {
    setSubmittingAction(true);
    try {
      const res = await api.post(`/incidents/${incidentId}/auto-assign`);
      if (res.data && res.data.success) {
        success('Spatial auto-assignment completed successfully!');
        setInspectorOpen(false);
        fetchIncidents();
      }
    } catch (err) {
      error(err.response?.data?.error?.message || 'Auto-assignment mapping failed.');
    } finally {
      setSubmittingAction(false);
    }
  };

  const handleDeleteIncident = async (id) => {
    if (!window.confirm('Are you sure you want to logically delete this incident report?')) return;
    
    setSubmittingAction(true);
    try {
      await api.delete(`/incidents/${id}`);
      success('Incident report logically soft deleted.');
      setInspectorOpen(false);
      fetchIncidents();
    } catch (err) {
      error('Failed to delete resource.');
    } finally {
      setSubmittingAction(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h1 className="font-display font-bold text-3xl text-slate-900 dark:text-white">Incidents Directory</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Audit safety logs and resolve field dispatches</p>
      </div>

      {/* Filter and Search Bar */}
      <Card className="py-4">
        <form onSubmit={handleSearch} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          <div className="md:col-span-2">
            <Input
              label="Keywords Query"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by title, location details..."
            />
          </div>

          <Select
            label="Category"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            options={[
              { label: 'All Categories', value: '' },
              ...Object.keys(CATEGORY_LABELS).map(k => ({ label: CATEGORY_LABELS[k], value: k }))
            ]}
          />

          <Select
            label="Status"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            options={[
              { label: 'All Statuses', value: '' },
              ...Object.keys(INCIDENT_STATUSES).map(k => ({ label: k, value: k }))
            ]}
          />
        </form>
      </Card>

      {/* Grid List / Table */}
      {loading ? (
        <div className="flex flex-col items-center justify-center min-h-[300px]">
          <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-3 text-sm text-slate-500">Retrieving records from repository...</p>
        </div>
      ) : incidents.length === 0 ? (
        <Card className="text-center py-12 text-slate-400">
          No records match the requested search query filters.
        </Card>
      ) : (
        <Table headers={['Title', 'Category', 'Risk Index', 'Status', 'Date Logged', 'Dispatch Action']}>
          {incidents.map((inc) => (
            <tr key={inc.id} className="hover:bg-slate-50/50 dark:hover:bg-navy-950/20 transition-colors">
              <td className="px-6 py-4 font-semibold text-slate-800 dark:text-slate-200">{inc.title}</td>
              <td className="px-6 py-4 text-xs font-semibold">{CATEGORY_LABELS[inc.category] || inc.category}</td>
              <td className="px-6 py-4">
                {inc.risk_score ? (
                  <span className={`font-semibold text-sm ${inc.risk_score >= 75 ? 'text-rose-500' : 'text-amber-500'}`}>
                    {inc.risk_score.toFixed(1)}
                  </span>
                ) : 'N/A'}
              </td>
              <td className="px-6 py-4">
                <Badge colorStyles={STATUS_COLORS[inc.status]}>{inc.status}</Badge>
              </td>
              <td className="px-6 py-4 text-xs text-slate-500 dark:text-slate-400">{formatDate(inc.created_at)}</td>
              <td className="px-6 py-4">
                <Button variant="ghost" onClick={() => handleInspect(inc.id)} className="p-1 text-brand-600 dark:text-brand-400">
                  <Eye className="w-5 h-5" />
                </Button>
              </td>
            </tr>
          ))}
        </Table>
      )}

      {/* INSPECTOR MODAL */}
      <Modal isOpen={inspectorOpen} onClose={() => setInspectorOpen(false)} title="Incident Inspector" maxWidthClass="max-w-2xl">
        {selectedIncident && (
          <div className="space-y-6">
            {/* Header info */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Badge colorStyles={STATUS_COLORS[selectedIncident.status]}>{selectedIncident.status}</Badge>
                <span className="text-xs text-slate-400">ID: {selectedIncident.id}</span>
              </div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white font-display">{selectedIncident.title}</h2>
            </div>

            {/* Description & Metadata */}
            <div className="space-y-4">
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Report Description</h4>
                <p className="text-sm text-slate-700 dark:text-slate-300 mt-1 bg-slate-50 dark:bg-navy-950 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
                  {selectedIncident.description}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="font-bold text-slate-400">Category:</span>
                  <p className="text-slate-700 dark:text-slate-300 mt-0.5">{CATEGORY_LABELS[selectedIncident.category]}</p>
                </div>
                <div>
                  <span className="font-bold text-slate-400">Report Date:</span>
                  <p className="text-slate-700 dark:text-slate-300 mt-0.5">{formatDate(selectedIncident.created_at)}</p>
                </div>
                <div>
                  <span className="font-bold text-slate-400">Geospatial Coordinates:</span>
                  <p className="text-slate-700 dark:text-slate-300 mt-0.5">{selectedIncident.latitude}, {selectedIncident.longitude}</p>
                </div>
                <div>
                  <span className="font-bold text-slate-400">Reporter User ID:</span>
                  <p className="text-slate-700 dark:text-slate-300 mt-0.5 truncate">{selectedIncident.reporter_id}</p>
                </div>
              </div>
            </div>

            {/* Risk calculations */}
            {selectedIncident.risk_score && (
              <div className="p-4 rounded-2xl bg-rose-500/5 dark:bg-rose-500/10 border border-rose-500/20">
                <div className="flex items-center gap-2 text-rose-600 dark:text-rose-400 mb-2">
                  <ShieldAlert className="w-5 h-5" />
                  <h4 className="font-bold text-sm">Predictive Risk Scoring Breakdown</h4>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-extrabold text-rose-600 dark:text-rose-450 font-display">{selectedIncident.risk_score.toFixed(1)}</span>
                  <span className="text-xs text-rose-500/80">/ 100.0 (High Priority bounds)</span>
                </div>
              </div>
            )}

            {/* Assignment Status details */}
            {selectedIncident.assignment && (
              <div className="p-4 rounded-2xl bg-brand-500/5 border border-brand-500/25">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Assigned Responder Details</h4>
                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="font-bold text-slate-500">Field Responder:</span>
                    <p className="text-slate-800 dark:text-slate-200 font-semibold">{selectedIncident.assignment.officer_name || 'Inspector'}</p>
                  </div>
                  <div>
                    <span className="font-bold text-slate-500">Dispatch Assigned:</span>
                    <p className="text-slate-850 dark:text-slate-350">{formatDate(selectedIncident.assignment.assigned_at)}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Operational Actions */}
            <div className="flex flex-wrap gap-3 pt-4 border-t border-slate-100 dark:border-slate-800 justify-end">
              {/* CITIZEN cancellation rights */}
              {user.role === ROLES.CITIZEN && selectedIncident.status === 'SUBMITTED' && (
                <Button variant="danger" onClick={() => handleDeleteIncident(selectedIncident.id)} loading={submittingAction}>
                  <Trash2 className="w-4 h-4" />
                  <span>Withdraw Report</span>
                </Button>
              )}

              {/* OFFICER responding workflows */}
              {user.role === ROLES.OFFICER && selectedIncident.assignment && (
                <>
                  {selectedIncident.status === 'ASSIGNED' && !showRejectForm && (
                    <>
                      <Button variant="danger" onClick={() => setShowRejectForm(true)} className="px-4 py-2">
                        Reject Call
                      </Button>
                      <Button variant="primary" onClick={() => handleOfficerAction(ASSIGNMENT_STATUSES.ACCEPTED)} loading={submittingAction}>
                        Accept Incident Call
                      </Button>
                    </>
                  )}
                  
                  {selectedIncident.status === 'IN_PROGRESS' && (
                    <Button variant="primary" onClick={() => handleOfficerAction(ASSIGNMENT_STATUSES.RESOLVED)} loading={submittingAction}>
                      <CheckCircle2 className="w-4.5 h-4.5" />
                      <span>Mark Solved & Upload Log</span>
                    </Button>
                  )}
                </>
              )}

              {/* STAFF/ADMIN worklist triggers */}
              {hasRole([ROLES.ADMINISTRATOR, ROLES.STAFF]) && selectedIncident.status === 'SUBMITTED' && (
                <Button variant="primary" onClick={() => handleAutoAssign(selectedIncident.id)} loading={submittingAction}>
                  <UserCheck className="w-4.5 h-4.5" />
                  <span>Trigger Auto-Assign Model</span>
                </Button>
              )}

              {/* Rejection Form fields rendering */}
              {showRejectForm && (
                <div className="w-full space-y-3 mt-4 border-t border-slate-100 dark:border-slate-800 pt-4 text-left">
                  <Input
                    label="Provide Rejection Reason"
                    value={rejectReason}
                    onChange={(e) => setRejectReason(e.target.value)}
                    placeholder="e.g. Officer out of grid, vehicle malfunction"
                  />
                  <div className="flex gap-2 justify-end">
                    <Button variant="secondary" onClick={() => setShowRejectForm(false)}>Cancel</Button>
                    <Button variant="danger" onClick={() => handleOfficerAction(ASSIGNMENT_STATUSES.REJECTED, rejectReason)} disabled={!rejectReason} loading={submittingAction}>
                      Submit Rejection
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
export default IncidentsList;
