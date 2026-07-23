import React from 'react';
import { Search, RotateCcw, Filter } from 'lucide-react';
import { useAnalytics } from '../../contexts/AnalyticsContext';
import { Input, Select } from '../UI/FormComponents';
import { Button } from '../UI/UI';
import { CATEGORY_LABELS, INCIDENT_STATUSES } from '../../constants';

export const InteractiveFilters = ({ onSearchSubmit }) => {
  const { filters, updateFilters, resetFilters } = useAnalytics();

  const handleClear = () => {
    resetFilters();
  };

  return (
    <div className="bg-white dark:bg-navy-900 border border-slate-200/50 dark:border-slate-800/50 rounded-2xl p-4 shadow-sm space-y-4">
      <div className="flex items-center gap-2 border-b border-slate-100 dark:border-slate-850 pb-2">
        <Filter className="w-4.5 h-4.5 text-brand-600 dark:text-brand-400" />
        <h4 className="font-display font-semibold text-sm text-slate-850 dark:text-slate-200">Refine Results</h4>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSearchSubmit && onSearchSubmit(filters);
        }}
        className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4 items-end"
      >
        <div className="sm:col-span-2">
          <Input
            label="Search Keywords"
            value={filters.q}
            onChange={(e) => updateFilters({ q: e.target.value })}
            placeholder="Type incident keywords..."
          />
        </div>

        <Select
          label="Category Filter"
          value={filters.category}
          onChange={(e) => updateFilters({ category: e.target.value })}
          options={[
            { label: 'All Categories', value: '' },
            ...Object.keys(CATEGORY_LABELS).map((k) => ({ label: CATEGORY_LABELS[k], value: k })),
          ]}
        />

        <Select
          label="Status Filter"
          value={filters.status}
          onChange={(e) => updateFilters({ status: e.target.value })}
          options={[
            { label: 'All Statuses', value: '' },
            ...Object.keys(INCIDENT_STATUSES).map((k) => ({ label: k, value: k })),
          ]}
        />

        <div className="flex gap-2">
          <Button type="submit" variant="primary" className="flex-grow py-2.5">
            <Search className="w-4 h-4" />
            <span>Search</span>
          </Button>
          <Button type="button" variant="secondary" onClick={handleClear} className="px-3 py-2.5" title="Reset Filters">
            <RotateCcw className="w-4 h-4" />
          </Button>
        </div>
      </form>
    </div>
  );
};
export default InteractiveFilters;
