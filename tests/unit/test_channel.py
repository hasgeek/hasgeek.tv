from hgtv.models import CHANNEL_TYPE, Channel

from ..fixtures import TestCaseBase


class ChannelUnitTest(TestCaseBase):
    def test_new_channel(self):
        test_channel = Channel.query.filter_by(name="test-channel").first()
        assert test_channel.title == "Test Channel"
        assert test_channel.type == CHANNEL_TYPE.UNDEFINED
