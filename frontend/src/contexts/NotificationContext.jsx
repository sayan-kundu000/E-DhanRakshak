import React, { createContext, useContext, useState } from 'react';
import toast, { Toaster } from 'react-hot-toast';

const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
  const [confirmDialog, setConfirmDialog] = useState(null);

  const showSuccess = (msg) => toast.success(msg);
  const showError = (msg) => toast.error(msg);
  const showInfo = (msg) => toast(msg, { icon: 'ℹ️' });
  const showWarning = (msg) => toast(msg, { icon: '⚠️' });
  
  const showPromise = (promise, messages = { loading: 'Processing...', success: 'Success!', error: 'Failed.' }) => {
    return toast.promise(promise, messages);
  };

  const confirm = ({ title, message, onConfirm, onCancel }) => {
    setConfirmDialog({
      title,
      message,
      onConfirm: () => {
        onConfirm && onConfirm();
        setConfirmDialog(null);
      },
      onCancel: () => {
        onCancel && onCancel();
        setConfirmDialog(null);
      }
    });
  };

  return (
    <NotificationContext.Provider
      value={{
        success: showSuccess,
        error: showError,
        info: showInfo,
        warning: showWarning,
        promise: showPromise,
        confirm,
      }}
    >
      {children}
      <Toaster position="top-right" toastOptions={{ duration: 4000 }} />
      
      {/* Confirmation Dialog Overlay */}
      {confirmDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-md overflow-hidden bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xl">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 font-display">{confirmDialog.title}</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{confirmDialog.message}</p>
            </div>
            <div className="flex justify-end gap-3 px-6 py-4 bg-slate-50 dark:bg-navy-950 border-t border-slate-100 dark:border-slate-800">
              <button
                onClick={confirmDialog.onCancel}
                className="px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors focus-ring"
              >
                Cancel
              </button>
              <button
                onClick={confirmDialog.onConfirm}
                className="px-4 py-2 text-sm font-medium text-white bg-rose-600 hover:bg-rose-700 rounded-lg transition-colors focus-ring"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </NotificationContext.Provider>
  );
};

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) throw new Error('useNotification must be used within a NotificationProvider');
  return context;
};
