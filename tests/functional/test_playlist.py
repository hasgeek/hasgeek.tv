import json

from ..fixtures import TestCaseBase


class PlaylistFunctionalTest(TestCaseBase):
    def test_playlist_page(self):
        response = self.test_client.get_ajax('/test-channel/test-playlist-1')
        self.assertEqual(response.status_code, 200)
        json_resp = json.loads(response.data)

        self.assertIn('playlist', json_resp)
        playlist1 = json_resp['playlist']

        self.assertIn('title', playlist1)
        self.assertEqual(playlist1['title'], 'Test Playlist 1')
        self.assertIn('videos', playlist1)
