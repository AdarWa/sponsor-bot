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
export const getWebsites = () => apiFetch('/api/dashboard/websites');

export const createWebsite = (payload) =>
  apiFetch('/api/dashboard/websites', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

export const scrapeWebsites = () =>
  apiFetch('/api/dashboard/websites/scrape', {
    method: 'POST'
  });

export const deleteWebsite = (id) =>
  apiFetch(`/api/dashboard/websites/${id}`, {
    method: 'DELETE',
  });

export const getSearchQueries = () => apiFetch('/api/dashboard/queries');

export const createSearchQuery = (payload) =>
  apiFetch('/api/dashboard/queries', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

export const scrapeSearchQueries = () =>
  apiFetch('/api/dashboard/queries/scrape', {
    method: 'POST'
  });

export const deleteSearchQuery = (id) =>
  apiFetch(`/api/dashboard/queries/${id}`, {
    method: 'DELETE',
  });

export const getEmailTemplate = () => apiFetch('/api/dashboard/email-template');

export const updateEmailTemplate = (payload) =>
  apiFetch('/api/dashboard/email-template', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

export const sendEmailCampaign = () =>
  apiFetch('/api/dashboard/email/send', {
    method: 'POST'
  });

export const getEmails = () => apiFetch('/api/dashboard/emails');

export const addEmail = (payload) =>
  apiFetch('/api/dashboard/emails', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

export const deleteEmail = (id) =>
  apiFetch(`/api/dashboard/emails/${id}`, {
    method: 'DELETE',
  });
