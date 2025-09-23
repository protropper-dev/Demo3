// Files Service
// Xử lý gọi API để lấy thông tin files từ tất cả thư mục documents

const API_BASE_URL = 'http://localhost:8000/api/v1';

class FilesService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * Lấy danh sách tất cả files từ các thư mục documents
   * @returns {Promise} Response chứa recent uploads và all files
   */
  async getAllFiles() {
    try {
      const response = await fetch(`${this.baseURL}/files/files/all`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        },
        credentials: 'include',
        cache: 'no-store'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;

    } catch (error) {
      console.error('Error fetching all files:', error);
      throw error;
    }
  }

  /**
   * Lấy danh sách files đã upload gần đây
   * @returns {Promise} Response chứa uploaded files
   */
  async getRecentUploadedFiles() {
    try {
      const response = await fetch(`${this.baseURL}/files/files/uploaded`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        },
        credentials: 'include',
        cache: 'no-store'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;

    } catch (error) {
      console.error('Error fetching uploaded files:', error);
      throw error;
    }
  }

  /**
   * Kiểm tra trạng thái sức khỏe của files service
   * @returns {Promise} Health status
   */
  async getHealthStatus() {
    try {
      const response = await fetch(`${this.baseURL}/files/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();

    } catch (error) {
      console.error('Error checking files service health:', error);
      return { status: 'unhealthy', error: error.message };
    }
  }

  /**
   * Format file size từ bytes sang readable format
   * @param {number} bytes - File size in bytes
   * @returns {string} Formatted size string
   */
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Lấy icon cho file dựa trên extension
   * @param {string} filename - Tên file
   * @returns {string} Icon emoji
   */
  getFileIcon(filename) {
    const extension = filename.split('.').pop().toLowerCase();
    switch (extension) {
      case 'pdf':
        return '📕';
      case 'doc':
      case 'docx':
        return '📄';
      case 'txt':
        return '📝';
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return '🖼️';
      case 'py':
      case 'js':
      case 'jsx':
      case 'ts':
      case 'tsx':
      case 'java':
      case 'cpp':
      case 'c':
        return '💻';
      case 'zip':
      case 'rar':
      case '7z':
        return '📦';
      default:
        return '📄';
    }
  }

  /**
   * Format thời gian hiển thị
   * @param {string} timestamp - ISO timestamp string
   * @returns {string} Formatted time string
   */
  formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'vài giây trước';
    if (diff < 3600000) return `${Math.floor(diff / 60000)} phút trước`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} giờ trước`;
    return `${Math.floor(diff / 86400000)} ngày trước`;
  }

  /**
   * Lấy status badge cho file
   * @param {boolean} isEmbedded - File đã được embedded chưa
   * @param {string} status - Status string
   * @returns {object} Badge info
   */
  getStatusBadge(isEmbedded, status) {
    if (isEmbedded || status === 'embedded') {
      return {
        icon: '✅',
        text: 'Đã embedding',
        className: 'status-embedded'
      };
    } else {
      return {
        icon: '⏳',
        text: 'Chưa embedding',
        className: 'status-pending'
      };
    }
  }

  /**
   * Group files theo category
   * @param {object} allFiles - Object chứa tất cả files theo category
   * @returns {object} Grouped files với metadata
   */
  groupFilesByCategory(allFiles) {
    const grouped = {};
    
    Object.entries(allFiles).forEach(([category, files]) => {
      grouped[category] = {
        files: files,
        count: files.length,
        totalSize: files.reduce((sum, file) => sum + file.size, 0),
        embeddedCount: files.filter(file => file.is_embedded).length
      };
    });
    
    return grouped;
  }

  /**
   * Filter files theo search term
   * @param {array} files - Danh sách files
   * @param {string} searchTerm - Từ khóa tìm kiếm
   * @returns {array} Filtered files
   */
  filterFiles(files, searchTerm) {
    if (!searchTerm || searchTerm.trim() === '') {
      return files;
    }
    
    const term = searchTerm.toLowerCase().trim();
    return files.filter(file => 
      file.filename.toLowerCase().includes(term) ||
      file.category?.toLowerCase().includes(term) ||
      file.extension?.toLowerCase().includes(term)
    );
  }

  /**
   * Sort files theo tiêu chí
   * @param {array} files - Danh sách files
   * @param {string} sortBy - Tiêu chí sort ('name', 'date', 'size', 'status')
   * @param {string} sortOrder - Thứ tự sort ('asc', 'desc')
   * @returns {array} Sorted files
   */
  sortFiles(files, sortBy = 'date', sortOrder = 'desc') {
    const sortedFiles = [...files];
    
    sortedFiles.sort((a, b) => {
      let valueA, valueB;
      
      switch (sortBy) {
        case 'name':
          valueA = a.filename.toLowerCase();
          valueB = b.filename.toLowerCase();
          break;
        case 'date':
          valueA = new Date(a.modified || a.uploaded_at);
          valueB = new Date(b.modified || b.uploaded_at);
          break;
        case 'size':
          valueA = a.size;
          valueB = b.size;
          break;
        case 'status':
          valueA = a.is_embedded ? 1 : 0;
          valueB = b.is_embedded ? 1 : 0;
          break;
        default:
          valueA = a.filename.toLowerCase();
          valueB = b.filename.toLowerCase();
      }
      
      if (sortOrder === 'asc') {
        return valueA < valueB ? -1 : valueA > valueB ? 1 : 0;
      } else {
        return valueA > valueB ? -1 : valueA < valueB ? 1 : 0;
      }
    });
    
    return sortedFiles;
  }
}

// Tạo instance singleton
const filesService = new FilesService();

export default filesService;
