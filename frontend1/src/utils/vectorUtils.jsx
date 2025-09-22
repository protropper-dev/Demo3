// Vector utility functions

// Calculate cosine similarity between two vectors
export const cosineSimilarity = (vector1, vector2) => {
  if (vector1.length !== vector2.length) {
    throw new Error('Vectors must have the same dimension');
  }

  let dotProduct = 0;
  let norm1 = 0;
  let norm2 = 0;

  for (let i = 0; i < vector1.length; i++) {
    dotProduct += vector1[i] * vector2[i];
    norm1 += vector1[i] * vector1[i];
    norm2 += vector2[i] * vector2[i];
  }

  norm1 = Math.sqrt(norm1);
  norm2 = Math.sqrt(norm2);

  if (norm1 === 0 || norm2 === 0) {
    return 0;
  }

  return dotProduct / (norm1 * norm2);
};

// Calculate Euclidean distance between two vectors
export const euclideanDistance = (vector1, vector2) => {
  if (vector1.length !== vector2.length) {
    throw new Error('Vectors must have the same dimension');
  }

  let sum = 0;
  for (let i = 0; i < vector1.length; i++) {
    const diff = vector1[i] - vector2[i];
    sum += diff * diff;
  }

  return Math.sqrt(sum);
};

// Calculate Manhattan distance between two vectors
export const manhattanDistance = (vector1, vector2) => {
  if (vector1.length !== vector2.length) {
    throw new Error('Vectors must have the same dimension');
  }

  let sum = 0;
  for (let i = 0; i < vector1.length; i++) {
    sum += Math.abs(vector1[i] - vector2[i]);
  }

  return sum;
};

// Normalize vector to unit length
export const normalizeVector = (vector) => {
  const norm = Math.sqrt(vector.reduce((sum, val) => sum + val * val, 0));
  if (norm === 0) return vector;
  return vector.map(val => val / norm);
};

// Calculate vector magnitude
export const vectorMagnitude = (vector) => {
  return Math.sqrt(vector.reduce((sum, val) => sum + val * val, 0));
};

// Add two vectors
export const addVectors = (vector1, vector2) => {
  if (vector1.length !== vector2.length) {
    throw new Error('Vectors must have the same dimension');
  }

  return vector1.map((val, i) => val + vector2[i]);
};

// Subtract two vectors
export const subtractVectors = (vector1, vector2) => {
  if (vector1.length !== vector2.length) {
    throw new Error('Vectors must have the same dimension');
  }

  return vector1.map((val, i) => val - vector2[i]);
};

// Multiply vector by scalar
export const multiplyVector = (vector, scalar) => {
  return vector.map(val => val * scalar);
};

// Calculate dot product of two vectors
export const dotProduct = (vector1, vector2) => {
  if (vector1.length !== vector2.length) {
    throw new Error('Vectors must have the same dimension');
  }

  return vector1.reduce((sum, val, i) => sum + val * vector2[i], 0);
};

// Find nearest neighbors using cosine similarity
export const findNearestNeighbors = (queryVector, vectors, topK = 5) => {
  const similarities = vectors.map((vector, index) => ({
    index,
    similarity: cosineSimilarity(queryVector, vector)
  }));

  return similarities
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, topK);
};

// Find nearest neighbors using Euclidean distance
export const findNearestNeighborsEuclidean = (queryVector, vectors, topK = 5) => {
  const distances = vectors.map((vector, index) => ({
    index,
    distance: euclideanDistance(queryVector, vector)
  }));

  return distances
    .sort((a, b) => a.distance - b.distance)
    .slice(0, topK);
};

// Calculate centroid of vectors
export const calculateCentroid = (vectors) => {
  if (vectors.length === 0) return null;

  const dimensions = vectors[0].length;
  const centroid = new Array(dimensions).fill(0);

  for (const vector of vectors) {
    for (let i = 0; i < dimensions; i++) {
      centroid[i] += vector[i];
    }
  }

  for (let i = 0; i < dimensions; i++) {
    centroid[i] /= vectors.length;
  }

  return centroid;
};

