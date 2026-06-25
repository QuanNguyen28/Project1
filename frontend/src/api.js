import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const api = axios.create({ baseURL });

api.interceptors.request.use((config) => {
  const t = localStorage.getItem("access_token");
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem("access_token");
    }
    return Promise.reject(err);
  },
);

export const AuthAPI = {
  async login(username, password) {
    const body = new URLSearchParams();
    body.append("username", username);
    body.append("password", password);
    const { data } = await api.post("/auth/token", body, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    localStorage.setItem("access_token", data.access_token);
    return data;
  },
  async me() {
    const { data } = await api.get("/auth/me");
    return data;
  },
};

export const JDAPI = {
  async generateJD(payload) {
    const { data } = await api.post("/v1/jd/generate", payload);
    return data;
  },
  async generate(payload) {
    return this.generateJD(payload);
  },
  async update(payload) {
    const { data } = await api.put("/v1/jd/update", payload);
    return data;
  },
  async versions(jdId) {
    const { data } = await api.get(`/v1/jd/version-history/${jdId}`);
    return data;
  },
  async exportJD(jdId, format = "pdf") {
    const res = await api.get(`/v1/jd/export/${jdId}?format=${format}`, {
      responseType: "blob",
    });
    return res.data;
  },
  async export(jdId, format = "pdf") {
    return this.exportJD(jdId, format);
  },
};

export const RetrieverAPI = {
  async similar(query, top_k = 5) {
    const { data } = await api.post("/v1/retrieve/similar", { query, top_k });
    return data;
  },
  async simple(query, top_k = 5) {
    const { data } = await api.post("/v1/retrieve", { query, top_k });
    return data;
  },
};

export const InterviewAPI = {
  async generate(payload) {
    const { data } = await api.post("/v1/interview/generate", payload);
    return data;
  },
};

export const RolesAPI = {
  async list() {
    const { data } = await api.get("/v1/roles/list");
    return data;
  },
};

export const improveJD = (payload) => api.post("/v1/jd/improve", payload);

export const suggestJD = (payload) => api.post("/v1/jd/suggest", payload);

export default api;
