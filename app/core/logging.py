import logging
from app.core.request_context import get_request_id


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [request_id=%(request_id)s] %(message)s",
    )

    root = logging.getLogger()
    root.addFilter(RequestIdFilter())
