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
        setup_logging('example-app', warn_on_overwrite=False)

        log = get_logger('ExampleClass')

        with capture_logs() as logs:
            # When
            log.info('This is a simple message')
            log.error('This is an error message', error_message='Something terrible happened', error_code=1234)

            # Then
            self.assertEqual([
                {'event': 'This is a simple message', 'log_level': 'info'},
                {'error_code': 1234, 'error_message': 'Something terrible happened',
                 'event': 'This is an error message', 'log_level': 'error'}], logs)

    def test_stdlib_logging(self):
        # Given
        setup_logging('example-app', warn_on_overwrite=False)

        stdlib_log = logging.getLogger('ExampleClass')

        with self.assertLogs(stdlib_log) as logs:
            # When
            stdlib_log.info('This is a simple %s message', 'stdlib')
            stdlib_log.error('This is an error message')

            # Then
            self.assertEqual([
                'INFO:ExampleClass:This is a simple stdlib message',
                'ERROR:ExampleClass:This is an error message'], logs.output)

    def test_file_logging(self):
        # Given
        log_file_path = f'{TESTS_DIR_PATH}/logs/example.log'
        shutil.rmtree(os.path.dirname(log_file_path), ignore_errors=True)
        setup_logging('example-app', 'INFO', log_file_path, add_call_info=True, warn_on_overwrite=False)

        log = get_logger('ExampleClass')
        stdlib_log = logging.getLogger('ExampleClass')

        # When
        log.info('This is a simple message')
        stdlib_log.info('This is a %s message', 'simple')
        log.error('This is an error message', error_message='Something terrible happened', error_code=1234)
        stdlib_log.error('This is an error message')

        # Then
        self.assertTrue(os.path.exists(log_file_path))
        with open(log_file_path) as log_file:
            log_entry = json.loads(log_file.readline())
            assert_simple_message(self, log_entry)

            log_entry = json.loads(log_file.readline())
            assert_simple_message(self, log_entry)

            log_entry = json.loads(log_file.readline())
            self.assertEqual('This is an error message', log_entry.get('message'))
            self.assertEqual('Something terrible happened', log_entry.get('error_message'))
            self.assertEqual(1234, log_entry.get('error_code'))
            self.assertIsNotNone(log_entry.get('pathname'))
            self.assertIsNotNone(log_entry.get('func_name'))
            self.assertIsNotNone(log_entry.get('lineno'))

            log_entry = json.loads(log_file.readline())
            self.assertEqual('This is an error message', log_entry.get('message'))

    def test_overwriting_setup(self):
        # Given
        log_file_path = f'{TESTS_DIR_PATH}/logs/example.log'
        shutil.rmtree(os.path.dirname(log_file_path), ignore_errors=True)
        setup_logging('example-app', 'INFO', log_file_path, add_call_info=True, warn_on_overwrite=False)

        log = get_logger('ExampleClass')
        stdlib_log = logging.getLogger('ExampleClass')

        # When
        setup_logging('example-app', 'ERROR', log_file_path, add_call_info=False, message_field='msg')

        log.info('This is a simple message')
        stdlib_log.error('This is an error message')
        log.error('This is an error message', error_message='Something terrible happened', error_code=1234)

        # Then
        self.assertTrue(os.path.exists(log_file_path))
        with open(log_file_path) as log_file:
            log_entry = json.loads(log_file.readline())
            self.assertEqual('This is an error message', log_entry.get('msg'))

            log_entry = json.loads(log_file.readline())
            self.assertEqual('This is an error message', log_entry.get('msg'))
            self.assertEqual('Something terrible happened', log_entry.get('error_message'))
            self.assertEqual(1234, log_entry.get('error_code'))
            self.assertIsNone(log_entry.get('pathname'))
            self.assertIsNone(log_entry.get('func_name'))
            self.assertIsNone(log_entry.get('lineno'))


def assert_simple_message(test_case, log_entry):
    test_case.assertEqual('This is a simple message', log_entry.get('message'))
    test_case.assertEqual('example-app', log_entry.get('application'))
    test_case.assertEqual('none', log_entry.get('app_version'))
    test_case.assertIsNotNone(log_entry.get('hostname'))
    test_case.assertEqual('loggerTest', log_entry.get('module'))
    test_case.assertIsNotNone(log_entry.get('pathname'))
    test_case.assertIsNotNone(log_entry.get('func_name'))
    test_case.assertIsNotNone(log_entry.get('lineno'))
    test_case.assertEqual('MainProcess', log_entry.get('process_name'))
    test_case.assertEqual('MainThread', log_entry.get('thread_name'))
    test_case.assertEqual('ExampleClass', log_entry.get('logger'))
    test_case.assertEqual('info', log_entry.get('level'))
    test_case.assertIsNotNone(log_entry.get('timestamp'))


if __name__ == '__main__':
    unittest.main()
