/*
 * @LastEditors: biz
 */

/**
 * Format elapsed time from milliseconds to readable string
 */
export const formatElapsedTime = (elapsedTimeMs: number): string => {
  if (!elapsedTimeMs) return '0s';
  
  const seconds = Math.floor(elapsedTimeMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  } else {
    return `${seconds}s`;
  }
};

/**
 * Get tag color based on node status
 */
export const getTagColor = (status: string): string => {
  switch (status) {
    case 'success':
      return 'success';
    case 'fail':
      return 'error';
    case 'pending':
      return 'processing';
    case 'running':
      return 'warning';
    case 'waitforhuman':
      return 'blue';
    default:
      return 'default';
  }
};

/**
 * Check if a value is a valid JSON string
 */
export const isValidJsonString = (value: string): boolean => {
  try {
    JSON.parse(value);
    return true;
  } catch (e) {
    return false;
  }
};

/**
 * Format JSON string with proper indentation
 */
export const formatJsonString = (value: string): string => {
  try {
    return JSON.stringify(JSON.parse(value), null, 2);
  } catch (e) {
    return value;
  }
}; 