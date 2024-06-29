"""Models for Running App."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

############ User Model and Methods ############

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Text, nullable=False)

    username = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    playlist = db.relationship('Playlist', backref='user')

    runs = db.relationship('Run', backref='user')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"
    
    ######## Signup and Authentication Methods ########
    @classmethod
    def signup(cls, name, username, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            name=name,
            username=username,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    

############ Music Models ############

class Playlist(db.Model):
    """Playlist."""

    __tablename__ = 'playlists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text, nullable=False)

    mood = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)

    songs = db.relationship('Song', cascade="all,delete", backref='playlist')

class Song(db.Model):
    """Song on Spotify."""

    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text, nullable=False)

    artist = db.Column(db.Text, nullable=False)
    
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id', ondelete='cascade'), nullable=False)

    __table_args__ = (
        UniqueConstraint('playlist_id', 'name', 'artist', name='unique_song_in_playlist'),
    )


############ Running Log Models ############
class Run(db.Model):
    """Recorded Run."""

    __tablename__ = 'runs'

    id = db.Column(db.Integer, primary_key=True)

    week = db.Column(db.Text, nullable=False)

    day = db.Column(db.Text, nullable=False)

    distance = db.Column(db.Text, nullable=False)

    time = db.Column(db.Text, nullable=False)

    pace = db.Column(db.Text)

    notes = db.Column(db.Text)

    user_id=db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)

# DO NOT MODIFY THIS FUNCTION
def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)