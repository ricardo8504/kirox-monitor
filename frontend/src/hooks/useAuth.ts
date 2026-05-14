import { useCallback } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { authApi } from "@/api/auth";
import { setTokens } from "@/api/client";
import { useAuthStore } from "@/stores/authStore";
import type { LoginRequest } from "@/types";


export function useAuth() {
  const { user, isAuthenticated, setAuth, logout: storeLogout } = useAuthStore();
  const qc = useQueryClient();

  const loginMutation = useMutation({
    mutationFn: async (data: LoginRequest) => {
      const tokens = await authApi.login(data);
      setTokens(tokens.access_token, tokens.refresh_token);
      const me = await authApi.me();
      return { tokens, me };
    },
    onSuccess: ({ tokens, me }) => {
      setAuth(me, tokens.access_token, tokens.refresh_token);
    },
  });

  const logout = useCallback(() => {
    storeLogout();
    qc.clear();
  }, [storeLogout, qc]);

  return {
    user,
    isAuthenticated,
    login: loginMutation.mutateAsync,
    loginError: loginMutation.error,
    isLoggingIn: loginMutation.isPending,
    logout,
  };
}

export function useMe() {
  const { setUser, isAuthenticated } = useAuthStore();

  return useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const user = await authApi.me();
      setUser(user);
      return user;
    },
    enabled: isAuthenticated,
    staleTime: 5 * 60_000,
  });
}
