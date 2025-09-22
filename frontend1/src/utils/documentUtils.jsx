// Document processing utility functions

// Extract text from different file types
export const extractTextFromFile = async (file) => {
  const fileType = file.type;
  const fileName = file.name.toLowerCase();

  try {
    if (fileType === 'text/plain' || fileName.endsWith('.txt')) {
      return await extractTextFromTxt(file);
    } else if (fileType === 'application/pdf' || fileName.endsWith('.pdf')) {
      return await extractTextFromPdf(file);
    } else if (fileType.includes('word') || fileName.endsWith('.docx') || fileName.endsWith('.doc')) {
      return await extractTextFromWord(file);
    } else if (fileName.endsWith('.md')) {
      return await extractTextFromMarkdown(file);
    } else {
      throw new Error(`Unsupported file type: ${fileType}`);
    }
  } catch (error) {
    console.error('Text extraction error:', error);
    throw error;
  }
};

// Extract text from plain text file
const extractTextFromTxt = async (file) => {
  return await file.text();
};

// Extract text from PDF file (mock implementation)
const extractTextFromPdf = async (file) => {
  // Mock PDF text extraction
  // In real implementation, use a PDF parsing library like pdf-parse
  return `PDF Content from ${file.name}:\n\nThis is mock text extracted from a PDF file. In a real implementation, you would use a PDF parsing library to extract the actual text content.`;
};

// Extract text from Word document (mock implementation)
const extractTextFromWord = async (file) => {
  // Mock Word document text extraction
  // In real implementation, use a library like mammoth.js
  return `Word Document Content from ${file.name}:\n\nThis is mock text extracted from a Word document. In a real implementation, you would use a library like mammoth.js to extract the actual text content.`;
};

// Extract text from Markdown file
const extractTextFromMarkdown = async (file) => {
  return await file.text();
};

// Split text into chunks
export const splitTextIntoChunks = (text, chunkSize = 1000, overlap = 200) => {
  if (!text || text.length === 0) return [];

  const chunks = [];
  let start = 0;

  while (start < text.length) {
    const end = Math.min(start + chunkSize, text.length);
    let chunk = text.slice(start, end);

    // Try to break at sentence boundary
    if (end < text.length) {
      const lastSentenceEnd = chunk.lastIndexOf('.');
      const lastQuestionEnd = chunk.lastIndexOf('?');
      const lastExclamationEnd = chunk.lastIndexOf('!');
      const lastNewline = chunk.lastIndexOf('\n');

      const breakPoint = Math.max(lastSentenceEnd, lastQuestionEnd, lastExclamationEnd, lastNewline);
      
      if (breakPoint > start + chunkSize * 0.5) {
        chunk = chunk.slice(0, breakPoint + 1);
        end = start + breakPoint + 1;
      }
    }

    chunks.push({
      text: chunk.trim(),
      start,
      end: start + chunk.length,
      index: chunks.length
    });

    start = end - overlap;
  }

  return chunks;
};

// Clean and normalize text
export const cleanText = (text) => {
  return text
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .replace(/[ \t]+/g, ' ')
    .trim();
};

// Remove extra whitespace
export const removeExtraWhitespace = (text) => {
  return text
    .replace(/\s+/g, ' ')
    .trim();
};

// Extract sentences from text
export const extractSentences = (text) => {
  const sentences = text
    .split(/[.!?]+/)
    .map(sentence => sentence.trim())
    .filter(sentence => sentence.length > 0);

  return sentences;
};

// Extract paragraphs from text
export const extractParagraphs = (text) => {
  const paragraphs = text
    .split(/\n\s*\n/)
    .map(paragraph => paragraph.trim())
    .filter(paragraph => paragraph.length > 0);

  return paragraphs;
};

// Extract words from text
export const extractWords = (text) => {
  return text
    .toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(word => word.length > 0);
};

// Calculate text statistics
export const calculateTextStats = (text) => {
  const words = extractWords(text);
  const sentences = extractSentences(text);
  const paragraphs = extractParagraphs(text);

  return {
    characters: text.length,
    charactersNoSpaces: text.replace(/\s/g, '').length,
    words: words.length,
    sentences: sentences.length,
    paragraphs: paragraphs.length,
    averageWordsPerSentence: words.length / sentences.length,
    averageSentencesPerParagraph: sentences.length / paragraphs.length,
    averageCharactersPerWord: text.length / words.length
  };
};

