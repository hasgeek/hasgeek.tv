import unittest
from hgtv import app
from hgtv.models import db, Channel, Playlist, CHANNEL_TYPE


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.app = app

        self.test_client = app.test_client()
        self.test_client.get_ajax = lambda url: self.test_client.get(url,
            headers=[('Accept', 'application/json'), ('X-Requested-With', 'XMLHttpRequest')])

        # Establish an application context before running the tests.
        self.ctx = app.app_context()
        self.ctx.push()

        # Create database
        print("Creating test database")
        db.create_all()

        # Create needed objects
        print("Creating db objects")
        channel = Channel(userid=u"testuserid", name=u"test-channel", title=u"Test Channel", type=CHANNEL_TYPE.UNDEFINED)
        db.session.add(channel)

        db.session.commit()  # need this for channel.id below

        playlist1 = Playlist(channel_id=channel.id, name=u"test-playlist-1", title=u"Test Playlist 1")
        db.session.add(playlist1)

        # Commit objects
        db.session.commit()

    def tearDown(self):
        # Drop database once testing is done
        print("Dropping test database")
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()

