import { useQuery } from "@tanstack/react-query";
import { useCallback } from "react";
import { metricsApi } from "@/api/metrics";
import { useServerStore } from "@/stores/serverStore";
import { useAuthStore } from "@/stores/authStore";
import { useServerMetricsWs } from "./useWebSocket";
import type { WsMessage } from "@/types";

export function useLatestMetrics(serverId: string) {
  return useQuery({
    queryKey: ["metrics", serverId, "latest"],
    queryFn: () => metricsApi.getLatest(serverId),
    staleTime: 15_000,
    refetchInterval: 60_000,
  });
}

export function useLiveMetrics(serverId: string) {
  const updateLiveMetrics = useServerStore((s) => s.updateLiveMetrics);
  const liveMetrics = useServerStore((s) => s.liveMetrics[serverId]);
  const accessToken = useAuthStore((s) => s.accessToken);

  const onMessage = useCallback(
    (msg: WsMessage) => {
      if (msg.type === "metrics" && msg.server_id === serverId) {
        updateLiveMetrics(serverId, msg.data);
      }
    },
    [serverId, updateLiveMetrics],
  );

  useServerMetricsWs(serverId, accessToken ?? "", {
    onMessage,
    enabled: !!accessToken,
  });

  return liveMetrics;
}
