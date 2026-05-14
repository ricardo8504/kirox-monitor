import ReactECharts from "echarts-for-react";
import type { MetricResponse } from "@/types";

interface MetricChartProps {
  metrics: MetricResponse[];
  label: string;
  color?: string;
  unit?: string;
  height?: number;
}

export function MetricChart({
  metrics,
  label,
  color = "#3b82f6",
  unit = "%",
  height = 160,
}: MetricChartProps) {
  const timestamps = metrics.map((m) =>
    new Date(m.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
  );
  const values = metrics.map((m) => Number(m.value.toFixed(1)));

  const option = {
    backgroundColor: "transparent",
    grid: { top: 10, right: 10, bottom: 24, left: 40 },
    tooltip: {
      trigger: "axis",
      formatter: (params: { name: string; value: number }[]) =>
        `${params[0]?.name ?? ""}<br/>${label}: <b>${params[0]?.value ?? 0}${unit}</b>`,
    },
    xAxis: {
      type: "category",
      data: timestamps,
      axisLine: { lineStyle: { color: "#374151" } },
      axisLabel: { color: "#6b7280", fontSize: 10 },
      splitLine: { show: false },
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 100,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: "#6b7280", fontSize: 10, formatter: `{value}${unit}` },
      splitLine: { lineStyle: { color: "#1f2937" } },
    },
    series: [
      {
        type: "line",
        data: values,
        smooth: true,
        symbol: "none",
        lineStyle: { color, width: 2 },
        areaStyle: { color, opacity: 0.1 },
      },
    ],
  };

  return (
    <ReactECharts
      option={option}
      style={{ height, width: "100%" }}
      opts={{ renderer: "svg" }}
    />
  );
}
