from django.test import TestCase

# Assuming the convert_errors function is in a module named utils
from manager.views_utils.errors_utils import convert_errors


class ConvertErrorsTestCase(TestCase):
    def test_single_error(self):
        errors = {'field1': ["['error message']"]}
        expected_result = {'field1': 'error message'}
        self.assertEqual(convert_errors(errors), expected_result)

    def test_multiple_fields(self):
        errors = {
            'field1': ["['error message']"],
            'field2': ["['another error message']"]
        }
        expected_result = {
            'field1': 'error message',
            'field2': 'another error message'
        }
        self.assertEqual(convert_errors(errors), expected_result)

    def test_no_brackets_error(self):
        errors = {'field1': ['error message']}
        expected_result = {}
        self.assertEqual(convert_errors(errors), expected_result)

    def test_empty_errors(self):
        errors = {}
        expected_result = {}
        self.assertEqual(convert_errors(errors), expected_result)
