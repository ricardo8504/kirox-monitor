from dataclasses import dataclass


@dataclass
class OdooMetrics:
    workers_active: int = 0
    processes_hung: int = 0
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    response_time_ms: float | None = None
    requests_concurrent: int = 0


def get_commands(odoo_port: int = 8069) -> dict[str, str]:
    return {
        "procs": "ps aux | grep -E 'openerp|odoo' | grep -v grep",
        "mem": "ps aux | grep -E 'openerp|odoo' | grep -v grep | awk '{sum+=$6} END {print sum+0}'",
        "cpu": "ps aux | grep -E 'openerp|odoo' | grep -v grep | awk '{sum+=$3} END {print sum+0}'",
        "http": (
            f"curl -s -o /dev/null -w '%{{time_total}}' http://localhost:{odoo_port} "
            "--connect-timeout 5 2>/dev/null || echo ''"
        ),
    }

_HUNG_CPU_THRESHOLD = 90.0


def parse_processes(output: str) -> tuple[int, int]:
    workers = 0
    hung = 0
    for line in output.strip().splitlines():
        if not line.strip():
            continue
        workers += 1
        try:
            parts = line.split()
            cpu = float(parts[2])
            if cpu >= _HUNG_CPU_THRESHOLD:
                hung += 1
        except (IndexError, ValueError):
            pass
    return workers, hung


def parse_memory_kb(output: str) -> float:
    try:
        return float(output.strip()) / 1024.0
    except Exception:
        return 0.0


def parse_cpu_sum(output: str) -> float:
    try:
        return float(output.strip())
    except Exception:
        return 0.0


def parse_http_time(output: str) -> float | None:
    try:
        val = float(output.strip())
        return round(val * 1000, 1) if val > 0 else None
    except Exception:
        return None


class OdooCollector:
    def parse(self, outputs: dict[str, str]) -> OdooMetrics:
        m = OdooMetrics()

        if proc_out := outputs.get("procs"):
            m.workers_active, m.processes_hung = parse_processes(proc_out)

        if mem_out := outputs.get("mem"):
            m.memory_mb = parse_memory_kb(mem_out)

        if cpu_out := outputs.get("cpu"):
            m.cpu_percent = parse_cpu_sum(cpu_out)

        if http_out := outputs.get("http"):
            m.response_time_ms = parse_http_time(http_out)

        return m
