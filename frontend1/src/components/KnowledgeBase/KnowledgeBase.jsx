import React from 'react';
import { useKnowledgeBase } from '../../context/KnowledgeBaseContext';
import DocumentList from '../DocumentList/DocumentList';
import DocumentUpload from '../DocumentUpload/DocumentUpload';
import './KnowledgeBase.css';

const KnowledgeBase = () => {
  const { 
    documents, 
    isUploading, 
    isProcessing, 
    uploadProgress, 
    processingProgress, 
    error,
    uploadDocument,
    processDocument,
    removeDocument,
    clearError
  } = useKnowledgeBase();

  return (
    <div className="knowledge-base">
      <div className="kb-header">
        <h3>Knowledge Base</h3>
        <p>Quản lý tài liệu và tìm kiếm thông tin</p>
      </div>

      <div className="kb-content">
        <div className="kb-section">
          <h4>Tải lên tài liệu</h4>
          <DocumentUpload 
            onUpload={uploadDocument}
            isUploading={isUploading}
            uploadProgress={uploadProgress}
          />
        </div>

        <div className="kb-section">
          <h4>Danh sách tài liệu ({documents.length})</h4>
          <DocumentList 
            documents={documents}
            onProcess={processDocument}
            onRemove={removeDocument}
            isProcessing={isProcessing}
            processingProgress={processingProgress}
          />
        </div>

        {error && (
          <div className="kb-error">
            <div className="error-content">
              <span className="error-icon">⚠️</span>
              <span className="error-message">{error}</span>
              <button 
                className="error-dismiss"
                onClick={clearError}
              >
                ✕
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default KnowledgeBase;