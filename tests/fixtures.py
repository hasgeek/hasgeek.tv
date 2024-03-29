import unittest

from hgtv import app
from hgtv.models import CHANNEL_TYPE, Channel, Playlist, Video, db


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.app = app

        self.test_client = app.test_client()
        self.test_client.get_ajax = lambda url: self.test_client.get(
            url,
            headers=[
                ('Accept', 'application/json'),
                ('X-Requested-With', 'XMLHttpRequest'),
            ],
        )

        # Establish an application context before running the tests.
        self.ctx = app.app_context()
        self.ctx.push()

        # Create database
        print("Creating test database")  # noqa: T201
        db.create_all()

        # Create needed objects
        print("Creating db objects")  # noqa: T201
        channel = Channel(
            userid="testuserid",
            name="test-channel",
            title="Test Channel",
            type=CHANNEL_TYPE.UNDEFINED,
        )
        db.session.add(channel)

        playlist1 = Playlist(
            channel=channel, name="test-playlist-1", title="Test Playlist 1"
        )
        db.session.add(playlist1)

        video1 = Video(
            playlist=playlist1,
            name="test-video-1",
            title="Test Video 1",
            video_url="https://www.youtube.com/watch?v=testvideo1",
        )
        playlist1.videos.append(video1)
        db.session.add(video1)

        # Commit objects
        db.session.commit()

    def tearDown(self):
        # Drop database once testing is done
        print("Dropping test database")  # noqa: T201
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()
