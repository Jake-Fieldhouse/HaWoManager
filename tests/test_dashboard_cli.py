import json
import unittest
import requests_mock

from dashboard_cli import create_dashboard


class TestDashboardCLI(unittest.TestCase):
    def test_create_new_view(self):
        posted = {}
        with requests_mock.Mocker() as m:
            m.get("http://ha/api/lovelace/config", json={})

            def record(request, context):
                posted['json'] = json.loads(request.text)
                return {}

            m.post("http://ha/api/lovelace/config", json=record)

            create_dashboard("http://ha", "tok", "device1", "rgb(1,2,3)")

        cfg = posted['json']
        self.assertEqual(cfg['views'][0]['path'], 'womgr')
        titles = [c.get('title') for c in cfg['views'][0]['cards']]
        self.assertIn('device1', titles)

    def test_update_existing_view(self):
        existing = {'views': [{'path': 'womgr', 'cards': [{'type': 'vertical-stack', 'title': 'old'}]}]}
        posted = {}
        with requests_mock.Mocker() as m:
            m.get("http://ha/api/lovelace/config", json=existing)

            def record(request, context):
                posted['json'] = json.loads(request.text)
                return {}

            m.post("http://ha/api/lovelace/config", json=record)

            create_dashboard("http://ha", "tok", "device2")

        cfg = posted['json']
        view = next(v for v in cfg['views'] if v.get('path') == 'womgr')
        titles = [c.get('title') for c in view['cards']]
        self.assertEqual(titles, ['old', 'device2'])

if __name__ == '__main__':
    unittest.main()
