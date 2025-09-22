import React from 'react';
import { useVinallama } from '../../context/VinallamaContext';
import { useE5Embedding } from '../../context/E5EmbeddingContext';
import './ModelStatus.css';

const ModelStatus = () => {
  const { modelStatus: vinallamaStatus, progress: vinallamaProgress } = useVinallama();
  const { modelStatus: e5Status, progress: e5Progress } = useE5Embedding();

  const getStatusColor = (status) => {
    switch (status) {
      case 'ready': return '#28a745';
      case 'loading': return '#ffc107';
      case 'error': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'ready': return 'Sẵn sàng';
      case 'loading': return 'Đang tải';
      case 'error': return 'Lỗi';
      default: return 'Không xác định';
    }
  };

  return (
    <div className="model-status">
      <h4>Trạng thái Models</h4>
      
      <div className="status-grid">
        <div className="status-item">
          <div className="status-header">
            <span className="model-name">Vinallama</span>
            <span 
              className="status-dot"
              style={{ backgroundColor: getStatusColor(vinallamaStatus) }}
            ></span>
          </div>
          <div className="status-details">
            <span className={`status-text status-${vinallamaStatus}`}>
              {getStatusText(vinallamaStatus)}
            </span>
            {vinallamaProgress && vinallamaStatus === 'loading' && (
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${vinallamaProgress.percentage}%` }}
                ></div>
              </div>
            )}
          </div>
        </div>

        <div className="status-item">
          <div className="status-header">
            <span className="model-name">E5 Embedding</span>
            <span 
              className="status-dot"
              style={{ backgroundColor: getStatusColor(e5Status) }}
            ></span>
          </div>
          <div className="status-details">
            <span className={`status-text status-${e5Status}`}>
              {getStatusText(e5Status)}
            </span>
            {e5Progress && e5Status === 'loading' && (
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${e5Progress.percentage}%` }}
                ></div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelStatus;