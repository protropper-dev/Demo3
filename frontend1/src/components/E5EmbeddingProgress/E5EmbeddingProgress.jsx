import React from 'react';
import './E5EmbeddingProgress.css';

const E5EmbeddingProgress = ({ progress }) => {
  return (
    <div className="e5-embedding-progress">
      <div className="progress-header">
        <span className="progress-icon">🔢</span>
        <span className="progress-title">E5 Embedding</span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress.percentage || 0}%` }}></div>
      </div>
      <div className="progress-text">{progress.status || 'Processing...'}</div>
    </div>
  );
};

export default E5EmbeddingProgress;
