import datetime
from unittest import TestCase

from modules.evaluator import execute_dynamic_json


class Test(TestCase):
    def test_execute_dynamic_json(self):
        input = {
                "07": { "func": "now", "args": ["MMDDhhmmss"] },
        }
        expected = {
                "07": datetime.datetime.now().strftime('%m%d%H%M%S'),
        }

        result = execute_dynamic_json(input)
        assert result == expected
