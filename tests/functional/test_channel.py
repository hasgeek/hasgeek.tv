import json
from ..fixtures import TestCaseBase


class ChannelFunctionalTest(TestCaseBase):
    def test_channel_page(self):
        response = self.test_client.get_ajax('/test-channel/')
        assert response.status_code == 200

        json_resp = json.loads(response.data)
        self.assertIn('channel', json_resp)
        self.assertIn('title', json_resp['channel'])
        self.assertEqual(json_resp['channel']['title'], u"Test Channel")

        self.assertIn('playlists', json_resp)
        self.assertEqual(len(json_resp['playlists']), 1)

        playlist1 = json_resp['playlists'][0]

        self.assertIn('title', playlist1)
        self.assertEqual(playlist1['title'], 'Test Playlist 1')
