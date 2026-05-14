import pytest

from app.services.collectors.system_collector import (
    SystemCollector,
    parse_cpu,
    parse_df,
    parse_free,
    parse_loadavg,
    parse_proc_net_dev,
    parse_process_count,
)

CPU_OUTPUT = """%Cpu(s): 12.5 us,  3.2 sy,  0.0 ni, 82.3 id,  0.0 wa,  0.0 hi,  2.0 si,  0.0 st"""
FREE_OUTPUT = """              total        used        free      shared  buff/cache   available
Mem:           7980        2100        4200         200        1680        5480
Swap:          2047         100        1947"""
DF_OUTPUT = """Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   20G   30G  40% /
tmpfs           7.8G     0  7.8G   0% /dev/shm"""
LOADAVG_OUTPUT = "0.52 0.48 0.42 1/234 5678"
NETDEV_OUTPUT = """Inter-|   Receive                                                |  Transmit
 face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
    lo:    1000      10    0    0    0     0          0         0     1000      10    0    0    0     0       0          0
  eth0: 5000000   50000    0    0    0     0          0         0  2000000   20000    0    0    0     0       0          0"""


def test_parse_cpu_idle():
    result = parse_cpu(CPU_OUTPUT)
    assert result == pytest.approx(17.7, abs=0.5)


def test_parse_cpu_malformed():
    assert parse_cpu("garbage") is None


def test_parse_free_mem():
    ram_used, ram_total, ram_pct, swap_used, swap_total, swap_pct = parse_free(FREE_OUTPUT)
    assert ram_total == 7980
    assert ram_used == 2100
    assert ram_pct == pytest.approx(26.3, abs=0.5)
    assert swap_total == 2047
    assert swap_used == 100


def test_parse_free_malformed():
    result = parse_free("garbage")
    assert all(v is None for v in result)


def test_parse_df():
    partitions = parse_df(DF_OUTPUT)
    assert len(partitions) == 2
    assert partitions[0]["mountpoint"] == "/"
    assert partitions[0]["use_percent"] == 40.0


def test_parse_df_malformed():
    assert parse_df("garbage") == []


def test_parse_loadavg():
    l1, l5, l15 = parse_loadavg(LOADAVG_OUTPUT)
    assert l1 == pytest.approx(0.52)
    assert l5 == pytest.approx(0.48)
    assert l15 == pytest.approx(0.42)


def test_parse_loadavg_malformed():
    assert parse_loadavg("bad") == (None, None, None)


def test_parse_proc_net_dev():
    in_b, out_b = parse_proc_net_dev(NETDEV_OUTPUT)
    assert in_b == pytest.approx(5000000.0)
    assert out_b == pytest.approx(2000000.0)


def test_parse_process_count():
    assert parse_process_count("  42\n") == 42


def test_parse_process_count_malformed():
    assert parse_process_count("bad") is None


def test_system_collector_parse_full():
    collector = SystemCollector()
    outputs = {
        "cpu": CPU_OUTPUT,
        "mem": FREE_OUTPUT,
        "df": DF_OUTPUT,
        "loadavg": LOADAVG_OUTPUT,
        "netdev": NETDEV_OUTPUT,
        "procs": "100",
    }
    m = collector.parse(outputs)
    assert m.cpu_percent is not None
    assert m.ram_total_mb == 7980
    assert len(m.disk_partitions) == 2
    assert m.load_avg_1 == pytest.approx(0.52)
    assert m.process_count == 100


def test_system_collector_parse_empty():
    collector = SystemCollector()
    m = collector.parse({})
    assert m.cpu_percent is None
    assert m.ram_total_mb is None
