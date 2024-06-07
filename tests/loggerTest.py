import json
import logging
import os
import shutil
import unittest
from unittest import TestCase

from structlog.testing import capture_logs

from context_logger import get_logger, setup_logging

TESTS_DIR_PATH = os.path.dirname(os.path.abspath(__file__))


class LoggerTest(TestCase):

    def setUp(self):
        print()

    def test_structlog_logging(self):
        # Given
        setup_logging('example-app')

        log = get_logger('ExampleClass')

        with capture_logs() as logs:
            # When
            log.info('This is a simple message')
            log.error('This is an error message', error_message='Something terrible happened', error_code=1234)

            # Then
            self.assertEqual(logs, [
                {'event': 'This is a simple message', 'log_level': 'info'},
                {'error_code': 1234, 'error_message': 'Something terrible happened',
                 'event': 'This is an error message', 'log_level': 'error'}])

    def test_stdlib_logging(self):
        # Given
        setup_logging('example-app')

        stdlib_log = logging.getLogger('ExampleClass')

        with self.assertLogs(stdlib_log) as logs:
            # When
            stdlib_log.info('This is a simple %s message', 'stdlib')

            # Then
            self.assertEqual(logs.output, ['INFO:ExampleClass:This is a simple stdlib message'])

    def test_file_logging(self):
        # Given
        log_file_path = f'{TESTS_DIR_PATH}/logs/example.log'
        shutil.rmtree(os.path.dirname(log_file_path), ignore_errors=True)
        setup_logging('example-app', 'INFO', log_file_path, add_call_info=True)

        log = get_logger('ExampleClass')
        stdlib_log = logging.getLogger('ExampleClass')

        # When
        log.info('This is a simple message')
        stdlib_log.info('This is a %s message', 'simple')
        log.error('This is an error message', error_message='Something terrible happened', error_code=1234)

        # Then
        self.assertTrue(os.path.exists(log_file_path))
        with open(log_file_path) as log_file:
            log_entry = json.loads(log_file.readline())
            assert_simple_message(self, log_entry)

            log_entry = json.loads(log_file.readline())
            assert_simple_message(self, log_entry)

            log_entry = json.loads(log_file.readline())
            self.assertEqual(log_entry['message'], 'This is an error message')
            self.assertEqual(log_entry['error_message'], 'Something terrible happened')
            self.assertEqual(log_entry['error_code'], 1234)


def assert_simple_message(test_case, log_entry):
    test_case.assertEqual(log_entry['message'], 'This is a simple message')
    test_case.assertEqual(log_entry['application'], 'example-app')
    test_case.assertEqual(log_entry['app_version'], 'none')
    test_case.assertIsNotNone(log_entry['hostname'])
    test_case.assertEqual(log_entry['module'], 'loggerTest')
    test_case.assertIsNotNone(log_entry['pathname'])
    test_case.assertIsNotNone(log_entry['func_name'])
    test_case.assertIsNotNone(log_entry['lineno'])
    test_case.assertEqual(log_entry['process_name'], 'MainProcess')
    test_case.assertEqual(log_entry['thread_name'], 'MainThread')
    test_case.assertEqual(log_entry['logger'], 'ExampleClass')
    test_case.assertEqual(log_entry['level'], 'info')
    test_case.assertIsNotNone(log_entry['timestamp'])


if __name__ == '__main__':
    unittest.main()
