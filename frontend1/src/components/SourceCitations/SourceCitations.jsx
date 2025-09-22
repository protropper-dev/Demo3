import React, { useState } from 'react';
import './SourceCitations.css';

const SourceCitations = ({ sources }) => {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) {
    return null;
  }

  const toggleExpanded = () => {
    setExpanded(!expanded);
  };

  return (
    <div className="source-citations">
      <div className="citations-header" onClick={toggleExpanded}>
        <span className="citations-title">
          📚 Nguồn tham khảo ({sources.length})
        </span>
        <span className={`expand-icon ${expanded ? 'expanded' : ''}`}>
          ▼
        </span>
      </div>
      
      {expanded && (
        <div className="citations-content">
          {sources.map((source, index) => (
            <div key={index} className="citation-item">
              <div className="citation-header">
                <span className="citation-filename">
                  {source.filename || source.title || `Nguồn ${index + 1}`}
                </span>
                <span className="citation-category">
                  {source.category && `[${source.category}]`}
                </span>
              </div>
              
              {source.content && (
                <div className="citation-content">
                  {source.content}
                </div>
              )}
              
              <div className="citation-meta">
                {source.similarity && (
                  <span className="similarity-score">
                    Độ liên quan: {(source.similarity * 100).toFixed(1)}%
                  </span>
                )}
                {source.page && (
                  <span className="page-number">
                    Trang: {source.page}
                  </span>
                )}
                {source.chunk && (
                  <span className="chunk-number">
                    Chunk: {source.chunk}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SourceCitations;