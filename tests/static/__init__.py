import json
import os

class MockOutputMixin(object):
    @staticmethod
    def _load_mock_json(file):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        with open(base_dir + file) as f:
            data = json.load(f)
        return data

    @staticmethod
    def _get_mocked_value(oid, data, *args, **kwargs):
        return data[oid]
