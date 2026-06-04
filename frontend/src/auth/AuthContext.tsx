import { createContext, PropsWithChildren, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { apiRequest } from "../api/client";
import { TOKEN_STORAGE_KEY } from "../api/config";
import { TokenResponse, User, UserProfile } from "../api/types";

type RegisterPayload = {
  email: string;
  password: string;
};

type ProfilePayload = {
  height_cm?: string;
  current_weight_kg?: string;
  goal?: string;
  training_level?: string;
  preferred_mode?: "home" | "gym";
  target_weekly_weight_loss_kg?: string;
  target_protein_g?: string;
  target_calories?: number;
};

type AuthContextValue = {
  token: string | null;
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  createProfile: (payload: ProfilePayload) => Promise<UserProfile>;
  updateProfile: (payload: ProfilePayload) => Promise<UserProfile>;
  refreshUser: () => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: PropsWithChildren) {
  const [token, setToken] = useState<string | null>(() => window.localStorage.getItem(TOKEN_STORAGE_KEY));
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(Boolean(token));

  const persistToken = useCallback((nextToken: string | null) => {
    setToken(nextToken);
    if (nextToken) {
      window.localStorage.setItem(TOKEN_STORAGE_KEY, nextToken);
    } else {
      window.localStorage.removeItem(TOKEN_STORAGE_KEY);
    }
  }, []);

  const refreshUser = useCallback(async () => {
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    try {
      const currentUser = await apiRequest<User>("/api/v1/me", { token });
      setUser(currentUser);
    } catch {
      persistToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, [persistToken, token]);

  useEffect(() => {
    void refreshUser();
  }, [refreshUser]);

  const login = useCallback(
    async (email: string, password: string) => {
      const response = await apiRequest<TokenResponse>("/api/v1/auth/login", {
        method: "POST",
        body: { email, password },
      });
      persistToken(response.access_token);
      const currentUser = await apiRequest<User>("/api/v1/me", { token: response.access_token });
      setUser(currentUser);
    },
    [persistToken],
  );

  const register = useCallback(
    async (payload: RegisterPayload) => {
      await apiRequest<User>("/api/v1/auth/register", {
        method: "POST",
        body: payload,
      });
      await login(payload.email, payload.password);
    },
    [login],
  );

  const createProfile = useCallback(
    async (payload: ProfilePayload) => {
      const profile = await apiRequest<UserProfile>("/api/v1/me/profile", {
        method: "POST",
        body: payload,
        token,
      });
      await refreshUser();
      return profile;
    },
    [refreshUser, token],
  );

  const updateProfile = useCallback(
    async (payload: ProfilePayload) => {
      const profile = await apiRequest<UserProfile>("/api/v1/me/profile", {
        method: "PUT",
        body: payload,
        token,
      });
      await refreshUser();
      return profile;
    },
    [refreshUser, token],
  );

  const logout = useCallback(() => {
    persistToken(null);
    setUser(null);
  }, [persistToken]);

  const value = useMemo(
    () => ({ token, user, isLoading, login, register, createProfile, updateProfile, refreshUser, logout }),
    [token, user, isLoading, login, register, createProfile, updateProfile, refreshUser, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
