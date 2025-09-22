import React from 'react';
import './DocumentList.css';

const DocumentList = ({ documents, onProcess, onRemove, isProcessing, processingProgress }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'uploaded': return '#ffc107';
      case 'processing': return '#17a2b8';
      case 'processed': return '#28a745';
      case 'error': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'uploaded': return 'Đã tải lên';
      case 'processing': return 'Đang xử lý';
      case 'processed': return 'Đã xử lý';
      case 'error': return 'Lỗi';
      default: return 'Không xác định';
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (documents.length === 0) {
    return (
      <div className="document-list empty">
        <div className="empty-state">
          <div className="empty-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
            </svg>
          </div>
          <h4>Chưa có tài liệu nào</h4>
          <p>Tải lên tài liệu đầu tiên để bắt đầu xây dựng knowledge base</p>
        </div>
      </div>
    );
  }

  return (
    <div className="document-list">
      {documents.map((doc) => (
        <div key={doc.id} className="document-item">
          <div className="document-info">
            <div className="document-header">
              <h5 className="document-name">{doc.name}</h5>
              <span 
                className="document-status"
                style={{ color: getStatusColor(doc.status) }}
              >
                {getStatusText(doc.status)}
              </span>
            </div>
            
            <div className="document-meta">
              <span className="document-size">{formatFileSize(doc.size)}</span>
              <span className="document-type">{doc.type}</span>
              <span className="document-date">
                {new Date(doc.uploadDate).toLocaleDateString('vi-VN')}
              </span>
            </div>
          </div>

          <div className="document-actions">
            {doc.status === 'uploaded' && (
              <button 
                className="action-button process-button"
                onClick={() => onProcess(doc.id)}
                disabled={isProcessing}
              >
                {isProcessing ? 'Đang xử lý...' : 'Xử lý'}
              </button>
            )}
            
            {doc.status === 'processing' && processingProgress > 0 && (
              <div className="processing-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${processingProgress}%` }}
                  ></div>
                </div>
                <span className="progress-text">{processingProgress}%</span>
              </div>
            )}
            
            <button 
              className="action-button remove-button"
              onClick={() => onRemove(doc.id)}
              disabled={doc.status === 'processing'}
            >
              Xóa
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default DocumentList;