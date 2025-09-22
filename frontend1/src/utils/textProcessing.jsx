// Vietnamese text processing utilities

// Vietnamese stop words
const VIETNAMESE_STOP_WORDS = new Set([
  'của', 'và', 'với', 'trong', 'cho', 'từ', 'đến', 'về', 'là', 'có', 'được', 'sẽ', 'đã', 'đang',
  'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười',
  'này', 'đó', 'kia', 'đây', 'đấy', 'nào', 'gì', 'sao', 'tại sao', 'như thế nào',
  'khi nào', 'ở đâu', 'ai', 'cái gì', 'thế nào', 'bao nhiêu', 'mấy',
  'rất', 'quá', 'cực kỳ', 'vô cùng', 'hết sức', 'tuyệt đối',
  'nhưng', 'tuy nhiên', 'mặc dù', 'dù', 'dẫu', 'dù sao',
  'nếu', 'nếu như', 'giả sử', 'trường hợp', 'khi', 'lúc', 'thời điểm',
  'vì', 'bởi vì', 'do', 'tại', 'nhờ', 'bởi', 'vì thế', 'do đó',
  'để', 'nhằm', 'mục đích', 'đích', 'kết quả', 'hậu quả',
  'cũng', 'cũng như', 'giống như', 'tương tự', 'như', 'như là',
  'hoặc', 'hay', 'hoặc là', 'hay là', 'chẳng hạn', 'ví dụ',
  'tất cả', 'mọi', 'mỗi', 'từng', 'cả', 'toàn bộ', 'toàn thể',
  'một số', 'một vài', 'vài', 'ít', 'nhiều', 'rất nhiều', 'vô số',
  'không', 'chưa', 'chẳng', 'đâu', 'đâu có', 'không có', 'chưa có',
  'có thể', 'có lẽ', 'có thể là', 'có khả năng', 'có thể xảy ra',
  'phải', 'cần', 'cần thiết', 'quan trọng', 'cần thiết phải',
  'nên', 'nên làm', 'nên có', 'nên được', 'nên phải',
  'được', 'được phép', 'được cho phép', 'được quyền',
  'bị', 'bị bắt', 'bị buộc', 'bị ép', 'bị cưỡng ép',
  'đã', 'đã từng', 'đã có', 'đã được', 'đã phải',
  'sẽ', 'sẽ có', 'sẽ được', 'sẽ phải', 'sẽ làm',
  'đang', 'đang có', 'đang được', 'đang phải', 'đang làm'
]);

// Vietnamese diacritics mapping
const VIETNAMESE_DIACRITICS = {
  'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a',
  'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a',
  'ằ': 'a', 'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a',
  'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e',
  'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
  'ì': 'i', 'í': 'i', 'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
  'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o',
  'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o',
  'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
  'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u',
  'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
  'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
  'đ': 'd'
};

// Remove Vietnamese diacritics
export const removeDiacritics = (text) => {
  return text
    .split('')
    .map(char => VIETNAMESE_DIACRITICS[char] || char)
    .join('');
};

// Normalize Vietnamese text
export const normalizeVietnameseText = (text) => {
  return text
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ')
    .replace(/[^\w\s]/g, ' ')
    .replace(/\s+/g, ' ');
};

// Tokenize Vietnamese text
export const tokenizeVietnamese = (text) => {
  return text
    .toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(token => token.length > 0);
};

// Remove Vietnamese stop words
export const removeVietnameseStopWords = (tokens) => {
  return tokens.filter(token => !VIETNAMESE_STOP_WORDS.has(token));
};

// Stem Vietnamese words (simple implementation)
export const stemVietnamese = (word) => {
  // Simple stemming for Vietnamese
  // Remove common suffixes
  const suffixes = ['ing', 'ed', 'er', 'est', 'ly', 'tion', 'sion', 'ness', 'ment'];
  
  for (const suffix of suffixes) {
    if (word.endsWith(suffix)) {
      return word.slice(0, -suffix.length);
    }
  }
  
  return word;
};

// Preprocess Vietnamese text for NLP
export const preprocessVietnameseText = (text) => {
  const normalized = normalizeVietnameseText(text);
  const tokens = tokenizeVietnamese(normalized);
  const withoutStopWords = removeVietnameseStopWords(tokens);
  const stemmed = withoutStopWords.map(stemVietnamese);
  
  return stemmed;
};

// Extract Vietnamese keywords
export const extractVietnameseKeywords = (text, maxKeywords = 10) => {
  const tokens = preprocessVietnameseText(text);
  const wordCount = {};
  
  tokens.forEach(token => {
    if (token.length > 2) {
      wordCount[token] = (wordCount[token] || 0) + 1;
    }
  });
  
  return Object.entries(wordCount)
    .sort(([, a], [, b]) => b - a)
    .slice(0, maxKeywords)
    .map(([word, count]) => ({ word, count }));
};

// Detect Vietnamese text
export const isVietnameseText = (text) => {
  const vietnameseChars = /[àáạảãầấậẩẫằắặẳẵèéẹẻẽềếệểễìíịỉĩòóọỏõồốộổỗờớợởỡùúụủũừứựửữỳýỵỷỹđ]/i;
  return vietnameseChars.test(text);
};

// Calculate Vietnamese text similarity
export const calculateVietnameseSimilarity = (text1, text2) => {
  const tokens1 = preprocessVietnameseText(text1);
  const tokens2 = preprocessVietnameseText(text2);
  
  const set1 = new Set(tokens1);
  const set2 = new Set(tokens2);
  
  const intersection = new Set([...set1].filter(x => set2.has(x)));
  const union = new Set([...set1, ...set2]);
  
  return intersection.size / union.size;
};

