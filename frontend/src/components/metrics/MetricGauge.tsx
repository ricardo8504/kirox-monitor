import ReactECharts from "echarts-for-react";

interface MetricGaugeProps {
  value: number;
  label: string;
  unit?: string;
  warning?: number;
  critical?: number;
  height?: number;
}

export function MetricGauge({
  value,
  label,
  unit = "%",
  warning = 75,
  critical = 90,
  height = 180,
}: MetricGaugeProps) {
  const color =
    value >= critical
      ? "#ef4444"
      : value >= warning
        ? "#f59e0b"
        : "#22c55e";

  const option = {
    backgroundColor: "transparent",
    series: [
      {
        type: "gauge",
        startAngle: 205,
        endAngle: -25,
        min: 0,
        max: 100,
        radius: "85%",
        progress: { show: true, width: 10, itemStyle: { color } },
        axisLine: { lineStyle: { width: 10, color: [[1, "#374151"]] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: false },
        detail: {
          offsetCenter: [0, "5%"],
          fontSize: 20,
          fontWeight: "bold",
          color,
          formatter: `{value}${unit}`,
        },
        title: {
          offsetCenter: [0, "30%"],
          fontSize: 11,
          color: "#9ca3af",
        },
        data: [{ value: Math.round(value), name: label }],
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
