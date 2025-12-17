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

export const listUsers = (token) =>
  apiFetch('/api/admin/users', {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

export const verifyUser = (userId, token) =>
  apiFetch(`/api/admin/users/${userId}/verify`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

export const deleteUser = (userId, token) =>
  apiFetch(`/api/admin/users/${userId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

export const getWebsites = (token) =>
  apiFetch('/api/dashboard/websites', {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

export const createWebsite = (payload, token) =>
  apiFetch('/api/dashboard/websites', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

export const scrapeWebsites = (token) =>
  apiFetch('/api/dashboard/websites/scrape', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

export const deleteWebsite = (id, token) =>
  apiFetch(`/api/dashboard/websites/${id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

export const getSearchQueries = (token) =>
  apiFetch('/api/dashboard/queries', {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

export const createSearchQuery = (payload, token) =>
  apiFetch('/api/dashboard/queries', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

export const scrapeSearchQueries = (token) =>
  apiFetch('/api/dashboard/queries/scrape', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

export const deleteSearchQuery = (id, token) =>
  apiFetch(`/api/dashboard/queries/${id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

export const getEmailTemplate = (token) =>
  apiFetch('/api/dashboard/email-template', {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

export const updateEmailTemplate = (payload, token) =>
  apiFetch('/api/dashboard/email-template', {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

export const sendEmailCampaign = (token) =>
  apiFetch('/api/dashboard/email/send', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

export const getEmails = (token) =>
  apiFetch('/api/dashboard/emails', {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

export const addEmail = (payload, token) =>
  apiFetch('/api/dashboard/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

export const deleteEmail = (id, token) =>
  apiFetch(`/api/dashboard/emails/${id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
