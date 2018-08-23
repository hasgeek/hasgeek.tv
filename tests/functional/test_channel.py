import json
from ..fixtures import TestCaseBase


class ChannelUnitTest(TestCaseBase):
    def test_channel_page(self):
        response = self.test_client.get_ajax('/test-channel/')
        assert response.status_code == 200

        json_resp = json.loads(response.data)
        assert 'channel' in json_resp
        assert 'title' in json_resp['channel']
        assert json_resp['channel']['title'] == u"Test Channel"

        assert 'playlists' in json_resp
        assert type(json_resp['playlists']) == list
        assert len(json_resp['playlists']) == 1

        playlist1 = json_resp['playlists'][0]

        assert 'title' in playlist1
        assert playlist1['title'] == 'Test Playlist 1'
