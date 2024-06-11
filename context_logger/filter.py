# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

import socket
from importlib.metadata import version, PackageNotFoundError
from logging import Filter, LogRecord


class ContextSetupFilter(Filter):

    def __init__(self, application_name: str, message_field: str):
        super().__init__()
        self._application_name = application_name
        self._message_field = message_field

    def filter(self, record: LogRecord) -> bool:
        if not isinstance(record.msg, dict):
            record.msg = {self._message_field: record.msg % record.args}
            record.args = ()

        record.msg['hostname'] = socket.gethostname()
        record.msg['application'] = self._application_name
        record.msg['app_version'] = self._get_application_version()

        if 'process_name' in record.msg:
            record.msg['process_name'] = record.processName

        return True

    def _get_application_version(self) -> str:
        try:
            return version(self._application_name)
        except PackageNotFoundError:
            return 'none'
