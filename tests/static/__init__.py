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
        result = data[oid]
        if type(result) == list:
            result = "\n".join(result[0:])
        return result

    @staticmethod
    def _get_mocked_getcmd(oid, data, *args, **kwargs):
        result = data[oid]
        if type(result) == list:
            result = "\n".join(result[0:])
        return [0, 0, 0, [[0, result.encode('ascii', 'ignore')], 0]]

    @staticmethod
    def _get_mocked_wireless_links(oid):
        return_data = {
            '1.3.6.1.4.1.14988.1.1.1.2.1': [0, 0, 0, [[[0, 0], 0]] * 28],
            '1.3.6.1.4.1.14988.1.1.1.2.1.3': [0, 0, 0, [0, 0]],
            '1.3.6.1.4.1.14988.1.1.1.2.1.3.0': [None, 0, 0, []],
        }
        return return_data[oid]
