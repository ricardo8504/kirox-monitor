import { apiClient } from "./client";
import type { LoginRequest, TokenPair, User } from "@/types";

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<TokenPair>("/auth/login", data).then((r) => r.data),

  refresh: (refreshToken: string) =>
    apiClient
      .post<TokenPair>("/auth/refresh", { refresh_token: refreshToken })
      .then((r) => r.data),

  me: () => apiClient.get<User>("/auth/me").then((r) => r.data),
};
