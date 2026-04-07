import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

// Stores
export const fetchStores = () => api.get("/stores/");
export const createStore = (data) => api.post("/stores/", data);
export const deleteStore = (id) => api.delete(`/stores/${id}/`);
export const syncStore = (id) => api.post(`/stores/${id}/sync/`);
export const fetchPages = (storeId) => api.get(`/stores/${storeId}/pages/`);
export const updatePage = (storeId, pageId, data) =>
  api.patch(`/stores/${storeId}/pages/${pageId}/`, data);

// Keywords
export const fetchKeywords = (storeId) =>
  api.get(`/keywords/?store=${storeId}`);
export const createKeyword = (data) => api.post("/keywords/", data);
export const researchKeywords = (keyword) =>
  api.post("/keywords/research/", { keyword });
export const fetchRankHistory = (keywordId) =>
  api.get(`/keywords/${keywordId}/rank-history/`);

// Audits
export const triggerAudit = (storeId) =>
  api.post("/audits/trigger/", { store_id: storeId });
export const fetchAuditRuns = (storeId) =>
  api.get(`/audits/runs/?store=${storeId}`);

// AI
export const generateMeta = (pageId, targetKeywords) =>
  api.post("/ai/generate-meta/", { page_id: pageId, target_keywords: targetKeywords });
export const generateAltText = (pageId) =>
  api.post("/ai/generate-alt/", { page_id: pageId });
export const scoreContent = (pageId, targetKeywords) =>
  api.post("/ai/score-content/", { page_id: pageId, target_keywords: targetKeywords });
export const bulkGenerateMeta = (pageIds) =>
  api.post("/ai/bulk-generate-meta/", { page_ids: pageIds });

// Dashboard
export const fetchDashboard = () => api.get("/dashboard/");
export const fetchStoreDashboard = (storeId) =>
  api.get(`/dashboard/${storeId}/`);

// Backlinks
export const fetchBacklinks = (storeId) =>
  api.get(`/backlinks/?store_id=${storeId}`);
export const fetchBacklinkSummary = (storeId) =>
  api.get(`/backlinks/summary/?store_id=${storeId}`);
export const fetchBacklinkSnapshot = (storeId) =>
  api.get(`/backlinks/snapshot/?store_id=${storeId}`);
export const refreshBacklinks = (storeId) =>
  api.post("/backlinks/refresh/", { store_id: storeId });
export const fetchProspects = (storeId) =>
  api.get(`/backlinks/prospects/?store_id=${storeId}`);
export const createProspect = (data) =>
  api.post("/backlinks/prospects/", data);
export const suggestProspects = (storeId) =>
  api.post("/backlinks/prospects/suggest/", { store_id: storeId });
export const sendProspectEmail = (prospectId) =>
  api.post(`/backlinks/prospects/${prospectId}/email/`);
export const updateProspectStatus = (prospectId, prospectStatus) =>
  api.patch(`/backlinks/prospects/${prospectId}/status/`, { status: prospectStatus });
export const fetchCampaigns = (storeId) =>
  api.get(`/backlinks/campaigns/?store_id=${storeId}`);
export const fetchEmailConfig = (storeId) =>
  api.get(`/backlinks/email-config/?store_id=${storeId}`);
export const saveEmailConfig = (data) =>
  api.post("/backlinks/email-config/", data);
export const updateEmailConfig = (id, data) =>
  api.put(`/backlinks/email-config/${id}/`, data);
export const getGmailAuthUrl = (storeId) =>
  api.get(`/backlinks/email-config/gmail/auth-url/?store_id=${storeId}`);

export default api;
