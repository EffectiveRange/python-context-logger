import logging
import logging.handlers
import os
import sys
import warnings
from logging.handlers import RotatingFileHandler
from typing import Any, Optional

import structlog
from structlog._log_levels import add_log_level
from structlog.dev import ConsoleRenderer
from structlog.processors import JSONRenderer, StackInfoRenderer, TimeStamper, EventRenamer, format_exc_info, \
    UnicodeDecoder, CallsiteParameterAdder
from structlog.stdlib import ProcessorFormatter, LoggerFactory, BoundLogger, PositionalArgumentsFormatter, \
    add_logger_name

from context_logger import ContextSetupFilter

STRUCTURED_LOGGER = None


def get_logger(logger_name: str) -> Any:
    return structlog.get_logger(logger_name)


def setup_logging(application_name: str, log_level: str = 'INFO',
                  log_file_path: Optional[str] = None, max_bytes: int = 1024 * 1024, backup_count: int = 5,
                  add_call_info: bool = False, message_field: str = 'message') -> None:
    global STRUCTURED_LOGGER

    if STRUCTURED_LOGGER is not None:
        warnings.warn('Logging has already been set up, overwriting existing configuration.', UserWarning)

    STRUCTURED_LOGGER = StructuredLogger(application_name, log_level, log_file_path, max_bytes, backup_count,
                                         add_call_info, message_field)


class StructuredLogger(object):

    def __init__(self, application_name: str, log_level: str, log_file_path: Optional[str], max_bytes: int,
                 backup_count: int, add_call_info: bool, message_field: str) -> None:
        self._application_name = application_name
        self._log_level = logging.getLevelName(log_level.upper())
        self._max_bytes = max_bytes
        self._backup_count = backup_count
        self._message_field = message_field
        self._add_call_info = add_call_info

        self._shared_processors: Any = [
            add_log_level,
            add_logger_name,
            PositionalArgumentsFormatter(),
            StackInfoRenderer(),
            TimeStamper(fmt='iso'),
            format_exc_info,
            UnicodeDecoder()
        ]

        if self._add_call_info:
            self._add_call_info_processor()

        self._shared_processors.append(EventRenamer(self._message_field))

        root = logging.getLogger()
        root.setLevel(self._log_level)

        self._clear_handlers(root)

        console_handler = self._create_console_handler()
        root.addHandler(console_handler)

        if log_file_path is not None:
            file_handler = self._create_file_handler(log_file_path)
            root.addHandler(file_handler)

        structlog.configure(
            processors=self._shared_processors + [ProcessorFormatter.wrap_for_formatter],
            logger_factory=LoggerFactory(),
            wrapper_class=BoundLogger,
            cache_logger_on_first_use=True
        )

    def _add_call_info_processor(self) -> None:
        self._shared_processors.append(CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.MODULE,
                structlog.processors.CallsiteParameter.PATHNAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.PROCESS_NAME,
                structlog.processors.CallsiteParameter.THREAD_NAME
            }
        ))

    def _clear_handlers(self, root: logging.Logger) -> None:
        for handler in root.handlers:
            if isinstance(handler, logging.StreamHandler) or isinstance(handler, RotatingFileHandler):
                root.removeHandler(handler)

    def _create_console_handler(self) -> logging.Handler:
        formatter = ProcessorFormatter(
            foreign_pre_chain=self._shared_processors + [self._enrich_stdlib_log],
            processors=[ProcessorFormatter.remove_processors_meta, ConsoleRenderer(event_key=self._message_field)]
        )

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        handler.addFilter(ContextSetupFilter(self._application_name))

        return handler

    def _create_file_handler(self, log_file_path: str) -> RotatingFileHandler:
        formatter = ProcessorFormatter(
            foreign_pre_chain=self._shared_processors + [self._enrich_stdlib_log],
            processors=[ProcessorFormatter.remove_processors_meta, JSONRenderer()]
        )

        self._ensure_directory_exists(log_file_path)

        handler = RotatingFileHandler(log_file_path, maxBytes=self._max_bytes, backupCount=self._backup_count)
        handler.setFormatter(formatter)
        handler.addFilter(ContextSetupFilter(self._application_name))

        return handler

    def _ensure_directory_exists(self, log_file_path: str) -> None:
        directory = os.path.dirname(log_file_path)

        if not os.path.exists(directory):
            os.makedirs(directory)

    def _enrich_stdlib_log(self, _: logging.Logger, __: str, event_dict: dict[Any, Any]) -> dict[Any, Any]:
        event_dict.update(event_dict['_record'].msg)

        return event_dict
