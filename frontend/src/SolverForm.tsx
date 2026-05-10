import React, { useState } from 'react';

const SolverForm: React.FC = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      setFile(files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <div className="solver-form-container card">
      <div className="form-header">
        <h2>Upload Your Network</h2>
        <p>Drag and drop your .inp file here to begin the optimization process.</p>
      </div>

      <div 
        className={`upload-zone ${isDragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <span className="material-symbols-outlined upload-icon">
          {file ? 'check_circle' : 'cloud_upload'}
        </span>
        <div className="upload-text">
          {file ? (
            <>
              <p className="file-name">{file.name}</p>
              <p className="file-status">File validated. Ready to optimize.</p>
            </>
          ) : (
            <>
              <p className="primary-text">Select a file or drag and drop here</p>
              <p className="secondary-text">EPANET .inp files up to 50MB</p>
            </>
          )}
        </div>
        {!file && (
          <label className="btn-browse">
            Browse Files
            <input type="file" hidden onChange={handleFileChange} accept=".inp" />
          </label>
        )}
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <span className="material-symbols-outlined metric-icon">speed</span>
          <div className="metric-label">Pressure</div>
          <div className="metric-value">10 - 80m</div>
        </div>
        <div className="metric-card">
          <span className="material-symbols-outlined metric-icon">water_drop</span>
          <div className="metric-label">Velocity</div>
          <div className="metric-value">0.3 - 2.5 m/s</div>
        </div>
        <div className="metric-card">
          <span className="material-symbols-outlined metric-icon">timeline</span>
          <div className="metric-label">Headloss</div>
          <div className="metric-value">Max 10 m/km</div>
        </div>
      </div>

      <div className="form-actions">
        <button className="btn-primary" disabled={!file}>
          Start Optimization
          <span className="material-symbols-outlined">arrow_forward</span>
        </button>
      </div>

      <style>{`
        .solver-form-container {
          max-width: 800px;
          width: 100%;
          display: flex;
          flex-direction: column;
          gap: 32px;
          animation: fadeIn 0.5s ease-out;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .form-header {
          text-align: center;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .upload-zone {
          border: 2px dashed var(--outline-variant);
          border-radius: var(--rounded-lg);
          padding: 48px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16px;
          transition: all 0.3s ease;
          cursor: pointer;
          min-height: 280px;
          justify-content: center;
          position: relative;
        }

        .upload-zone.dragging {
          border-color: var(--primary);
          background-color: var(--primary-container);
          opacity: 0.1;
        }

        .upload-zone.has-file {
          border-style: solid;
          border-color: var(--secondary);
          background-color: rgba(16, 185, 129, 0.05);
        }

        .upload-icon {
          font-size: 64px;
          color: var(--outline-variant);
          font-variation-settings: 'wght' 200;
        }

        .has-file .upload-icon {
          color: var(--secondary);
        }

        .upload-text {
          text-align: center;
        }

        .upload-text .primary-text {
          font-size: 24px;
          font-weight: 600;
          color: var(--on-surface);
        }

        .upload-text .secondary-text {
          font-size: 15px;
          color: var(--on-surface-variant);
        }

        .file-name {
          font-size: 20px;
          font-weight: 600;
          color: var(--on-surface);
        }

        .file-status {
          color: var(--secondary);
          font-weight: 500;
        }

        .btn-browse {
          background-color: var(--surface-container);
          color: var(--on-surface);
          padding: 12px 24px;
          border-radius: var(--rounded-md);
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .btn-browse:hover {
          background-color: var(--surface-container-high);
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 16px;
        }

        .metric-card {
          background-color: var(--surface-container-low);
          padding: 16px;
          border-radius: var(--rounded-md);
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
        }

        .metric-icon {
          color: var(--secondary);
          font-size: 32px;
        }

        .metric-label {
          font-size: 13px;
          font-weight: 700;
          color: var(--on-surface);
        }

        .metric-value {
          font-size: 15px;
          color: var(--on-surface-variant);
        }

        .form-actions {
          display: flex;
          justify-content: center;
        }

        .btn-primary:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }

        @media (max-width: 600px) {
          .metrics-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default SolverForm;
