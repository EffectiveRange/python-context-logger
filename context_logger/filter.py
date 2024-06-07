# Copyright (C) 2024  Ferenc Nandor Janky
# Copyright (C) 2024  Attila Gombos
# Contact: info@effective-range.com
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA
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
