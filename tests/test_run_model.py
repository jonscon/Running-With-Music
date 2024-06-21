"""Run model tests."""


import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Run

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
    """Test views for run."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.uid = 94566
        u = User.signup("testname", "testing", "password")
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)
        
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_run_model(self):
        """Does basic model work?"""

        run = Run(
            week = "Week 1",
            day = "Monday",
            distance = "1 mi",
            time = "5:17",
            pace = "5:17/mi",
            notes = "All out mile for time",
            user_id = self.uid
        )
    
        db.session.add(run)
        db.session.commit()

        # User should have 1 run logged
        self.assertEqual(len(self.u.runs), 1)
        self.assertIsNotNone(self.u.runs[0])

    def test_valid_run(self):
        """Can some fields be empty?"""

        r = Run(
            week = "Week 3",
            day = "Tuesday",
            distance = "3.17 mi",
            time = "24:17",
            user_id = self.uid
        )

        db.session.add(r)
        db.session.commit()

        # User should have 1 run logged
        self.assertEqual(len(self.u.runs), 1)
        self.assertIsNotNone(self.u.runs[0])        