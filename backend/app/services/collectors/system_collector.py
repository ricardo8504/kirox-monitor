from dataclasses import dataclass, field


@dataclass
class SystemMetrics:
    cpu_percent: float | None = None
    ram_used_mb: float | None = None
    ram_total_mb: float | None = None
    ram_percent: float | None = None
    swap_used_mb: float | None = None
    swap_total_mb: float | None = None
    swap_percent: float | None = None
    disk_partitions: list[dict] = field(default_factory=list)
    load_avg_1: float | None = None
    load_avg_5: float | None = None
    load_avg_15: float | None = None
    network_in_bytes: float | None = None
    network_out_bytes: float | None = None
    process_count: int | None = None
    cpu_temp: float | None = None


def parse_cpu(output: str) -> float | None:
    try:
        for line in output.splitlines():
            if "Cpu(s)" in line or "cpu" in line.lower():
                parts = line.split()
                for i, p in enumerate(parts):
                    if "id" in p.lower() or "idle" in p.lower():
                        idle = float(parts[i - 1].replace(",", "."))
                        return round(100.0 - idle, 1)
                for p in parts:
                    try:
                        val = float(p.replace(",", ".").rstrip("%"))
                        if 0 <= val <= 100:
                            return round(100.0 - val, 1)
                    except ValueError:
                        continue
    except Exception:  # noqa: S110
        pass
    return None


def parse_free(output: str) -> tuple[float | None, float | None, float | None,
                                      float | None, float | None, float | None]:
    ram_used = ram_total = ram_pct = swap_used = swap_total = swap_pct = None
    try:
        for line in output.splitlines():
            parts = line.split()
            if parts and parts[0].lower() in ("mem:", "memoria:"):
                if len(parts) >= 3:
                    ram_total = float(parts[1])
                    ram_used = float(parts[2])
                    ram_pct = round(ram_used / ram_total * 100, 1) if ram_total else None
            elif parts and parts[0].lower() in ("swap:", "intercambio:"):
                if len(parts) >= 3:
                    swap_total = float(parts[1])
                    swap_used = float(parts[2])
                    swap_pct = round(swap_used / swap_total * 100, 1) if swap_total else None
    except Exception:  # noqa: S110
        pass
    return ram_used, ram_total, ram_pct, swap_used, swap_total, swap_pct


def parse_df(output: str) -> list[dict]:
    partitions = []
    try:
        lines = output.strip().splitlines()
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 6:
                try:
                    pct = float(parts[4].replace("%", ""))
                    partitions.append({
                        "filesystem": parts[0],
                        "mountpoint": parts[5],
                        "size": parts[1],
                        "used": parts[2],
                        "available": parts[3],
                        "use_percent": pct,
                    })
                except (ValueError, IndexError):
                    continue
    except Exception:  # noqa: S110
        pass
    return partitions


def parse_loadavg(output: str) -> tuple[float | None, float | None, float | None]:
    try:
        parts = output.strip().split()
        return float(parts[0]), float(parts[1]), float(parts[2])
    except Exception:
        return None, None, None


def parse_proc_net_dev(output: str) -> tuple[float | None, float | None]:
    in_bytes = out_bytes = 0.0
    try:
        for line in output.splitlines()[2:]:
            parts = line.split()
            if len(parts) >= 10 and not parts[0].startswith("lo"):
                in_bytes += float(parts[1])
                out_bytes += float(parts[9])
        return in_bytes, out_bytes
    except Exception:
        return None, None


def parse_process_count(output: str) -> int | None:
    try:
        return int(output.strip())
    except Exception:
        return None


def parse_cpu_temp(output: str) -> float | None:
    try:
        values = []
        for line in output.splitlines():
            val = float(line.strip()) / 1000.0
            if val > 0:
                values.append(val)
        return round(sum(values) / len(values), 1) if values else None
    except Exception:
        return None


class SystemCollector:
    COMMANDS = {
        "cpu": "top -bn1 | grep -i 'cpu\\|Cpu'",
        "mem": "free -m",
        "df": "df -h",
        "loadavg": "cat /proc/loadavg",
        "netdev": "cat /proc/net/dev",
        "procs": "ps aux --no-headers | wc -l",
        "temp": "cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null || true",
    }

    def parse(self, outputs: dict[str, str]) -> SystemMetrics:
        m = SystemMetrics()

        if cpu_out := outputs.get("cpu"):
            m.cpu_percent = parse_cpu(cpu_out)

        if mem_out := outputs.get("mem"):
            (
                m.ram_used_mb, m.ram_total_mb, m.ram_percent,
                m.swap_used_mb, m.swap_total_mb, m.swap_percent,
            ) = parse_free(mem_out)

        if df_out := outputs.get("df"):
            m.disk_partitions = parse_df(df_out)

        if load_out := outputs.get("loadavg"):
            m.load_avg_1, m.load_avg_5, m.load_avg_15 = parse_loadavg(load_out)

        if net_out := outputs.get("netdev"):
            m.network_in_bytes, m.network_out_bytes = parse_proc_net_dev(net_out)

        if proc_out := outputs.get("procs"):
            m.process_count = parse_process_count(proc_out)

        if temp_out := outputs.get("temp"):
            m.cpu_temp = parse_cpu_temp(temp_out)

        return m
