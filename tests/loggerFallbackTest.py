import logging
import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch

from context_logger.logger import Logger, setup_logging


class _LegacyProcessorFormatter:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        # Simulate old API: no `processors` support.
        if 'processors' in kwargs:
            raise AttributeError('processors is not supported')


class LoggerFallbackTest(TestCase):

    def test_setup_logging_warns_and_cleans_up_on_overwrite(self):
        # Given
        previous_logger = MagicMock()
        replacement_logger = MagicMock()

        with patch('context_logger.logger.LOGGER', previous_logger), \
                patch('context_logger.logger.Logger', return_value=replacement_logger) as logger_ctor, \
                patch('context_logger.logger.warnings.warn') as warn_mock:
            # When
            setup_logging('example-app')

        # Then
        warn_mock.assert_called_once()
        previous_logger.cleanup.assert_called_once()
        logger_ctor.assert_called_once()
        replacement_logger.setup.assert_called_once()

    def test_setup_logging_skips_warning_when_warn_on_overwrite_is_false(self):
        # Given
        previous_logger = MagicMock()
        replacement_logger = MagicMock()

        with patch('context_logger.logger.LOGGER', previous_logger), \
                patch('context_logger.logger.Logger', return_value=replacement_logger), \
                patch('context_logger.logger.warnings.warn') as warn_mock:
            # When
            setup_logging('example-app', warn_on_overwrite=False)

        # Then
        warn_mock.assert_not_called()
        previous_logger.cleanup.assert_called_once()
        replacement_logger.setup.assert_called_once()

    def test_setup_processors_ignores_missing_event_renamer(self):
        # Given
        logger = Logger('example-app', 'INFO', None, 1024, 1, False, 'message')

        with patch('context_logger.logger.structlog.processors.EventRenamer', side_effect=AttributeError):
            # When
            logger._setup_processors()

        # Then
        self.assertIsInstance(logger._shared_processors, list)
        self.assertGreater(len(logger._shared_processors), 0)

    def test_setup_processors_ignores_missing_callsite_parameter_adder(self):
        # Given
        logger = Logger('example-app', 'INFO', None, 1024, 1, True, 'message')

        with patch('context_logger.logger.structlog.processors.CallsiteParameterAdder', side_effect=AttributeError):
            # When
            logger._setup_processors()

        # Then
        self.assertIsInstance(logger._shared_processors, list)
        self.assertGreater(len(logger._shared_processors), 0)

    def test_create_console_handler_uses_legacy_formatter_fallback(self):
        # Given
        logger = Logger('example-app', 'INFO', None, 1024, 1, False, 'message')
        logger._shared_processors = []

        with patch('context_logger.logger.ProcessorFormatter', _LegacyProcessorFormatter):
            # When
            handler = logger._create_console_handler()

        # Then
        self.assertIsInstance(handler, logging.Handler)
        self.assertIn('processor', handler.formatter.kwargs)

    def test_create_file_handler_uses_legacy_formatter_fallback(self):
        # Given
        logger = Logger('example-app', 'INFO', '/tmp/unused.log', 1024, 1, False, 'message')
        logger._shared_processors = []

        fake_handler = MagicMock()
        fake_handler.setFormatter = MagicMock()
        fake_handler.addFilter = MagicMock()

        with patch('context_logger.logger.ProcessorFormatter', _LegacyProcessorFormatter), \
                patch.object(Logger, '_ensure_directory_exists') as ensure_directory_mock, \
                patch('context_logger.logger.RotatingFileHandler', return_value=fake_handler):
            # When
            handler = logger._create_file_handler('/tmp/test.log')

        # Then
        self.assertIs(handler, fake_handler)
        ensure_directory_mock.assert_called_once_with('/tmp/test.log')
        fake_handler.setFormatter.assert_called_once()
        fake_handler.addFilter.assert_called_once()

    def test_ensure_directory_exists_creates_directory_when_missing(self):
        # Given
        logger = Logger('example-app', 'INFO', None, 1024, 1, False, 'message')

        with patch('context_logger.logger.os.path.exists', return_value=False), \
                patch('context_logger.logger.os.makedirs') as makedirs_mock:
            # When
            logger._ensure_directory_exists('/tmp/new-dir/test.log')

        # Then
        makedirs_mock.assert_called_once_with('/tmp/new-dir')

    def test_ensure_directory_exists_does_not_create_existing_directory(self):
        # Given
        logger = Logger('example-app', 'INFO', None, 1024, 1, False, 'message')

        with patch('context_logger.logger.os.path.exists', return_value=True), \
                patch('context_logger.logger.os.makedirs') as makedirs_mock:
            # When
            logger._ensure_directory_exists('/tmp/existing-dir/test.log')

        # Then
        makedirs_mock.assert_not_called()

    def test_enrich_stdlib_log_updates_event_dict_from_mapping_message(self):
        # Given
        logger = Logger('example-app', 'INFO', None, 1024, 1, False, 'message')
        record = MagicMock()
        record.msg = {'message': 'ok', 'code': 7}
        event_dict = {'_record': record, 'existing': True}

        # When
        result = logger._enrich_stdlib_log(logging.getLogger('x'), 'info', event_dict)

        # Then
        self.assertIs(result, event_dict)
        self.assertEqual('ok', event_dict.get('message'))
        self.assertEqual(7, event_dict.get('code'))
        self.assertTrue(event_dict.get('existing'))

    def test_enrich_stdlib_log_updates_event_dict_from_json_message(self):
        # Given
        logger = Logger('example-app', 'INFO', None, 1024, 1, False, 'message')
        record = MagicMock()
        record.msg = '{"message": "ok", "code": 9}'
        event_dict = {'_record': record}

        # When
        result = logger._enrich_stdlib_log(logging.getLogger('x'), 'info', event_dict)

        # Then
        self.assertIs(result, event_dict)
        self.assertEqual('ok', event_dict.get('message'))
        self.assertEqual(9, event_dict.get('code'))

    def test_enrich_stdlib_log_handles_invalid_message(self):
        # Given
        logger = Logger('example-app', 'INFO', None, 1024, 1, False, 'message')
        record = MagicMock()
        record.msg = object()
        event_dict = {'_record': record, 'untouched': 'value'}

        with patch('builtins.print') as print_mock:
            # When
            result = logger._enrich_stdlib_log(logging.getLogger('x'), 'info', event_dict)

        # Then
        self.assertIs(result, event_dict)
        self.assertEqual('value', event_dict.get('untouched'))
        print_mock.assert_called_once()
        self.assertEqual('Failed to handle stdlib log record:', print_mock.call_args.args[0])

    def test_get_foreign_prechain_appends_stdlib_enricher(self):
        # Given
        logger = Logger('example-app', 'INFO', None, 1024, 1, False, 'message')
        logger._shared_processors = ['p1', 'p2']

        # When
        prechain = logger._get_foreign_prechain()

        # Then
        self.assertEqual(['p1', 'p2'], prechain[:-1])
        self.assertIs(prechain[-1].__self__, logger)
        self.assertIs(prechain[-1].__func__, Logger._enrich_stdlib_log)


if __name__ == '__main__':
    unittest.main()
