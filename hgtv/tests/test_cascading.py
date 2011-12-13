#!/usr/bin/env python
import os
import unittest
import tempfile
import json
import hgtv

class CascadingTestCase(unittest.TestCase):

    def setUp(self):
        self.db = hgtv.models.db
        self.db.create_all()
        path_to_file = os.path.abspath(os.path.dirname(__file__))
        json_data = unicode(open(os.path.join(path_to_file,
            'test_cascading.json')).read(), 'utf-8')
        data = json.loads(json_data)
        ashow = hgtv.models.Show(**data['show'])
        aseason = hgtv.models.Season(**data['season'])
        avideo = hgtv.models.Video(**data['video'])
        self.db.session.add(ashow)
        self.db.session.add(aseason)
        self.db.session.add(avideo)
        self.db.session.commit()

    def test_show_delete(self):
        ashow = hgtv.models.Show.query.get(1)
        self.db.session.delete(ashow)
        self.db.session.commit()
        aseason = hgtv.models.Season.query.get(1)
        avideo = hgtv.models.Video.query.get(1)
        self.assertEqual(aseason, None)
        self.assertEqual(avideo, None)

    def test_season_delete(self):
        aseason = hgtv.models.Season.query.get(1)
        self.db.session.delete(aseason)
        self.db.session.commit()
        ashow = hgtv.models.Show.query.get(1)
        avideo = hgtv.models.Video.query.get(1)
        self.assertNotEqual(ashow, None)
        self.assertEqual(avideo, None)

    def tearDown(self):
        self.db.drop_all()
