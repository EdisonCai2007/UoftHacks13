import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const login = async (username, password) => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  const response = await api.post('/token', formData);
  return response.data;
};

export const register = async (username, email, password) => {
  const response = await api.post('/register', { username, email, password });
  return response.data;
};

export const getMe = async () => {
  const response = await api.get('/users/me');
  return response.data;
};

export const getSessions = async () => {
  const response = await api.get('/sessions');
  return response.data;
};

export default api;
