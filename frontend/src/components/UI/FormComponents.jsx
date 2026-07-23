import React from 'react';

export const Input = React.forwardRef(({ label, error, type = 'text', ...props }, ref) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
          {label}
        </label>
      )}
      <input
        ref={ref}
        type={type}
        className={`w-full px-4 py-2.5 bg-slate-50 dark:bg-navy-950 border rounded-xl text-slate-900 dark:text-slate-100 transition-all focus-ring ${
          error
            ? 'border-rose-500 focus-visible:ring-rose-500'
            : 'border-slate-200 dark:border-slate-800 focus-visible:ring-brand-500 hover:border-slate-300 dark:hover:border-slate-700'
        }`}
        {...props}
      />
      {error && <span className="block text-xs font-medium text-rose-500 mt-1">{error}</span>}
    </div>
  );
});

Input.displayName = 'Input';

export const Select = React.forwardRef(({ label, error, options = [], ...props }, ref) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
          {label}
        </label>
      )}
      <select
        ref={ref}
        className={`w-full px-4 py-2.5 bg-slate-50 dark:bg-navy-950 border rounded-xl text-slate-900 dark:text-slate-100 transition-all focus-ring appearance-none ${
          error
            ? 'border-rose-500 focus-visible:ring-rose-500'
            : 'border-slate-200 dark:border-slate-800 focus-visible:ring-brand-500 hover:border-slate-300 dark:hover:border-slate-700'
        }`}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <span className="block text-xs font-medium text-rose-500 mt-1">{error}</span>}
    </div>
  );
});

Select.displayName = 'Select';

export const Textarea = React.forwardRef(({ label, error, rows = 4, ...props }, ref) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
          {label}
        </label>
      )}
      <textarea
        ref={ref}
        rows={rows}
        className={`w-full px-4 py-2.5 bg-slate-50 dark:bg-navy-950 border rounded-xl text-slate-900 dark:text-slate-100 transition-all focus-ring ${
          error
            ? 'border-rose-500 focus-visible:ring-rose-500'
            : 'border-slate-200 dark:border-slate-800 focus-visible:ring-brand-500 hover:border-slate-300 dark:hover:border-slate-700'
        }`}
        {...props}
      />
      {error && <span className="block text-xs font-medium text-rose-500 mt-1">{error}</span>}
    </div>
  );
});

Textarea.displayName = 'Textarea';

export const Checkbox = React.forwardRef(({ label, error, ...props }, ref) => {
  return (
    <div className="w-full">
      <label className="inline-flex items-center gap-3 cursor-pointer">
        <input
          type="checkbox"
          ref={ref}
          className="w-4.5 h-4.5 rounded border-slate-300 dark:border-slate-800 text-brand-600 focus:ring-brand-500 dark:focus:ring-offset-navy-950 bg-slate-50 dark:bg-navy-950 cursor-pointer"
          {...props}
        />
        {label && (
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300 select-none">
            {label}
          </span>
        )}
      </label>
      {error && <span className="block text-xs font-medium text-rose-500 mt-1">{error}</span>}
    </div>
  );
});

Checkbox.displayName = 'Checkbox';