// Calculate variance of vectors
export const calculateVariance = (vectors) => {
  if (vectors.length === 0) return null;

  const centroid = calculateCentroid(vectors);
  const dimensions = vectors[0].length;
  const variance = new Array(dimensions).fill(0);

  for (const vector of vectors) {
    for (let i = 0; i < dimensions; i++) {
      const diff = vector[i] - centroid[i];
      variance[i] += diff * diff;
    }
  }

  for (let i = 0; i < dimensions; i++) {
    variance[i] /= vectors.length;
  }

  return variance;
};

// Calculate standard deviation of vectors
export const calculateStandardDeviation = (vectors) => {
  const variance = calculateVariance(vectors);
  if (!variance) return null;

  return variance.map(val => Math.sqrt(val));
};

// Calculate mean of vectors
export const calculateMean = (vectors) => {
  return calculateCentroid(vectors);
};

// Calculate median of vectors
export const calculateMedian = (vectors) => {
  if (vectors.length === 0) return null;

  const dimensions = vectors[0].length;
  const median = new Array(dimensions).fill(0);

  for (let i = 0; i < dimensions; i++) {
    const values = vectors.map(vector => vector[i]).sort((a, b) => a - b);
    const mid = Math.floor(values.length / 2);
    median[i] = values.length % 2 === 0 ? 
      (values[mid - 1] + values[mid]) / 2 : 
      values[mid];
  }

  return median;
};

// Calculate range of vectors
export const calculateRange = (vectors) => {
  if (vectors.length === 0) return null;

  const dimensions = vectors[0].length;
  const min = new Array(dimensions).fill(Infinity);
  const max = new Array(dimensions).fill(-Infinity);

  for (const vector of vectors) {
    for (let i = 0; i < dimensions; i++) {
      min[i] = Math.min(min[i], vector[i]);
      max[i] = Math.max(max[i], vector[i]);
    }
  }

  return {
    min,
    max,
    range: max.map((val, i) => val - min[i])
  };
};

// Calculate correlation between two vectors
export const calculateCorrelation = (vector1, vector2) => {
  if (vector1.length !== vector2.length) {
    throw new Error('Vectors must have the same dimension');
  }

  const n = vector1.length;
  const mean1 = vector1.reduce((sum, val) => sum + val, 0) / n;
  const mean2 = vector2.reduce((sum, val) => sum + val, 0) / n;

  let numerator = 0;
  let sumSq1 = 0;
  let sumSq2 = 0;

  for (let i = 0; i < n; i++) {
    const diff1 = vector1[i] - mean1;
    const diff2 = vector2[i] - mean2;
    numerator += diff1 * diff2;
    sumSq1 += diff1 * diff1;
    sumSq2 += diff2 * diff2;
  }

  const denominator = Math.sqrt(sumSq1 * sumSq2);
  return denominator === 0 ? 0 : numerator / denominator;
};

// Calculate angle between two vectors
export const calculateAngle = (vector1, vector2) => {
  const similarity = cosineSimilarity(vector1, vector2);
  return Math.acos(Math.max(-1, Math.min(1, similarity))) * (180 / Math.PI);
};

// Check if vectors are orthogonal
export const areOrthogonal = (vector1, vector2, tolerance = 1e-10) => {
  return Math.abs(dotProduct(vector1, vector2)) < tolerance;
};

// Check if vectors are parallel
export const areParallel = (vector1, vector2, tolerance = 1e-10) => {
  const similarity = Math.abs(cosineSimilarity(vector1, vector2));
  return Math.abs(similarity - 1) < tolerance;
};

// Calculate vector statistics
export const calculateVectorStats = (vectors) => {
  if (vectors.length === 0) return null;

  return {
    count: vectors.length,
    dimensions: vectors[0].length,
    mean: calculateMean(vectors),
    median: calculateMedian(vectors),
    variance: calculateVariance(vectors),
    standardDeviation: calculateStandardDeviation(vectors),
    range: calculateRange(vectors)
  };
};
