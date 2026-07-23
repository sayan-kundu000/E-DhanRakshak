import React, { useState, useRef } from 'react';
import { UploadCloud, File, AlertCircle, CheckCircle2, Trash2, XCircle } from 'lucide-react';

export const FileUpload = ({ label, error, onChange, value, maxSizeMB = 5 }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [fileError, setFileError] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const processFile = (file) => {
    setFileError(null);
    if (!file) return;

    // Validation checks
    const sizeInMB = file.size / (1024 * 1024);
    if (sizeInMB > maxSizeMB) {
      setFileError(`File size exceeds the ${maxSizeMB}MB safety limit.`);
      return;
    }

    // Start upload progress simulation
    setUploading(true);
    setProgress(0);
    
    let currentProgress = 0;
    const interval = setInterval(() => {
      currentProgress += 10;
      setProgress(currentProgress);
      if (currentProgress >= 100) {
        clearInterval(interval);
        setUploading(false);
        // Bind URL string or file object back to form state hook
        onChange && onChange(file);
      }
    }, 150);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const handleRemove = (e) => {
    e.stopPropagation();
    onChange && onChange(null);
    setProgress(0);
    setFileError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="w-full">
      {label && (
        <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
          {label}
        </label>
      )}

      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[160px] ${
          dragActive
            ? 'border-brand-500 bg-brand-50/30 dark:bg-brand-950/20'
            : 'border-slate-200 dark:border-slate-800 hover:border-brand-400 hover:bg-slate-50/50 dark:hover:bg-navy-950/30'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={handleFileChange}
          accept="image/*,application/pdf"
        />

        {!value && !uploading && (
          <>
            <UploadCloud className="w-10 h-10 text-slate-400 dark:text-slate-600 mb-3" />
            <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
              Drag & Drop file here or <span className="text-brand-600 dark:text-brand-400">Browse</span>
            </p>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Supports Images, PDFs up to 5MB</p>
          </>
        )}

        {uploading && (
          <div className="w-full max-w-[200px] flex flex-col items-center">
            <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mb-3"></div>
            <p className="text-xs font-medium text-slate-600 dark:text-slate-400">Uploading attachment ({progress}%)</p>
            <div className="w-full bg-slate-200 dark:bg-slate-800 h-1 rounded-full mt-2 overflow-hidden">
              <div className="bg-brand-500 h-1 transition-all duration-150" style={{ width: `${progress}%` }}></div>
            </div>
          </div>
        )}

        {value && !uploading && (
          <div className="flex items-center gap-3 p-3 bg-slate-100 dark:bg-navy-950/80 rounded-xl w-full text-left border border-slate-200/50 dark:border-slate-800/50">
            <File className="w-8 h-8 text-brand-600 dark:text-brand-400 flex-shrink-0" />
            <div className="flex-grow min-w-0">
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate">
                {value.name || 'attachment_file.pdf'}
              </p>
              <p className="text-xs text-slate-400 dark:text-slate-500">
                {value.size ? `${(value.size / 1024).toFixed(1)} KB` : 'Uploaded'}
              </p>
            </div>
            <button
              onClick={handleRemove}
              className="p-2 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/20 rounded-lg transition-colors focus-ring"
              title="Remove attachment"
            >
              <Trash2 className="w-4.5 h-4.5" />
            </button>
          </div>
        )}
      </div>

      {(fileError || error) && (
        <div className="flex items-center gap-1.5 text-xs font-medium text-rose-500 mt-1.5">
          <AlertCircle className="w-3.5 h-3.5" />
          <span>{fileError || error}</span>
        </div>
      )}
    </div>
  );
};
