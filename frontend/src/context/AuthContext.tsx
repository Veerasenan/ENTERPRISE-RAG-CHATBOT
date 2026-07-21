import React, { createContext, useContext, useEffect, useState } from "react";
import { login as loginRequest } from "../api/authApi";
import type { AuthUser } from "../types";

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const STORAGE_TOKEN_KEY = "access_token";
const STORAGE_USER_KEY = "auth_user";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  // Restore session on page reload (sessionStorage clears when the tab closes,
  // which is the safer choice for auth tokens vs. localStorage).
  useEffect(() => {
    const token = sessionStorage.getItem(STORAGE_TOKEN_KEY);
    const rawUser = sessionStorage.getItem(STORAGE_USER_KEY);
    if (token && rawUser) {
      setUser(JSON.parse(rawUser));
    }
    setLoading(false);
  }, []);

  async function login(email: string, password: string) {
    const res = await loginRequest(email, password);
    const authUser: AuthUser = {
      userId: res.user_id,
      email,
      fullName: res.full_name,
      role: res.role,
      token: res.access_token,
    };
    sessionStorage.setItem(STORAGE_TOKEN_KEY, res.access_token);
    sessionStorage.setItem(STORAGE_USER_KEY, JSON.stringify(authUser));
    setUser(authUser);
  }

  function logout() {
    sessionStorage.removeItem(STORAGE_TOKEN_KEY);
    sessionStorage.removeItem(STORAGE_USER_KEY);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
