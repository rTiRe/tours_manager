"""Tests for errors utils."""

from django.test import TestCase

from manager.views_utils.errors_utils import convert_errors

FIELD1 = 'field1'


class ConvertErrorsTestCase(TestCase):
    """Tests class for errors converter."""

    def test_single_error(self):
        """Test with single error."""
        errors = {FIELD1: ["['error message']"]}
        expected_result = {'field1': 'error message'}
        self.assertEqual(convert_errors(errors), expected_result)

    def test_multiple_fields(self):
        """Test with multiple fields."""
        errors = {
            FIELD1: ["['error message']"],
            'field2': ["['another error message']"],
        }
        expected_result = {
            FIELD1: 'error message',
            'field2': 'another error message',
        }
        self.assertEqual(convert_errors(errors), expected_result)

    def test_no_brackets_error(self):
        """Test with errors dict without brackets."""
        errors = {FIELD1: ['error message']}
        expected_result = {}
        self.assertEqual(convert_errors(errors), expected_result)

    def test_empty_errors(self):
        """Test with empty errors dict."""
        errors = {}
        expected_result = {}
        self.assertEqual(convert_errors(errors), expected_result)
