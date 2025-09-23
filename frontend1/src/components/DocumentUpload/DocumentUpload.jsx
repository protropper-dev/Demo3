import React, { useState, useRef } from 'react';
import './DocumentUpload.css';
import fileUploadService from '../../services/fileUploadService';

const DocumentUpload = ({ onUpload, isUploading, uploadProgress }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState({});
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (files) => {
    const fileArray = Array.from(files);
    const validFiles = fileArray.filter(file => {
      const validTypes = [
        'text/plain',
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword'
      ];
      const validExtensions = ['.txt', '.pdf', '.docx', '.doc'];
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      
      return validTypes.includes(file.type) || validExtensions.includes(fileExtension);
    });

    if (validFiles.length !== fileArray.length) {
      alert('Một số file không được hỗ trợ. Chỉ chấp nhận: .txt, .pdf, .docx, .doc');
    }

    setSelectedFiles(prev => [...prev, ...validFiles]);
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    for (const file of selectedFiles) {
      try {
        // Cập nhật status upload
        setUploadStatus(prev => ({
          ...prev,
          [file.name]: {
            status: 'uploading',
            progress: 0,
            message: 'Đang tải lên...'
          }
        }));

        // Upload file với theo dõi tiến trình
        const result = await fileUploadService.uploadFile(file, (progressData) => {
          setUploadStatus(prev => ({
            ...prev,
            [file.name]: {
              status: progressData.status,
              progress: progressData.progress,
              message: progressData.message
            }
          }));
        });

        // Gọi callback từ parent component nếu có
        if (onUpload) {
          await onUpload(file, result);
        }

        // Cập nhật status cuối cùng
        setUploadStatus(prev => ({
          ...prev,
          [file.name]: {
            status: 'completed',
            progress: 100,
            message: 'Upload và embedding hoàn thành!'
          }
        }));

      } catch (error) {
        console.error('Upload error:', error);
        setUploadStatus(prev => ({
          ...prev,
          [file.name]: {
            status: 'error',
            progress: 0,
            message: `Lỗi: ${error.message}`
          }
        }));
      }
    }

    // Clear files sau khi upload xong
    setTimeout(() => {
      setSelectedFiles([]);
      setUploadStatus({});
    }, 2000);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="document-upload">
      <div 
        className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".txt,.pdf,.docx,.doc"
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />
        
        <div className="upload-content">
          <div className="upload-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
            </svg>
          </div>
          <h4>Kéo thả file vào đây hoặc click để chọn</h4>
          <p>Hỗ trợ: PDF, Word, Text (tối đa 10MB mỗi file)</p>
        </div>
      </div>

      {selectedFiles.length > 0 && (
        <div className="selected-files">
          <h5>File đã chọn ({selectedFiles.length})</h5>
          <div className="file-list">
            {selectedFiles.map((file, index) => {
              const fileStatus = uploadStatus[file.name] || {};
              return (
                <div key={index} className="file-item">
                  <div className="file-info">
                    <span className="file-name">{file.name}</span>
                    <span className="file-size">{formatFileSize(file.size)}</span>
                    {fileStatus.status && (
                      <div className="file-status">
                        <span className={`status-indicator ${fileStatus.status}`}>
                          {fileStatus.status === 'uploading' && '📤'}
                          {fileStatus.status === 'processing' && '⚙️'}
                          {fileStatus.status === 'completed' && '✅'}
                          {fileStatus.status === 'error' && '❌'}
                        </span>
                        <span className="status-message">{fileStatus.message}</span>
                        {fileStatus.progress > 0 && (
                          <div className="progress-bar">
                            <div 
                              className="progress-fill"
                              style={{ width: `${fileStatus.progress}%` }}
                            ></div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <button 
                    className="remove-file"
                    onClick={() => removeFile(index)}
                    disabled={fileStatus.status === 'uploading' || fileStatus.status === 'processing'}
                  >
                    ✕
                  </button>
                </div>
              );
            })}
          </div>
          
          <div className="upload-actions">
            <button 
              className="upload-button"
              onClick={handleUpload}
              disabled={isUploading}
            >
              {isUploading ? 'Đang tải lên...' : 'Tải lên'}
            </button>
            <button 
              className="clear-button"
              onClick={() => setSelectedFiles([])}
              disabled={isUploading}
            >
              Xóa tất cả
            </button>
          </div>
        </div>
      )}

      {isUploading && uploadProgress > 0 && (
        <div className="upload-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <span className="progress-text">{uploadProgress}%</span>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;