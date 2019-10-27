from hgtv.models import Video
from hgtv.views.video import process_slides
from ..fixtures import TestCaseBase


class VideoUnitTest(TestCaseBase):
    def test_new_video(self):
        test_video1 = Video.query.filter_by(name=u"test-video-1").first()
        self.assertEqual(test_video1.title, u"Test Video 1")

    def test_slides_process_speakerdeck(self):
        test_video1 = Video.query.filter_by(name=u"test-video-1").first()
        self.assertEqual(test_video1.slides_source, u'')
        self.assertEqual(test_video1.slides_sourceid, u'')
        process_slides(test_video1)
        self.assertEqual(test_video1.slides_source, u'speakerdeck')
        self.assertNotEqual(test_video1.slides_sourceid, u'')

    def test_slides_process_slideshare(self):
        test_video2 = Video.query.filter_by(name=u"test-video-2").first()
        self.assertEqual(test_video2.slides_source, u'')
        self.assertEqual(test_video2.slides_sourceid, u'')
        process_slides(test_video2)
        self.assertEqual(test_video2.slides_source, u'slideshare')
        self.assertNotEqual(test_video2.slides_sourceid, u'')
