from dataclasses import dataclass


@dataclass
class PgMetrics:
    connections_active: int = 0
    slow_queries: int = 0
    locks: int = 0
    deadlocks: int = 0
    db_size_mb: float = 0.0


QUERIES = {
    # Total de conexiones activas (excluye idle y conexiones de sistema)
    "connections": (
        "SELECT count(*) FROM pg_stat_activity "
        "WHERE state IS NOT NULL AND datname NOT IN ('postgres','template0','template1');"
    ),
    # Consultas lentas (>5 s) en cualquier estado activo
    "slow_queries": (
        "SELECT count(*) FROM pg_stat_activity "
        "WHERE state NOT IN ('idle') AND state IS NOT NULL "
        "AND now() - query_start > interval '5 seconds';"
    ),
    "locks": "SELECT count(*) FROM pg_locks WHERE NOT granted;",
    "deadlocks": "SELECT coalesce(sum(deadlocks), 0) FROM pg_stat_database;",
    # Tamaño total de todas las BDs de usuario (excluye plantillas de sistema)
    "db_size": (
        "SELECT coalesce(sum(pg_database_size(datname)), 0) / 1048576.0 "
        "FROM pg_database WHERE datname NOT IN ('template0','template1');"
    ),
}

def get_commands(
    db_port: int = 5432,
    db_user: str = "postgres",
    db_password: str | None = None,
) -> dict[str, str]:
    # Busca el contenedor Docker con imagen postgres y corre psql dentro de él.
    # Se usa "docker exec -e" para pasar PGPASSWORD sin sh -c, evitando conflictos
    # de comillas simples en el SQL con el delimitador de la cadena shell.
    pw_flag = f'-e PGPASSWORD={db_password} ' if db_password else ""
    find_cid = (
        '$(docker ps --format "{{.Names}} {{.Image}}" 2>/dev/null'
        ' | awk \'/postgres/{print $1}\' | head -1)'
    )
    return {
        k: (
            f'cid={find_cid}; '
            f'if [ -n "$cid" ]; then '
            f'  docker exec {pw_flag}"$cid" psql -U {db_user} -t -A -c "{v}" 2>/dev/null; '
            f'else '
            f'  su - postgres -s /bin/sh -c "psql -d postgres -t -A -c \\"{v}\\"" 2>/dev/null; '
            f'fi'
        )
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
