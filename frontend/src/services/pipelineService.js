import api from './api';

export const runPipeline = () => {
  return api.post('/pipeline/run');
};

export const getPipelineStatus = () => {
  return api.get('/pipeline/status');
};

export const getPipelineResults = () => {
  return api.get('/pipeline/results');
};

export const downloadResults = async (format = 'csv') => {
  // Use axios directly or through our api with blob response type
  const response = await api.get(`/pipeline/export?format=${format}`, { responseType: 'blob' });
  
  // Need to handle the blob download in browser
  const url = window.URL.createObjectURL(new Blob([response]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `forgeiq_export.${format}`);
  document.body.appendChild(link);
  link.click();
  link.parentNode.removeChild(link);
  
  return true;
};
