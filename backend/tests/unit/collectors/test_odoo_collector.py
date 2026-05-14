from app.services.collectors.odoo_collector import OdooCollector, parse_http_time, parse_processes

PROCS_OUTPUT = """\
ubuntu    1234  0.5  2.1 ... openerp-server worker
ubuntu    1235 95.0  2.1 ... openerp-server worker
ubuntu    1236  1.2  1.5 ... odoo --http-interface
"""


def test_parse_processes_normal():
    workers, hung = parse_processes(PROCS_OUTPUT)
    assert workers == 3
    assert hung == 1  # only pid 1235 has cpu >= 90


def test_parse_processes_empty():
    workers, hung = parse_processes("")
    assert workers == 0
    assert hung == 0


def test_parse_http_time_ok():
    assert parse_http_time("0.352") == 352.0


def test_parse_http_time_empty():
    assert parse_http_time("") is None


def test_parse_http_time_zero():
    assert parse_http_time("0") is None


def test_odoo_collector_parse_full():
    collector = OdooCollector()
    outputs = {
        "procs": PROCS_OUTPUT,
        "mem": "512000",
        "cpu": "15.3",
        "http": "0.450",
    }
    m = collector.parse(outputs)
    assert m.workers_active == 3
    assert m.processes_hung == 1
    assert m.memory_mb > 0
    assert m.cpu_percent == 15.3
    assert m.response_time_ms == 450.0


def test_odoo_collector_parse_empty():
    collector = OdooCollector()
    m = collector.parse({})
    assert m.workers_active == 0
    assert m.response_time_ms is None
