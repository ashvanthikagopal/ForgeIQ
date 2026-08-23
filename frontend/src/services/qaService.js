import api from './api';

export const getQASummary = () => {
  return api.get('/qa/summary');
};

export const getQAReviews = (params) => {
  return api.get('/qa/reviews', { params });
};