// Extract Vietnamese entities
export const extractVietnameseEntities = (text) => {
  const entities = {
    dates: extractVietnameseDates(text),
    numbers: extractVietnameseNumbers(text),
    locations: extractVietnameseLocations(text),
    names: extractVietnameseNames(text)
  };
  
  return entities;
};

// Extract Vietnamese dates
export const extractVietnameseDates = (text) => {
  const datePatterns = [
    /\b\d{1,2}\/\d{1,2}\/\d{2,4}\b/g,
    /\b\d{1,2}-\d{1,2}-\d{2,4}\b/g,
    /\b\d{1,2}\s+tháng\s+\d{1,2}\s+năm\s+\d{4}\b/g,
    /\btháng\s+\d{1,2}\s+năm\s+\d{4}\b/g,
    /\bnăm\s+\d{4}\b/g
  ];
  
  const dates = [];
  datePatterns.forEach(pattern => {
    const matches = text.match(pattern);
    if (matches) {
      dates.push(...matches);
    }
  });
  
  return dates;
};

// Extract Vietnamese numbers
export const extractVietnameseNumbers = (text) => {
  const numberPatterns = [
    /\b\d+\b/g,
    /\b\d+\.\d+\b/g,
    /\b\d+,\d+\b/g
  ];
  
  const numbers = [];
  numberPatterns.forEach(pattern => {
    const matches = text.match(pattern);
    if (matches) {
      numbers.push(...matches);
    }
  });
  
  return numbers;
};

// Extract Vietnamese locations (simple implementation)
export const extractVietnameseLocations = (text) => {
  const locationKeywords = [
    'hà nội', 'hồ chí minh', 'đà nẵng', 'hải phòng', 'cần thơ',
    'an giang', 'bà rịa - vũng tàu', 'bạc liêu', 'bắc giang', 'bắc kạn',
    'bắc ninh', 'bến tre', 'bình định', 'bình dương', 'bình phước',
    'bình thuận', 'cà mau', 'cao bằng', 'đắk lắk', 'đắk nông',
    'điện biên', 'đồng nai', 'đồng tháp', 'gia lai', 'hà giang',
    'hà nam', 'hà tĩnh', 'hải dương', 'hậu giang', 'hòa bình',
    'hưng yên', 'khánh hòa', 'kiên giang', 'kon tum', 'lai châu',
    'lâm đồng', 'lạng sơn', 'lào cai', 'long an', 'nam định',
    'nghệ an', 'ninh bình', 'ninh thuận', 'phú thọ', 'phú yên',
    'quảng bình', 'quảng nam', 'quảng ngãi', 'quảng ninh', 'quảng trị',
    'sóc trăng', 'sơn la', 'tây ninh', 'thái bình', 'thái nguyên',
    'thanh hóa', 'thừa thiên huế', 'tiền giang', 'trà vinh', 'tuyên quang',
    'vĩnh long', 'vĩnh phúc', 'yên bái'
  ];
  
  const locations = [];
  const lowerText = text.toLowerCase();
  
  locationKeywords.forEach(location => {
    if (lowerText.includes(location)) {
      locations.push(location);
    }
  });
  
  return locations;
};

// Extract Vietnamese names (simple implementation)
export const extractVietnameseNames = (text) => {
  // Simple name extraction based on capitalization patterns
  const words = text.split(/\s+/);
  const names = [];
  
  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    if (word.length > 2 && /^[A-ZÀÁẠẢÃẦẤẬẨẪẰẮẶẲẴÈÉẸẺẼỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕỒỐỘỔỖỜỚỢỞỠÙÚỤỦŨỪỨỰỬỮỲÝỴỶỸĐ]/.test(word)) {
      names.push(word);
    }
  }
  
  return names;
};

// Format Vietnamese text for display
export const formatVietnameseText = (text) => {
  return text
    .replace(/\s+/g, ' ')
    .replace(/([.!?])\s*([A-ZÀÁẠẢÃẦẤẬẨẪẰẮẶẲẴÈÉẸẺẼỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕỒỐỘỔỖỜỚỢỞỠÙÚỤỦŨỪỨỰỬỮỲÝỴỶỸĐ])/g, '$1 $2')
    .trim();
};

// Calculate Vietnamese text readability
export const calculateVietnameseReadability = (text) => {
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
  const words = text.split(/\s+/).filter(w => w.length > 0);
  const syllables = words.reduce((count, word) => count + countVietnameseSyllables(word), 0);
  
  const avgWordsPerSentence = words.length / sentences.length;
  const avgSyllablesPerWord = syllables / words.length;
  
  // Simple readability score for Vietnamese
  const score = 206.835 - (1.015 * avgWordsPerSentence) - (84.6 * avgSyllablesPerWord);
  
  return {
    score: Math.max(0, Math.min(100, score)),
    avgWordsPerSentence,
    avgSyllablesPerWord,
    totalWords: words.length,
    totalSentences: sentences.length,
    totalSyllables: syllables
  };
};

// Count Vietnamese syllables
export const countVietnameseSyllables = (word) => {
  // Simple syllable counting for Vietnamese
  const vowels = /[aeiouàáạảãầấậẩẫằắặẳẵèéẹẻẽềếệểễìíịỉĩòóọỏõồốộổỗờớợởỡùúụủũừứựửữỳýỵỷỹ]/gi;
  const matches = word.match(vowels);
  return matches ? matches.length : 1;
};
