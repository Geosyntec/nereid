"""ref: mCoding json config https://github.com/mCodingLLC/VideosSampleCode/blob/master/videos/135_modern_logging/mylogger.py"""
import datetime as dt
import json
import logging
import logging.handlers
import queue

from typing_extensions import override

LOG_RECORD_BUILTIN_ATTRS = {  # pragma: no cover
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class JSONLogFormatter(logging.Formatter):  # pragma: no cover
    def __init__(
        self,
        *,
        fmt_keys: dict[str, str] | None = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord):
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


def _resolve_handlers(handlers: list[str]):  # pragma: no cover
    _handlers = getattr(logging, "_handlers", {})

    return [handler for name, handler in _handlers.items() if name in handlers]


class QueueHandler(logging.handlers.QueueHandler):  # pragma: no cover
    def __init__(self, **kwargs):
        q = queue.Queue()
        super().__init__(q)
        auto_run = kwargs.pop("auto_run", False)
        handlers = _resolve_handlers(kwargs.pop("handlers", []))
        _resolve_handlers(handlers)

        self.listener = logging.handlers.QueueListener(q, *handlers, **kwargs)

        if auto_run:
            import atexit

            self.listener.start()
            atexit.register(self.listener.stop)
