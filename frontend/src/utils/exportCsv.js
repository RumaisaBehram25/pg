/**
 * Utility functions for exporting data to CSV
 */

/**
 * Convert an array of objects to CSV string
 * @param {Array} data - Array of objects to convert
 * @param {Array} columns - Array of column definitions { key, header }
 * @returns {string} CSV formatted string
 */
export const arrayToCsv = (data, columns) => {
  if (!data || data.length === 0) return '';
  
  // Create header row
  const headers = columns.map(col => `"${col.header}"`).join(',');
  
  // Create data rows
  const rows = data.map(item => {
    return columns.map(col => {
      let value = item[col.key];
      
      // Handle null/undefined
      if (value === null || value === undefined) {
        value = '';
      }
      
      // Handle objects (stringify)
      if (typeof value === 'object') {
        value = JSON.stringify(value);
      }
      
      // Escape quotes and wrap in quotes
      value = String(value).replace(/"/g, '""');
      return `"${value}"`;
    }).join(',');
  });
  
  return [headers, ...rows].join('\n');
};

/**
 * Download a CSV file
 * @param {string} csvContent - CSV formatted string
 * @param {string} filename - Name of the file to download
 */
export const downloadCsv = (csvContent, filename) => {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  
  if (navigator.msSaveBlob) {
    // IE 10+
    navigator.msSaveBlob(blob, filename);
  } else {
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.download = filename;
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
};

/**
 * Export data to CSV and trigger download
 * @param {Array} data - Array of objects to export
 * @param {Array} columns - Column definitions
 * @param {string} filename - Filename for the download
 */
export const exportToCsv = (data, columns, filename) => {
  const csvContent = arrayToCsv(data, columns);
  downloadCsv(csvContent, filename);
};

/**
 * Get formatted date string for filenames
 * @returns {string} Formatted date string (YYYY-MM-DD)
 */
export const getDateString = () => {
  const now = new Date();
  return now.toISOString().split('T')[0];
};


