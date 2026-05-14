import structlog

from app.core.logging import get_logger, get_request_id, request_id_var, setup_logging


def test_setup_logging_dev_does_not_raise():
    setup_logging(log_level="DEBUG", is_development=True)


def test_setup_logging_prod_does_not_raise():
    setup_logging(log_level="INFO", is_development=False)


def test_get_logger_returns_bound_logger():
    setup_logging()
    logger = get_logger("test")
    assert logger is not None


def test_get_request_id_returns_string():
    rid = get_request_id()
    assert isinstance(rid, str)
    assert len(rid) > 0


def test_request_id_var_can_be_set():
    token = request_id_var.set("abc-123")
    assert get_request_id() == "abc-123"
    request_id_var.reset(token)


def test_logger_emits_without_error(capsys):
    setup_logging(log_level="DEBUG", is_development=True)
    logger = get_logger("test_emit")
    logger.info("hello", key="value")
    captured = capsys.readouterr()
    assert "hello" in captured.out
