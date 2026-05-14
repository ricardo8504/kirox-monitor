import uuid
from datetime import UTC, datetime

from app.core.encryption import decrypt
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.models.metric import Metric, MetricType, OdooMetric, PgMetric
from app.models.server import Server
from app.repositories.metric_repository import MetricRepository
from app.repositories.server_repository import ServerRepository
from app.services.collectors.odoo_collector import OdooCollector
from app.services.collectors.odoo_collector import get_commands as get_odoo_commands
from app.services.collectors.pg_collector import PgCollector
from app.services.collectors.pg_collector import get_commands as get_pg_commands
from app.services.collectors.system_collector import SystemCollector
from app.services.ssh_manager import SSHManager

logger = get_logger(__name__)


class MonitoringOrchestrator:
    def __init__(
        self,
        server_repo: ServerRepository,
        metric_repo: MetricRepository,
        ssh: SSHManager,
    ) -> None:
        self._servers = server_repo
        self._metrics = metric_repo
        self._ssh = ssh
        self._sys = SystemCollector()
        self._odoo = OdooCollector()
        self._pg = PgCollector()

    def _decrypt_creds(self, server: "Server") -> tuple[str | None, str | None]:
        password = decrypt(server.ssh_password_encrypted) if server.ssh_password_encrypted else None
        key = decrypt(server.ssh_key_encrypted) if server.ssh_key_encrypted else None
        return password, key

    def _decrypt_db_password(self, server: "Server") -> str | None:
        return decrypt(server.db_password_encrypted) if server.db_password_encrypted else None

    def _run_commands(self, server: "Server", commands: dict[str, str]) -> dict[str, str]:
        password, key = self._decrypt_creds(server)
        outputs: dict[str, str] = {}
        for name, cmd in commands.items():
            try:
                result = self._ssh.execute_command(
                    host=server.host,
                    port=server.port,
                    user=server.ssh_user,
                    command=cmd,
                    password=password,
                    key=key,
                )
                outputs[name] = result.stdout
            except ExternalServiceError:
                outputs[name] = ""
        return outputs

    async def collect(self, server_id: uuid.UUID) -> bool:
        server = await self._servers.get_by_id(server_id)
        if not server or not server.is_active:
            return False

        now = datetime.now(UTC)

        try:
            sys_out = self._run_commands(server, self._sys.COMMANDS)
        except Exception as exc:
            logger.warning("ssh_collect_failed", server_id=str(server_id), error=str(exc))
            return False

        db_password = self._decrypt_db_password(server)
        sys_m = self._sys.parse(sys_out)
        odoo_m = self._odoo.parse(self._run_commands(server, get_odoo_commands(server.odoo_port)))
        pg_m = self._pg.parse(self._run_commands(server, get_pg_commands(
            db_port=server.db_port,
            db_user=server.db_user,
            db_password=db_password,
        )))

        batch: list[Metric] = []
        scalar_metrics = [
            (MetricType.CPU_USAGE, sys_m.cpu_percent, "%"),
            (MetricType.RAM_USAGE, sys_m.ram_percent, "%"),
            (MetricType.SWAP_USAGE, sys_m.swap_percent, "%"),
            (MetricType.LOAD_AVG_1, sys_m.load_avg_1, ""),
            (MetricType.LOAD_AVG_5, sys_m.load_avg_5, ""),
            (MetricType.LOAD_AVG_15, sys_m.load_avg_15, ""),
            (MetricType.NETWORK_IN, sys_m.network_in_bytes, "bytes"),
            (MetricType.NETWORK_OUT, sys_m.network_out_bytes, "bytes"),
            (MetricType.PROCESS_COUNT, sys_m.process_count, ""),
            (MetricType.CPU_TEMP, sys_m.cpu_temp, "°C"),
        ]
        for mtype, value, unit in scalar_metrics:
            if value is not None:
                batch.append(Metric(
                    server_id=server_id, metric_type=mtype,
                    value=float(value), unit=unit, timestamp=now,
                ))

        for partition in sys_m.disk_partitions:
            batch.append(Metric(
                server_id=server_id, metric_type=MetricType.DISK_USAGE,
                value=partition["use_percent"], unit="%", timestamp=now, raw_data=partition,
            ))

        await self._metrics.insert_batch(batch)
        await self._metrics.insert_odoo(OdooMetric(
            server_id=server_id,
            workers_active=odoo_m.workers_active,
            processes_hung=odoo_m.processes_hung,
            memory_mb=odoo_m.memory_mb,
            cpu_percent=odoo_m.cpu_percent,
            response_time_ms=odoo_m.response_time_ms,
            requests_concurrent=odoo_m.requests_concurrent,
            timestamp=now,
        ))
        await self._metrics.insert_pg(PgMetric(
            server_id=server_id,
            connections_active=pg_m.connections_active,
            slow_queries=pg_m.slow_queries,
            locks=pg_m.locks,
            deadlocks=pg_m.deadlocks,
            db_size_mb=pg_m.db_size_mb,
            timestamp=now,
        ))
        return True
