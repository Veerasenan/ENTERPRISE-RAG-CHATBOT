import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

/**
 * Attach the JWT to every outgoing request automatically.
 * Token is read fresh from sessionStorage on each call (not held in a closure),
 * so logging in/out is picked up immediately without recreating the client.
 */
apiClient.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      // Token invalid/expired — force back to login.
      sessionStorage.removeItem("access_token");
      sessionStorage.removeItem("auth_user");
      window.location.href = "/login";
    }
    const message = error?.response?.data?.detail || error?.message || "Unexpected error occurred";
    return Promise.reject(new Error(message));
  }
);
