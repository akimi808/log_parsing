import unittest
from unittest import TestCase
from io import StringIO

from logtail import *

class DateExtractorTest(TestCase):

    def test_simple_extract(self):
        input = '109.169.248.247 - - [12/Dec/2015:18:25:11 +0100] "GET /administrator/ HTTP/1.1" 200 4263 "-" "Mozilla/5.0 (Windows NT 6.0; rv:34.0) Gecko/20100101 Firefox/34.0" "-"'
        self.assertEqual(parse_str(input), "12/Dec/2015:18:25:11")

    def test_empty_input(self):
        input = ''
        self.assertEqual(parse_str(input), "")

class LogTailTest(TestCase):

    def test_empty_file(self):
        log = StringIO("")
        date = "12/Dec/2015:18:25:11"
        self.assertEqual(logtail(log, date), "")

if __name__ == "__main__":
    unittest.main(verbosity=2)