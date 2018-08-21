from hgtv.models import Channel, CHANNEL_TYPE


def test_new_channel():
    test_channel = Channel.query.filter_by(name=u"test-channel").first()
    assert test_channel.title == u"Test Channel"
    assert test_channel.type == CHANNEL_TYPE.UNDEFINED
