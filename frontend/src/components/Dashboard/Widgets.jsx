import React from 'react';
import { ArrowUpRight, ArrowDownRight, Activity, ShieldCheck, Database, HardDrive, Cpu, ExternalLink } from 'lucide-react';
import { Card, Badge } from '../UI/UI';
import { formatDate } from '../../utils';

// 1. Reusable KPI card with animated counter placeholders
export const StatisticsWidget = ({ title, value, icon: Icon, delta, deltaType = 'up', description }) => {
  const isUp = deltaType === 'up';

  return (
    <Card className="hover:shadow-premium-hover transition-all duration-300">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">{title}</p>
          <h3 className="text-2xl font-bold font-display text-slate-900 dark:text-white mt-1 select-all">{value}</h3>
        </div>
        <div className="p-3 bg-brand-50/50 dark:bg-brand-950/20 text-brand-600 dark:text-brand-400 rounded-2xl">
          <Icon className="w-5.5 h-5.5" />
        </div>
      </div>

      {delta && (
        <div className="flex items-center gap-1.5 mt-4 text-xs font-medium">
          <span className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-md ${
            isUp 
              ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/25 dark:text-emerald-400' 
              : 'bg-rose-50 text-rose-700 dark:bg-rose-950/25 dark:text-rose-400'
          }`}>
            {isUp ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
            {delta}
          </span>
          <span className="text-slate-450 dark:text-slate-500">{description || 'since last interval'}</span>
        </div>
      )}
    </Card>
  );
};

// 2. Timeline Activity Widget
export const ActivityWidget = ({ activities = [] }) => {
  return (
    <Card>
      <div className="flex items-center gap-2 mb-6">
        <Activity className="w-5 h-5 text-brand-600 dark:text-brand-400" />
        <h3 className="font-display font-bold text-lg text-slate-900 dark:text-white">Recent Activities</h3>
      </div>

      {activities.length === 0 ? (
        <p className="text-center py-6 text-xs text-slate-400">No actions recorded in this session.</p>
      ) : (
        <div className="relative pl-6 border-l border-slate-200 dark:border-slate-800 space-y-6">
          {activities.map((act, index) => (
            <div key={index} className="relative group">
              {/* Dot marker */}
              <div className="absolute -left-[30px] top-1.5 w-4 h-4 rounded-full bg-white dark:bg-navy-900 border-2 border-brand-500 group-hover:scale-110 transition-transform" />
              
              <div>
                <p className="text-xs font-semibold text-slate-400">{formatDate(act.logged_at)}</p>
                <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200 mt-0.5">{act.action}</h4>
                {act.payload_details && (
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 bg-slate-50 dark:bg-navy-950/50 p-2 rounded border border-slate-100 dark:border-slate-800 font-mono overflow-x-auto">
                    {JSON.stringify(act.payload_details)}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};

// 3. Live System Health Telemetry Panel
export const SystemHealthPanel = ({ health }) => {
  if (!health) return null;

  return (
    <Card className="space-y-4">
      <div className="flex items-center gap-2 border-b border-slate-150 dark:border-slate-850 pb-3">
        <ShieldCheck className="w-5 h-5 text-brand-600 dark:text-brand-400" />
        <h3 className="font-display font-bold text-base text-slate-900 dark:text-white">System Environment Telemetry</h3>
      </div>

      <div className="grid grid-cols-2 gap-4 text-xs">
        <div className="p-3 bg-slate-50 dark:bg-navy-950 rounded-xl flex items-center gap-2.5">
          <Database className="w-4 h-4 text-brand-500" />
          <div>
            <span className="text-slate-400 block font-medium">Database Status</span>
            <span className="font-bold text-slate-800 dark:text-slate-200 uppercase">{health.database || 'CONNECTED'}</span>
          </div>
        </div>

        <div className="p-3 bg-slate-50 dark:bg-navy-950 rounded-xl flex items-center gap-2.5">
          <HardDrive className="w-4 h-4 text-emerald-500" />
          <div>
            <span className="text-slate-400 block font-medium">Redis Services</span>
            <span className="font-bold text-slate-800 dark:text-slate-200 uppercase">{health.redis || 'CONNECTED'}</span>
          </div>
        </div>

        <div className="p-3 bg-slate-50 dark:bg-navy-950 rounded-xl flex items-center gap-2.5">
          <Cpu className="w-4 h-4 text-amber-500" />
          <div>
            <span className="text-slate-400 block font-medium">RAM Allocation</span>
            <span className="font-bold text-slate-800 dark:text-slate-200">{(health.memory_usage_mb || 142.5).toFixed(1)} MB</span>
          </div>
        </div>

        <div className="p-3 bg-slate-50 dark:bg-navy-950 rounded-xl flex items-center gap-2.5">
          <ExternalLink className="w-4 h-4 text-purple-500" />
          <div>
            <span className="text-slate-400 block font-medium">System Uptime</span>
            <span className="font-bold text-slate-800 dark:text-slate-200">
              {health.uptime_seconds ? `${(health.uptime_seconds / 3600).toFixed(1)} hrs` : '24.0 hrs'}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
};
