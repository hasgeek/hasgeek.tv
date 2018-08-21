import pytest
from hgtv import app
from hgtv.models import db, Channel, Playlist, CHANNEL_TYPE


@pytest.fixture
def init_database():
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

    # pytest uses yield instead of return, all code before yield becomes teardown code
    yield db

    # Drop database once testing is done
    print("Dropping test database")
    db.drop_all()


@pytest.fixture(scope='module')
def test_client():
    testing_client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    testing_client.get_ajax = lambda url: testing_client.get(url,
        headers=[('Accept', 'application/json'), ('X-Requested-With', 'XMLHttpRequest')])

    yield testing_client  # this is where the testing happens!

    ctx.pop()
