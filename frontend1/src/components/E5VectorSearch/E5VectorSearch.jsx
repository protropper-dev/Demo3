import React, { useState } from 'react';
import './E5VectorSearch.css';

const E5VectorSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setSearching(true);
    // Search logic here
    setTimeout(() => {
      setResults([
        { id: 1, text: 'Kết quả tìm kiếm 1', score: 0.95 },
        { id: 2, text: 'Kết quả tìm kiếm 2', score: 0.87 }
      ]);
      setSearching(false);
    }, 1000);
  };

  return (
    <div className="e5-vector-search">
      <div className="search-header">
        <h3>Tìm kiếm Vector E5</h3>
        <p>Tìm kiếm thông tin dựa trên embedding vectors</p>
      </div>
      
      <div className="search-input">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Nhập từ khóa tìm kiếm..."
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button onClick={handleSearch} disabled={searching}>
          {searching ? '🔍' : 'Tìm kiếm'}
        </button>
      </div>
      
      <div className="search-results">
        {results.map(result => (
          <div key={result.id} className="result-item">
            <div className="result-score">{Math.round(result.score * 100)}%</div>
            <div className="result-text">{result.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default E5VectorSearch;
