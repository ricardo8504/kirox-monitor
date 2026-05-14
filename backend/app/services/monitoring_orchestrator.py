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
from app.workers.ws_publisher import publish_metrics

logger = get_logger(__name__)


class MonitoringOrchestrator:
    def __init__(
        self,
        server_repo: ServerRepository,
        metric_repo: MetricRepository,
        ssh: SSHManager,
        alert_engine=None,  # AlertEngine | None — avoids circular import
    ) -> None:
        self._servers = server_repo
        self._metrics = metric_repo
        self._ssh = ssh
        self._sys = SystemCollector()
        self._odoo = OdooCollector()
        self._pg = PgCollector()
        self._alert_engine = alert_engine

    def _decrypt_creds(self, server: "Server") -> tuple[str | None, str | None]:
        password = decrypt(server.ssh_password_encrypted) if server.ssh_password_encrypted else None
        key = decrypt(server.ssh_key_encrypted) if server.ssh_key_encrypted else None
        return password, key

    def _decrypt_db_password(self, server: "Server") -> str | None:
        return decrypt(server.db_password_encrypted) if server.db_password_encrypted else None

    def _run_commands(
        self, server: "Server", commands: dict[str, str], log_stderr: bool = False
    ) -> dict[str, str]:
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
                if log_stderr and result.stderr.strip():
                    logger.warning(
                        "pg_command_stderr",
                        server_id=str(server.id),
                        command=name,
                        stderr=result.stderr.strip(),
                        exit_code=result.exit_code,
                    )
                outputs[name] = result.stdout
            except ExternalServiceError:
                outputs[name] = ""
        return outputs

    @staticmethod
    def _build_ws_snapshot(
        server_id: uuid.UUID,
        sys_m,
        odoo_m,
        pg_m,
        now: datetime,
    ) -> dict:
        ts = now.isoformat()
        sid = str(server_id)
        null_id = "00000000-0000-0000-0000-000000000000"

        system: dict = {}
        metric_map = [
            (MetricType.CPU_USAGE, sys_m.cpu_percent, "%"),
            (MetricType.RAM_USAGE, sys_m.ram_percent, "%"),
            (MetricType.SWAP_USAGE, sys_m.swap_percent, "%"),
            (MetricType.LOAD_AVG_1, sys_m.load_avg_1, ""),
            (MetricType.LOAD_AVG_5, sys_m.load_avg_5, ""),
            (MetricType.LOAD_AVG_15, sys_m.load_avg_15, ""),
            (MetricType.PROCESS_COUNT, sys_m.process_count, ""),
            (MetricType.CPU_TEMP, sys_m.cpu_temp, "°C"),
        ]
        for mtype, value, unit in metric_map:
            if value is not None:
                system[mtype.value] = {
                    "id": null_id, "server_id": sid, "metric_type": mtype.value,
                    "value": float(value), "unit": unit, "timestamp": ts, "raw_data": None,
                }
        if sys_m.disk_partitions:
            system[MetricType.DISK_USAGE.value] = {
                "id": null_id, "server_id": sid, "metric_type": MetricType.DISK_USAGE.value,
                "value": float(sys_m.disk_partitions[0]["use_percent"]),
                "unit": "%", "timestamp": ts, "raw_data": sys_m.disk_partitions[0],
            }

        odoo = {
            "id": null_id, "server_id": sid,
            "workers_active": odoo_m.workers_active,
            "processes_hung": odoo_m.processes_hung,
            "memory_mb": odoo_m.memory_mb,
            "cpu_percent": odoo_m.cpu_percent,
            "response_time_ms": odoo_m.response_time_ms,
            "requests_concurrent": odoo_m.requests_concurrent,
            "timestamp": ts,
        }

        pg = {
            "id": null_id, "server_id": sid,
            "connections_active": pg_m.connections_active,
            "slow_queries": pg_m.slow_queries,
            "locks": pg_m.locks,
            "deadlocks": pg_m.deadlocks,
            "db_size_mb": pg_m.db_size_mb,
            "timestamp": ts,
        }

        return {
            "type": "metrics",
            "server_id": sid,
            "data": {"system": system, "odoo": odoo, "pg": pg},
        }

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
        ), log_stderr=True))

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

        # Update last_seen via explicit SQL UPDATE (ORM dirty tracking unreliable after flush)
        await self._servers.update_last_seen(server_id, now)

        # Evaluate alert rules if engine is configured
        if self._alert_engine is not None:
            metrics_snapshot: dict[str, float] = {}
            if sys_m.cpu_percent is not None:
                metrics_snapshot[MetricType.CPU_USAGE.value] = float(sys_m.cpu_percent)
            if sys_m.ram_percent is not None:
                metrics_snapshot[MetricType.RAM_USAGE.value] = float(sys_m.ram_percent)
            if sys_m.swap_percent is not None:
                metrics_snapshot[MetricType.SWAP_USAGE.value] = float(sys_m.swap_percent)
            if sys_m.load_avg_1 is not None:
                metrics_snapshot[MetricType.LOAD_AVG_1.value] = float(sys_m.load_avg_1)
            if sys_m.disk_partitions:
                metrics_snapshot[MetricType.DISK_USAGE.value] = float(
                    sys_m.disk_partitions[0]["use_percent"]
                )
            metrics_snapshot["pg_connections"] = float(pg_m.connections_active)
            metrics_snapshot["pg_slow_queries"] = float(pg_m.slow_queries)
            metrics_snapshot["pg_locks"] = float(pg_m.locks)
            metrics_snapshot["odoo_workers"] = float(odoo_m.workers_active)
            metrics_snapshot["odoo_hung"] = float(odoo_m.processes_hung)

            try:
                fired = await self._alert_engine.evaluate_rules(server_id, metrics_snapshot)
                if fired:
                    logger.info("alerts_fired", server_id=str(server_id), count=len(fired))
            except Exception as exc:
                logger.warning("alert_engine_error", server_id=str(server_id), error=str(exc))

        # Publish real-time snapshot to WebSocket clients via Redis pub/sub
        ws_snapshot = self._build_ws_snapshot(server_id, sys_m, odoo_m, pg_m, now)
        publish_metrics(server_id, ws_snapshot)

        return True
