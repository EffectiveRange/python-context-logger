import logging
import unittest
from importlib.metadata import PackageNotFoundError
from unittest import TestCase
from unittest.mock import patch

from context_logger.filter import ContextSetupFilter


class FilterTest(TestCase):

    def test_filter_enriches_string_message_and_context(self):
        # Given
        filter_ = ContextSetupFilter('example-app', 'message',
                                     global_context={'team': 'platform', 'application': 'ignored'})
        record = logging.LogRecord('ExampleClass', logging.INFO, __file__, 10, 'Hello %s', ('World',), None)

        with patch('context_logger.filter.socket.gethostname', return_value='test-host'), \
                patch.object(filter_, '_get_application_version', return_value='1.2.3'):
            # When
            result = filter_.filter(record)

        # Then
        self.assertTrue(result)
        self.assertEqual((), record.args)
        self.assertEqual('Hello World', record.msg.get('message'))
        self.assertEqual('test-host', record.msg.get('hostname'))
        self.assertEqual('example-app', record.msg.get('application'))
        self.assertEqual('1.2.3', record.msg.get('app_version'))
        self.assertEqual('platform', record.msg.get('team'))

    def test_filter_updates_process_name_when_key_exists(self):
        # Given
        filter_ = ContextSetupFilter('example-app', 'message')
        record = logging.LogRecord('ExampleClass', logging.INFO, __file__, 10, {'message': 'ok', 'process_name': 'x'},
                                   (), None)

        with patch('context_logger.filter.socket.gethostname', return_value='test-host'), \
                patch.object(filter_, '_get_application_version', return_value='1.2.3'):
            # When
            filter_.filter(record)

        # Then
        self.assertEqual(record.processName, record.msg.get('process_name'))

    def test_filter_handles_string_format_error(self):
        # Given
        filter_ = ContextSetupFilter('example-app', 'message')
        record = logging.LogRecord('ExampleClass', logging.INFO, __file__, 10, 'broken %s %s', ('format',), None)

        with patch('builtins.print') as print_mock:
            # When
            result = filter_.filter(record)

        # Then
        self.assertTrue(result)
        self.assertEqual('broken %s %s', record.msg)
        print_mock.assert_called_once()
        self.assertEqual('Failed to handle log record:', print_mock.call_args.args[0])

    def test_filter_handles_non_mapping_message(self):
        # Given
        filter_ = ContextSetupFilter('example-app', 'message')
        record = logging.LogRecord('ExampleClass', logging.INFO, __file__, 10, 123, (), None)

        with patch('builtins.print') as print_mock:
            # When
            result = filter_.filter(record)

        # Then
        self.assertTrue(result)
        self.assertEqual(123, record.msg)
        print_mock.assert_not_called()

    def test_filter_handles_unexpected_version_lookup_error(self):
        # Given
        filter_ = ContextSetupFilter('example-app', 'message')
        record = logging.LogRecord('ExampleClass', logging.INFO, __file__, 10, 'Hello', (), None)

        with patch('context_logger.filter.socket.gethostname', return_value='test-host'), \
                patch.object(filter_, '_get_application_version', side_effect=RuntimeError('boom')), \
                patch('builtins.print') as print_mock:
            # When
            result = filter_.filter(record)

        # Then
        self.assertTrue(result)
        self.assertEqual('Hello', record.msg.get('message'))
        self.assertEqual('test-host', record.msg.get('hostname'))
        self.assertEqual('example-app', record.msg.get('application'))
        self.assertNotIn('app_version', record.msg)
        print_mock.assert_called_once()
        self.assertEqual('Failed to handle log record:', print_mock.call_args.args[0])

    def test_get_application_version_returns_package_version(self):
        # Given
        filter_ = ContextSetupFilter('example-app', 'message')

        with patch('context_logger.filter.version', return_value='9.9.9'):
            # When
            version = filter_._get_application_version()

        # Then
        self.assertEqual('9.9.9', version)

    def test_get_application_version_returns_none_when_package_is_missing(self):
        # Given
        filter_ = ContextSetupFilter('missing-package', 'message')

        with patch('context_logger.filter.version', side_effect=PackageNotFoundError):
            # When
            version = filter_._get_application_version()

        # Then
        self.assertEqual('none', version)


if __name__ == '__main__':
    unittest.main()
