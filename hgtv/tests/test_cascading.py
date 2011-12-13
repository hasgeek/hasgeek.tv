#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
import tempfile
import json
import hgtv

class CascadingTestCase(unittest.TestCase):

    def setUp(self):
        """
        Setup the in-memory sqlite database and add sample data from
        test_cascade.json.
        """
        self.db = hgtv.models.db
        self.db.create_all()
        path_to_file = os.path.abspath(os.path.dirname(__file__))
        json_data = unicode(open(os.path.join(path_to_file,
            'test_cascading.json')).read(), 'utf-8')
        data = json.loads(json_data)
        ashow = hgtv.models.Show(**data['show'])
        aseason = hgtv.models.Season(**data['season'])
        video1 = hgtv.models.Video(**data['video'][0])
        video2 = hgtv.models.Video(**data['video'][1])
        self.db.session.add(ashow)
        self.db.session.add(aseason)
        self.db.session.add(video1)
        self.db.session.add(video2)
        self.db.session.commit()

    def test_show_delete(self):
        """
        Delete a show and ensure that associated seasons and videos get
        deleted.
        """
        ashow = hgtv.models.Show.query.get(1)
        self.db.session.delete(ashow)
        self.db.session.commit()
        aseason = hgtv.models.Season.query.get(1)
        avideo = hgtv.models.Video.query.get(1)
        self.assertEqual(aseason, None)
        self.assertEqual(avideo, None)

    def test_season_delete(self):
        """
        Delete a season, and ensure the associated videos are deleted while the
        show remains intact.
        """
        aseason = hgtv.models.Season.query.get(1)
        self.db.session.delete(aseason)
        self.db.session.commit()
        ashow = hgtv.models.Show.query.get(1)
        avideo = hgtv.models.Video.query.get(1)
        self.assertNotEqual(ashow, None)
        self.assertEqual(avideo, None)
    
    def test_tags_delete(self):
        """
        Delete a tag and ensure the associate videos are not deleted.
        """
        avideo = hgtv.models.Video.query.get(1)
        never = hgtv.models.Tag.get(u'never')
        gonna = hgtv.models.Tag.get(u'gonna')
        snowman = hgtv.models.Tag.get(u'☃')
        avideo.tags = [never, gonna, snowman]
        self.db.session.commit()
        self.db.session.delete(snowman)
        self.db.session.commit()
        self.assertEqual(len(hgtv.models.Tag.query.all()), 2)
        self.assertEqual(len(hgtv.models.Video.query.all()), 2)
        self.db.session.commit()

    def test_video_delete(self):
        """
        Delete a video and ensure that the shared tags between 2 videos
        and associated tags are not deleted.
        """
        video1 = hgtv.models.Video.query.get(1)
        video2 = hgtv.models.Video.query.get(2)
        never = hgtv.models.Tag.get(u'never')
        gonna = hgtv.models.Tag.get(u'gonna')
        snowman = hgtv.models.Tag.get(u'☃')
        video1.tags = [never, gonna, snowman]
        video2.tags = [never, snowman]
        self.db.session.commit()
        self.db.session.delete(video1)
        self.db.session.commit()
        self.assertEqual(len(hgtv.models.Tag.query.all()), 3)
        self.db.session.delete(snowman)
        self.db.session.commit()
        self.assertEqual(len(hgtv.models.Tag.query.all()), 2)

    def tearDown(self):
        self.db.session.expunge_all()
        self.db.drop_all()
