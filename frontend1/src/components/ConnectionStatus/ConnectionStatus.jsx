import React, { useState, useEffect } from 'react';
import Backend1Service from '../../services/backend1Service.jsx';
import './ConnectionStatus.css';

const ConnectionStatus = () => {
  const [connectionStatus, setConnectionStatus] = useState({
    connected: false,
    loading: true,
    message: '',
    lastChecked: null
  });
  const [systemInfo, setSystemInfo] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  const checkConnection = async (retries = 3) => {
    try {
      setConnectionStatus(prev => ({ ...prev, loading: true }));
      
      console.log(`Checking connection to backend1... (attempt ${4-retries})`);
      
      // Thử kết nối với retry logic
      let result;
      let attempts = retries;
      
      while (attempts > 0) {
        try {
          result = await Backend1Service.checkConnection();
          break; // Thành công, thoát khỏi retry loop
        } catch (error) {
          console.error(`Connection attempt ${4-attempts} failed:`, error);
          attempts--;
          
          if (attempts > 0) {
            console.log(`Retrying connection in 1 second... (${attempts} attempts left)`);
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
        }
      }
      
      if (!result) {
        throw new Error('All connection attempts failed');
      }
      
      setConnectionStatus({
        connected: result.connected,
        loading: false,
        message: result.message,
        lastChecked: new Date().toISOString()
      });

      // Nếu kết nối thành công, lấy thông tin hệ thống
      if (result.connected) {
        try {
          const info = await Backend1Service.getSystemInfo();
          setSystemInfo(info);
        } catch (error) {
          console.error('Lỗi lấy thông tin hệ thống:', error);
        }
      }
    } catch (error) {
      console.error('Connection check error:', error);
      
      let errorMessage = 'Không thể kết nối đến backend1';
      
      if (error.message.includes('ERR_EMPTY_RESPONSE')) {
        errorMessage = 'Backend1 không phản hồi - có thể đã dừng';
      } else if (error.message.includes('Network error')) {
        errorMessage = 'Lỗi mạng - kiểm tra kết nối';
      } else if (error.message.includes('timeout')) {
        errorMessage = 'Hết thời gian chờ - backend1 phản hồi chậm';
      } else {
        errorMessage = `Lỗi kết nối: ${error.message}`;
      }
      
      setConnectionStatus({
        connected: false,
        loading: false,
        message: errorMessage,
        lastChecked: new Date().toISOString()
      });
    }
  };

  useEffect(() => {
    // Delay 2 giây để đảm bảo backend đã sẵn sàng hoàn toàn
    const initialTimer = setTimeout(checkConnection, 2000);
    
    // Kiểm tra kết nối mỗi 30 giây
    const interval = setInterval(checkConnection, 30000);
    
    return () => {
      clearTimeout(initialTimer);
      clearInterval(interval);
    };
  }, []);

  const handleRetry = () => {
    checkConnection();
  };

  const toggleDetails = () => {
    setShowDetails(!showDetails);
  };

  return (
    <div className="connection-status">
      <div className="connection-header">
        <div className="connection-indicator">
          <div className={`status-dot ${connectionStatus.connected ? 'connected' : 'disconnected'}`}>
            {connectionStatus.loading && <div className="loading-pulse"></div>}
          </div>
          <span className="status-text">
            {connectionStatus.loading ? 'Đang kiểm tra...' : 
             connectionStatus.connected ? 'Đã kết nối' : 'Mất kết nối'}
          </span>
        </div>
        
        <div className="connection-actions">
          <button 
            className="retry-button"
            onClick={handleRetry}
            disabled={connectionStatus.loading}
            title="Kiểm tra lại kết nối"
          >
            🔄
          </button>
          
          <button 
            className="details-button"
            onClick={toggleDetails}
            title="Xem chi tiết"
          >
            {showDetails ? '📖' : '📋'}
          </button>
        </div>
      </div>

      {connectionStatus.message && (
        <div className={`connection-message ${connectionStatus.connected ? 'success' : 'error'}`}>
          {connectionStatus.message}
        </div>
      )}

      {connectionStatus.lastChecked && (
        <div className="last-checked">
          Cập nhật lần cuối: {new Date(connectionStatus.lastChecked).toLocaleTimeString('vi-VN')}
        </div>
      )}

      {showDetails && systemInfo && (
        <div className="system-details">
          <h4>Thông tin hệ thống</h4>
          
          <div className="info-section">
            <h5>Trạng thái Health</h5>
            <div className="info-item">
              <span className="label">Status:</span>
              <span className={`value ${systemInfo.health?.status === 'healthy' ? 'success' : 'error'}`}>
                {systemInfo.health?.status || 'Unknown'}
              </span>
            </div>
            <div className="info-item">
              <span className="label">Environment:</span>
              <span className="value">{systemInfo.health?.environment || 'Unknown'}</span>
            </div>
            <div className="info-item">
              <span className="label">Database:</span>
              <span className={`value ${systemInfo.health?.database?.includes('healthy') ? 'success' : 'error'}`}>
                {systemInfo.health?.database || 'Unknown'}
              </span>
            </div>
          </div>

          {systemInfo.enhancedStatus && (
            <div className="info-section">
              <h5>Enhanced System</h5>
              <div className="info-item">
                <span className="label">Status:</span>
                <span className={`value ${systemInfo.enhancedStatus.status === 'healthy' ? 'success' : 'error'}`}>
                  {systemInfo.enhancedStatus.status || 'Unknown'}
                </span>
              </div>
              <div className="info-item">
                <span className="label">LLM Model:</span>
                <span className={`value ${systemInfo.enhancedStatus.llm_model_loaded ? 'success' : 'error'}`}>
                  {systemInfo.enhancedStatus.llm_model_loaded ? 'Loaded' : 'Not Loaded'}
                </span>
              </div>
              <div className="info-item">
                <span className="label">Embedding Model:</span>
                <span className={`value ${systemInfo.enhancedStatus.embedding_model_loaded ? 'success' : 'error'}`}>
                  {systemInfo.enhancedStatus.embedding_model_loaded ? 'Loaded' : 'Not Loaded'}
                </span>
              </div>
              <div className="info-item">
                <span className="label">Device:</span>
                <span className="value">{systemInfo.enhancedStatus.device || 'Unknown'}</span>
              </div>
              <div className="info-item">
                <span className="label">FAISS Loaded:</span>
                <span className={`value ${systemInfo.enhancedStatus.faiss_loaded ? 'success' : 'error'}`}>
                  {systemInfo.enhancedStatus.faiss_loaded ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="info-item">
                <span className="label">Chunks:</span>
                <span className="value">{systemInfo.enhancedStatus.chunks_loaded || 0}</span>
              </div>
            </div>
          )}

          <div className="info-section">
            <h5>Thời gian</h5>
            <div className="info-item">
              <span className="label">Timestamp:</span>
              <span className="value">{new Date(systemInfo.timestamp).toLocaleString('vi-VN')}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConnectionStatus;
