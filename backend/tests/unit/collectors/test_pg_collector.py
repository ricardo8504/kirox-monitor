from app.services.collectors.pg_collector import PgCollector


def test_pg_collector_parse_full():
    collector = PgCollector()
    outputs = {
        "connections": "5",
        "slow_queries": "2",
        "locks": "1",
        "deadlocks": "0",
        "db_size": "1024.5",
    }
    m = collector.parse(outputs)
    assert m.connections_active == 5
    assert m.slow_queries == 2
    assert m.locks == 1
    assert m.deadlocks == 0
    assert m.db_size_mb == 1024.5


def test_pg_collector_parse_empty():
    collector = PgCollector()
    m = collector.parse({})
    assert m.connections_active == 0
    assert m.db_size_mb == 0.0


def test_pg_collector_parse_malformed():
    collector = PgCollector()
    m = collector.parse({
        "connections": "not a number",
        "db_size": "bad",
    })
    assert m.connections_active == 0
    assert m.db_size_mb == 0.0
