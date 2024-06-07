import socket
from importlib.metadata import version, PackageNotFoundError
from logging import Filter, LogRecord


class ContextSetupFilter(Filter):

    def __init__(self, application_name: str):
        super().__init__()
        self._application_name = application_name

    def filter(self, record: LogRecord) -> bool:
        if not isinstance(record.msg, dict):
            self._convert_stdlib_record(record)

        if isinstance(record.msg, dict):
            record.msg['hostname'] = socket.gethostname()
            record.msg['application'] = self._application_name
            record.msg['app_version'] = self._get_application_version()

            if 'process_name' in record.msg:
                record.msg['process_name'] = record.processName

        return True

    def _convert_stdlib_record(self, record: LogRecord) -> None:
        if record.args:
            record.msg = record.msg % record.args
            record.args = ()

        record.msg = {'message': record.msg}

    def _get_application_version(self) -> str:
        try:
            return version(self._application_name)
        except PackageNotFoundError:
            return 'none'
