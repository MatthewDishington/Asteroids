import unittest
from unittest import *
from ScoreDatabase import *
import os

class TestScoreDatabase(TestCase):

    database_name = "test.sqlite"

    def cleardown(self):
        if os.path.isfile(self.database_name):
            os.remove(self.database_name)

    def test_create_database(self):

        self.cleardown()

        db = ScoreDatabase(self.database_name)

        db.create_database()
        cursor = db.get_cursor()
        cursor.execute("select count() from User")

    def test_save_score(self):

        self.cleardown()
        db = ScoreDatabase(self.database_name)

        db.create_database()

        db.save_score("Matthew", 555)

    def test_get_high_scores(self):

        self.cleardown()
        db = ScoreDatabase(self.database_name)

        db.create_database()
        db.save_score("Matthew", 555)

        scores = db.get_high_scores()

        self.assertEquals(1, len(scores))

        (position, name, score) = scores[0]

        self.assertEquals("Matthew",name)
        self.assertEquals(555, score)

    def test_get_rank(self):

        self.cleardown()
        db = ScoreDatabase(self.database_name)

        db.create_database()

        rank = db.get_rank(40)

        # should be top score
        self.assertEquals(1,rank)

        db.save_score("Matthew", 555)

        # is the score 2nd
        rank = db.get_rank(40)
        self.assertEquals(2,rank)

        # is the top
        rank = db.get_rank(880)
        self.assertEquals(1,rank)

