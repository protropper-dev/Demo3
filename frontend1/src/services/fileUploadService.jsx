// File Upload Service
// Xử lý upload file và embedding

const API_BASE_URL = 'http://localhost:8000/api/v1';

class FileUploadService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * Upload file lên server
   * @param {File} file - File cần upload
   * @param {Function} onProgress - Callback để theo dõi tiến trình
   * @returns {Promise} Response từ server
   */
  async uploadFile(file, onProgress = null) {
    try {
      // Validate file type
      const allowedTypes = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           'text/plain'];
      const allowedExtensions = ['.pdf', '.doc', '.docx', '.txt'];
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      
      if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
        throw new Error('Chỉ chấp nhận file PDF, DOC, DOCX, TXT');
      }

      // Validate file size (10MB max)
      const maxSize = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSize) {
        throw new Error('File quá lớn. Kích thước tối đa: 10MB');
      }

      // Tạo FormData
      const formData = new FormData();
      formData.append('file', file);

      // Gọi API upload
      const response = await fetch(`${this.baseURL}/files/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Lỗi upload file');
      }

      const result = await response.json();
      
      // Bắt đầu theo dõi tiến trình embedding
      if (result.success && result.file_id) {
        this.monitorEmbeddingProgress(result.file_id, onProgress);
      }

      return result;

    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  }

  /**
   * Theo dõi tiến trình embedding
   * @param {string} fileId - ID của file
   * @param {Function} onProgress - Callback để cập nhật tiến trình
   */
  async monitorEmbeddingProgress(fileId, onProgress = null) {
    const maxAttempts = 30; // Tối đa 30 lần check (5 phút)
    let attempts = 0;

    const checkStatus = async () => {
      try {
        const response = await fetch(`${this.baseURL}/files/status/${fileId}`);
        
        if (response.ok) {
          const status = await response.json();
          
          if (onProgress) {
            onProgress({
              progress: status.progress,
              status: status.status,
              message: status.message
            });
          }

          // Nếu đã hoàn thành hoặc lỗi, dừng monitoring
          if (status.status === 'completed' || status.status === 'error') {
            return;
          }
        }

        attempts++;
        if (attempts < maxAttempts) {
          // Check lại sau 10 giây
          setTimeout(checkStatus, 10000);
        } else {
          console.warn('Timeout monitoring embedding progress');
          if (onProgress) {
            onProgress({
              progress: 100,
              status: 'timeout',
              message: 'Timeout - vui lòng kiểm tra lại sau'
            });
          }
        }

      } catch (error) {
        console.error('Error monitoring embedding:', error);
        if (onProgress) {
          onProgress({
            progress: 0,
            status: 'error',
            message: 'Lỗi theo dõi tiến trình'
          });
        }
      }
    };

    // Bắt đầu monitoring sau 2 giây
    setTimeout(checkStatus, 2000);
  }

  /**
   * Lấy danh sách files đã upload
   * @returns {Promise} Danh sách files
   */
  async getUploadedFiles() {
    try {
      const response = await fetch(`${this.baseURL}/files/files`);
      
      if (!response.ok) {
        throw new Error('Lỗi lấy danh sách file');
      }

      return await response.json();

    } catch (error) {
      console.error('Error getting files:', error);
      throw error;
    }
  }

  /**
   * Xóa file
   * @param {string} fileId - ID của file cần xóa
   * @returns {Promise} Kết quả xóa
   */
  async deleteFile(fileId) {
    try {
      const response = await fetch(`${this.baseURL}/files/files/${fileId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Lỗi xóa file');
      }

      return await response.json();

    } catch (error) {
      console.error('Error deleting file:', error);
      throw error;
    }
  }

  /**
   * Kiểm tra trạng thái service
   * @returns {Promise} Trạng thái service
   */
  async getHealthStatus() {
    try {
      const response = await fetch(`${this.baseURL}/files/health`);
      return await response.json();
    } catch (error) {
      console.error('Error checking health:', error);
      return { status: 'unhealthy', error: error.message };
    }
  }
}

// Tạo instance singleton
const fileUploadService = new FileUploadService();

export default fileUploadService;
