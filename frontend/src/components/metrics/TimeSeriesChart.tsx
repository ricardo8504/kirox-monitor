import ReactECharts from "echarts-for-react";

interface DataPoint {
  timestamp: string;
  value: number;
}

interface TimeSeriesChartProps {
  data: DataPoint[];
  label: string;
  color?: string;
  unit?: string;
  height?: number;
  yMax?: number;
}

export function TimeSeriesChart({
  data,
  label,
  color = "#3b82f6",
  unit = "",
  height = 160,
  yMax,
}: TimeSeriesChartProps) {
  const timestamps = data.map((d) =>
    new Date(d.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
  );
  const values = data.map((d) => Number(d.value.toFixed(1)));

  const option = {
    backgroundColor: "transparent",
    grid: { top: 10, right: 10, bottom: 24, left: 44 },
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
      ...(yMax !== undefined ? { max: yMax } : {}),
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
