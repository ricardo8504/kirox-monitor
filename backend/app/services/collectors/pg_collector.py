from dataclasses import dataclass


@dataclass
class PgMetrics:
    connections_active: int = 0
    slow_queries: int = 0
    locks: int = 0
    deadlocks: int = 0
    db_size_mb: float = 0.0


QUERIES = {
    "connections": "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';",
    "slow_queries": (
        "SELECT count(*) FROM pg_stat_activity WHERE state = 'active' "
        "AND now() - pg_stat_activity.query_start > interval '5 seconds';"
    ),
    "locks": "SELECT count(*) FROM pg_locks WHERE NOT granted;",
    "deadlocks": "SELECT sum(deadlocks) FROM pg_stat_database;",
    "db_size": "SELECT pg_database_size(current_database()) / 1048576.0;",
}

def get_commands(
    db_port: int = 5432,
    db_user: str = "postgres",
    db_password: str | None = None,
) -> dict[str, str]:
    env = f"PGPASSWORD={db_password} " if db_password else ""
    opts = f"-U {db_user} -p {db_port}"
    return {
        k: f"{env}psql {opts} -t -A -c \"{v}\" 2>/dev/null"
        for k, v in QUERIES.items()
    }


def _parse_int(output: str) -> int:
    try:
        return int(output.strip())
    except Exception:
        return 0


def _parse_float(output: str) -> float:
    try:
        return round(float(output.strip()), 2)
    except Exception:
        return 0.0


class PgCollector:
    def parse(self, outputs: dict[str, str]) -> PgMetrics:
        return PgMetrics(
            connections_active=_parse_int(outputs.get("connections", "")),
            slow_queries=_parse_int(outputs.get("slow_queries", "")),
            locks=_parse_int(outputs.get("locks", "")),
            deadlocks=_parse_int(outputs.get("deadlocks", "")),
            db_size_mb=_parse_float(outputs.get("db_size", "")),
        )
