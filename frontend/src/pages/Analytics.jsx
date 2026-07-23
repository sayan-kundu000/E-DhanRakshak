import React, { useState, useEffect } from 'react';
import { Compass, Download, ShieldAlert, Cpu, BarChart3 } from 'lucide-react';
import { useNotification } from '../contexts/NotificationContext';
import { useAnalytics } from '../contexts/AnalyticsContext';
import api from '../api/axios';

// Reusable Components
import { Card, Button, Badge } from '../components/UI/UI';
import { Input, Select } from '../components/UI/FormComponents';
import { LineChart, BarChart } from '../components/Charts/ChartLibrary';
import { InteractiveFilters } from '../components/Dashboard/Filters';

// Constants & Utils
import { CATEGORY_LABELS } from '../constants';
import { downloadBlob } from '../utils';

export const Analytics = () => {
  const { success, error, warning } = useNotification();
  const { trends, filters, loading, refreshTrends } = useAnalytics();

  // Prediction Tool Form state
  const [predForm, setPredForm] = useState({
    category: 'THEFT',
    latitude: '28.6139',
    longitude: '77.2090',
  });
  const [prediction, setPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);

  // Export state
  const [exportInterval, setExportInterval] = useState('weekly');
  const [exporting, setExporting] = useState(false);

  const handlePredict = async (e) => {
    e.preventDefault();
    setPredicting(true);
    setPrediction(null);
    try {
      const params = {
        category: predForm.category,
        latitude: parseFloat(predForm.latitude),
        longitude: parseFloat(predForm.longitude),
      };
      
      const response = await api.get('/analytics/prediction', { params });
      if (response.data && response.data.success) {
        setPrediction(response.data.data);
        success('ML priority prediction compiled!');
      }
    } catch (err) {
      error('Prediction calculation failed.');
    } finally {
      setPredicting(false);
    }
  };

  const handleExport = async (format) => {
    setExporting(true);
    try {
      const response = await api.get('/reports/export', {
        params: { interval: exportInterval, format },
        responseType: format === 'json' ? 'json' : 'blob',
      });

      if (format === 'json') {
        const jsonString = JSON.stringify(response.data, null, 2);
        downloadBlob(jsonString, `report_${exportInterval}.json`, 'application/json');
      } else {
        const fileType = format === 'csv' ? 'text/csv' : 'application/pdf';
        downloadBlob(response.data, `report_${exportInterval}.${format}`, fileType);
      }
      success(`Exported ${format.toUpperCase()} report successfully!`);
    } catch (err) {
      error('Failed to export reports.');
    } finally {
      setExporting(false);
    }
  };

  const handleSearchSubmit = () => {
    refreshTrends();
  };

  if (loading && !trends) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <div className="w-12 h-12 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="mt-4 text-sm font-medium text-slate-500">Compiling historical charts...</p>
      </div>
    );
  }

  // Get trend data safely from state, fallback to mock if null
  const chartDays = trends?.days || ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const chartCounts = trends?.counts || [12, 19, 3, 5, 2, 3, 9];

  return (
    <div className="space-y-8">
      {/* Title */}
      <div>
        <h1 className="font-display font-bold text-3xl text-slate-900 dark:text-white">Analytics & Intelligence</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Machine Learning incident prioritizations and statistical auditing logs</p>
      </div>

      {/* Cross Filtering Search panel */}
      <InteractiveFilters onSearchSubmit={handleSearchSubmit} />

      {/* Grid: Trend Plotly Chart & Export Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card className="lg:col-span-2">
          <LineChart x={chartDays} y={chartCounts} title="7-Day Rolling Incident Activity" />
        </Card>

        {/* Report Exports */}
        <Card className="flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5 text-brand-600 dark:text-brand-400" />
              <h3 className="font-display font-bold text-lg text-slate-900 dark:text-white">Export Operations</h3>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
              Download CSV summaries or PDF logs of community safety incidents over chosen reporting intervals.
            </p>

            <Select
              label="Select Auditing Interval"
              value={exportInterval}
              onChange={(e) => setExportInterval(e.target.value)}
              options={[
                { label: 'Weekly Summary', value: 'weekly' },
                { label: 'Monthly Summary', value: 'monthly' },
                { label: 'Quarterly Summary', value: 'quarterly' },
              ]}
            />
          </div>

          <div className="grid grid-cols-2 gap-3 mt-6">
            <Button variant="secondary" onClick={() => handleExport('csv')} disabled={exporting} className="w-full">
              <Download className="w-4 h-4" />
              <span>CSV Sheet</span>
            </Button>
            <Button variant="primary" onClick={() => handleExport('pdf')} disabled={exporting} className="w-full">
              <Download className="w-4 h-4" />
              <span>PDF Report</span>
            </Button>
          </div>
        </Card>
      </div>

      {/* Predictive Modeling Simulator (Interactive) */}
      <Card className="max-w-3xl">
        <div className="flex items-center gap-3 mb-6">
          <Cpu className="w-6 h-6 text-rose-500" />
          <div>
            <h3 className="font-display font-bold text-lg text-slate-900 dark:text-white">Predictive Risk Scoring Inference</h3>
            <p className="text-xs text-slate-400 mt-0.5">Hypothetical model simulator for incident prioritization triage</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
          {/* Inputs Form */}
          <form onSubmit={handlePredict} className="space-y-4">
            <Select
              label="Incident Category"
              value={predForm.category}
              onChange={(e) => setPredForm({ ...predForm, category: e.target.value })}
              options={Object.keys(CATEGORY_LABELS).map(key => ({ label: CATEGORY_LABELS[key], value: key }))}
            />

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Latitude"
                value={predForm.latitude}
                onChange={(e) => setPredForm({ ...predForm, latitude: e.target.value })}
              />
              <Input
                label="Longitude"
                value={predForm.longitude}
                onChange={(e) => setPredForm({ ...predForm, longitude: e.target.value })}
              />
            </div>

            <Button type="submit" loading={predicting} className="w-full">
              Run Inference
            </Button>
          </form>

          {/* Outputs display */}
          <div className="h-full flex flex-col justify-center">
            {prediction ? (
              <div className="p-5 rounded-2xl bg-rose-500/5 border border-rose-500/20 text-center space-y-4 animate-scale-up">
                <ShieldAlert className="w-10 h-10 text-rose-500 mx-auto" />
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Estimated Risk Index</p>
                  <h4 className="text-4xl font-extrabold text-rose-600 dark:text-rose-450 font-display mt-1">
                    {prediction.risk_score?.toFixed(1) || '82.5'}
                  </h4>
                </div>
                <div className="text-xs text-slate-500 dark:text-slate-400 space-y-1">
                  <p>Severity Coeff: {prediction.factors?.category_severity || '8.5'}/10</p>
                  <p>Calculated: {new Date().toLocaleTimeString()}</p>
                </div>
              </div>
            ) : (
              <div className="border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl p-8 text-center text-slate-400">
                Submit inputs on the left to trigger the multi-factor weighted predictive ML risk scorer.
              </div>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};
export default Analytics;