// Detect language of text
export const detectLanguage = (text) => {
  // Simple language detection based on common words
  const vietnameseWords = ['của', 'và', 'với', 'trong', 'cho', 'từ', 'đến', 'về', 'là', 'có', 'được', 'sẽ', 'đã', 'đang'];
  const englishWords = ['the', 'and', 'with', 'in', 'for', 'from', 'to', 'about', 'is', 'are', 'was', 'were', 'will', 'have', 'has'];

  const words = extractWords(text);
  const sampleSize = Math.min(100, words.length);
  const sample = words.slice(0, sampleSize);

  const vietnameseCount = sample.filter(word => vietnameseWords.includes(word)).length;
  const englishCount = sample.filter(word => englishWords.includes(word)).length;

  if (vietnameseCount > englishCount) {
    return 'vi';
  } else if (englishCount > vietnameseCount) {
    return 'en';
  } else {
    return 'unknown';
  }
};

// Extract keywords from text
export const extractKeywords = (text, maxKeywords = 10) => {
  const words = extractWords(text);
  const stopWords = new Set([
    'của', 'và', 'với', 'trong', 'cho', 'từ', 'đến', 'về', 'là', 'có', 'được', 'sẽ', 'đã', 'đang',
    'the', 'and', 'with', 'in', 'for', 'from', 'to', 'about', 'is', 'are', 'was', 'were', 'will', 'have', 'has'
  ]);

  const wordCount = {};
  words.forEach(word => {
    if (word.length > 2 && !stopWords.has(word)) {
      wordCount[word] = (wordCount[word] || 0) + 1;
    }
  });

  return Object.entries(wordCount)
    .sort(([, a], [, b]) => b - a)
    .slice(0, maxKeywords)
    .map(([word, count]) => ({ word, count }));
};

// Extract entities from text
export const extractEntities = (text) => {
  const entities = {
    dates: extractDates(text),
    numbers: extractNumbers(text),
    emails: extractEmails(text),
    urls: extractUrls(text),
    phoneNumbers: extractPhoneNumbers(text)
  };

  return entities;
};

// Extract dates from text
export const extractDates = (text) => {
  const dateRegex = /\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b/g;
  return text.match(dateRegex) || [];
};

// Extract numbers from text
export const extractNumbers = (text) => {
  const numberRegex = /\b\d+(?:\.\d+)?\b/g;
  return text.match(numberRegex) || [];
};

// Extract email addresses from text
export const extractEmails = (text) => {
  const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
  return text.match(emailRegex) || [];
};

// Extract URLs from text
export const extractUrls = (text) => {
  const urlRegex = /https?:\/\/[^\s]+/g;
  return text.match(urlRegex) || [];
};

// Extract phone numbers from text
export const extractPhoneNumbers = (text) => {
  const phoneRegex = /\b\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b/g;
  return text.match(phoneRegex) || [];
};

// Validate document file
export const validateDocumentFile = (file) => {
  const errors = [];
  const maxSize = 10 * 1024 * 1024; // 10MB
  const allowedTypes = [
    'text/plain',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword'
  ];
  const allowedExtensions = ['.txt', '.pdf', '.docx', '.doc', '.md'];

  if (file.size > maxSize) {
    errors.push('File size must be less than 10MB');
  }

  if (!allowedTypes.includes(file.type) && !allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext))) {
    errors.push('File type not supported. Please upload .txt, .pdf, .docx, .doc, or .md files');
  }

  return errors;
};

// Get file type from filename
export const getFileType = (filename) => {
  const extension = filename.toLowerCase().split('.').pop();
  
  const typeMap = {
    'txt': 'text/plain',
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'doc': 'application/msword',
    'md': 'text/markdown'
  };

  return typeMap[extension] || 'application/octet-stream';
};

// Format file size
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Generate document metadata
export const generateDocumentMetadata = (file, extractedText) => {
  const stats = calculateTextStats(extractedText);
  const language = detectLanguage(extractedText);
  const keywords = extractKeywords(extractedText, 5);
  const entities = extractEntities(extractedText);

  return {
    filename: file.name,
    size: file.size,
    type: file.type,
    language,
    stats,
    keywords,
    entities,
    uploadDate: new Date().toISOString(),
    processedDate: new Date().toISOString()
  };
};
