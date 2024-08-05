# python-context-logger
Contextual structured logging library for Python.

Uses [structlog](https://www.structlog.org/en/stable/) to provide structured logging with minimal setup.

## Table of contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [New in 1.1.0](#new-in-110)

## Features

- Structured logging
- Contextual logging
- Colorized console output
- JSON line file output
- Easy setup
- [New in 1.1.0](#new-in-110) Standard library log messages are also captured, enriched and formatted

Contextual information is added to each structured log message on any thread, including:
- Application name
- Application version
- Hostname
- Logger name
- Log level
- Timestamp
- [New in 1.1.0](#new-in-110) Optional call information (module name, filename, line number, function name, process name, thread name)

Custom fields can be added to each log message

## Requirements

- [Python3](https://www.python.org/downloads/)
- [structlog](https://www.structlog.org/en/stable/)

## Installation

### Install from source root directory

```bash
pip install .
```

### Install from source distribution

1. Create source distribution
    ```bash
    python setup.py sdist
    ```

2. Install from distribution file
    ```bash
    pip install dist/python_context_logger-1.0.0.tar.gz
    ```
   
3. Install from GitHub repository
    ```bash
    pip install git+https://github.com/EffectiveRange/python-context-logger.git@latest
    ```

## Usage
Example usage:
```python
from context_logger import get_logger, setup_logging

log = get_logger('ExampleClass')

setup_logging('example-app', 'INFO', 'logs/example.log')

log.info('This is a simple message')
log.error('This is an error message', error_message='Something terrible happened', error_code=1234)
```
Console output (colored):
```
2024-02-16T12:49:41.733384Z [info     ] This is a simple message       [ExampleClass] app_version=0.0.1 application=example-app hostname=example-host
2024-02-16T12:49:41.734073Z [error    ] This is an error message       [ExampleClass] app_version=0.0.1 application=example-app error_code=1234 error_message=Something terrible happened hostname=example-host
```
File output (logs/example.log):
```
{"logger": "ExampleClass", "level": "info", "timestamp": "2024-02-16T12:49:41.733384Z", "message": "This is a simple message", "hostname": "example-host", "app_version": "0.0.1", "application": "example-app"}
{"error_message": "Something terrible happened", "error_code": 1234, "logger": "ExampleClass", "level": "error", "timestamp": "2024-02-16T12:49:41.734073Z", "message": "This is an error message", "hostname": "example-host", "app_version": "0.0.1", "application": "example-app"}
```
### New in 1.1.0
Example usage with call information and standard library logging:
```python
import logging
from context_logger import get_logger, setup_logging

setup_logging('example-app', add_call_info=True)

log = get_logger('ExampleClass')
stdlib_log = logging.getLogger('StdLibClass')

log.info('This is a simple message')
stdlib_log.info('This is a simple message')
```
Console output (colored):
```
2024-02-26T14:55:40.320668Z [info     ] This is a simple message       [ExampleClass] app_version=0.0.1 application=example-app func_name=test_file_logging hostname=example-host lineno=27 module=test_logger pathname=/home/attila/Work/context-logger/tests/test_logger.py process_name=MainProcess thread_name=MainThread
2024-02-26T14:55:40.326201Z [info     ] This is a simple message       [StdLibClass] app_version=0.0.1 application=example-app func_name=test_file_logging hostname=example-host lineno=28 module=test_logger pathname=/home/attila/Work/context-logger/tests/test_logger.py process_name=MainProcess thread_name=MainThread
```
