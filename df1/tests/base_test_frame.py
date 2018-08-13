from unittest import TestCase


class BaseTestFrame(TestCase):
    def _assert_bytes_equal(self, expected, actual):
        def format_hex(c):
            return hex(c)[2:]

        expected = [format_hex(c) for c in expected]
        actual = [format_hex(c) for c in actual]
        self.assertEquals(expected, actual)
