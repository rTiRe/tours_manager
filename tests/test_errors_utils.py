from django.test import TestCase

# Assuming the convert_errors function is in a module named utils
from manager.views_utils.errors_utils import convert_errors

FIELD1 = 'field1'


class ConvertErrorsTestCase(TestCase):
    def test_single_error(self):
        errors = {FIELD1: ["['error message']"]}
        expected_result = {'field1': 'error message'}
        self.assertEqual(convert_errors(errors), expected_result)

    def test_multiple_fields(self):
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
        errors = {FIELD1: ['error message']}
        expected_result = {}
        self.assertEqual(convert_errors(errors), expected_result)

    def test_empty_errors(self):
        errors = {}
        expected_result = {}
        self.assertEqual(convert_errors(errors), expected_result)
