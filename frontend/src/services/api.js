const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000';

export const apiFetch = async (path, options = {}) => {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const errorPayload = await response.json().catch(() => ({ message: 'Unknown error' }));
    const error = new Error(errorPayload.detail || errorPayload.message || response.statusText);
    error.status = response.status;
    error.payload = errorPayload;
    throw error;
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
};

export const login = async (email, password) => {
  const body = new URLSearchParams();
  body.append('username', email);
  body.append('password', password);
  return apiFetch('/api/auth/jwt/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body
  });
};

export const register = (payload) =>
  apiFetch('/api/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

export const getProfile = (token) =>
  apiFetch('/api/me', {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
