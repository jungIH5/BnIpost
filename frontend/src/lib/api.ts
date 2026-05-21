import axios from "axios";
import { getToken, logout } from "./auth";
import type { User, PostResult, HistoryItem } from "@/types";

const JAVA_URL = process.env.NEXT_PUBLIC_JAVA_URL || "http://localhost:8080";
const PYTHON_URL = process.env.NEXT_PUBLIC_PYTHON_URL || "http://localhost:8000";

const javaApi = axios.create({ baseURL: JAVA_URL });
const pythonApi = axios.create({ baseURL: PYTHON_URL });

function authHeader() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// Intercept 401 responses and logout
[javaApi, pythonApi].forEach((api) => {
  api.interceptors.response.use(
    (res) => res,
    (err) => {
      if (err.response?.status === 401) logout();
      return Promise.reject(err);
    }
  );
});

export const authApi = {
  getNaverLoginUrl: () => `${JAVA_URL}/auth/naver`,
  getInstagramLoginUrl: () => `${JAVA_URL}/auth/instagram`,
};

export const userApi = {
  getMe: async (): Promise<User> => {
    const res = await javaApi.get("/api/users/me", { headers: authHeader() });
    return res.data;
  },
};

export const postApi = {
  generate: async (formData: FormData): Promise<PostResult> => {
    const res = await pythonApi.post("/api/posts/generate", formData, {
      headers: { ...authHeader(), "Content-Type": "multipart/form-data" },
    });
    return res.data;
  },

  preview: async (formData: FormData): Promise<PostResult> => {
    const res = await pythonApi.post("/api/posts/preview", formData, {
      headers: { ...authHeader(), "Content-Type": "multipart/form-data" },
    });
    return res.data;
  },
};

export const historyApi = {
  getHistory: async (page = 1, platform?: string): Promise<HistoryItem[]> => {
    const params: Record<string, unknown> = { page, size: 10 };
    if (platform) params.platform = platform;
    const res = await pythonApi.get("/api/history/", {
      headers: authHeader(),
      params,
    });
    return res.data;
  },
};
