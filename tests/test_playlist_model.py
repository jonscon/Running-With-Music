"""Playlist model tests."""


import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Playlist, Song

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///run-test"

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for playlist."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.uid = 94566
        u = User.signup("testname", "testing", "passwor")
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_playlist_model(self):
        """Does basic model work?"""

        p = Playlist(
            name = "Test Playlist",
            mood = "Upbeat and Groovy",
            user_id = self.uid
        )

        db.session.add(p)
        db.session.commit()

        # User should have 1 playlist
        self.assertEqual(len(self.u.playlist), 1)
        self.assertEqual(self.u.playlist[0].name, "Test Playlist")

    def test_playlist_songs(self):
        p = Playlist(
            name = "Test Playlist",
            mood = "Upbeat and Groovy",
            user_id = self.uid
        )
        p.id = 1

        s = Song(
            name = "dashstar",
            artist = "Knock2",
            playlist_id = 1
        )

        db.session.add_all([p, s])
        db.session.commit()

        playlist = self.u.playlist[0]
        self.assertEqual(len(playlist.songs), 1)
        self.assertEqual(playlist.songs[0].name, "dashstar")
