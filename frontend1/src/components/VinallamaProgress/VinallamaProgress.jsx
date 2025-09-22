import React from 'react';
import './VinallamaProgress.css';

const VinallamaProgress = ({ progress }) => {
  return (
    <div className="vinallama-progress">
      <div className="progress-header">
        <span className="progress-icon">🤖</span>
        <span className="progress-title">Vinallama Processing</span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress.percentage || 0}%` }}></div>
      </div>
      <div className="progress-text">{progress.status || 'Processing...'}</div>
    </div>
  );
};

export default VinallamaProgress;
