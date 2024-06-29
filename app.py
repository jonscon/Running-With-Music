############ Flask App Environmental Variables ############

import os, random, time

from flask import Flask, redirect, render_template, flash, session, g, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, PlaylistForm, MusicForm, NewRunForm
from models import db, connect_db, User, Playlist, Song, Run

############ Spotify Environmental Variables ############

from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

############ Configure Flask App ############

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = ('postgresql://postgres.roaatkovyyztyhfwwnxc:xZd3BP29sSceddQB@aws-0-us-west-1.pooler.supabase.com:6543/postgres')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
app.app_context().push()
db.create_all()

app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"
# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

############ User Signup/Login/Logout ############

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                name=form.name.data,
                username=form.username.data,
                password=form.password.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    # Deletes user ID from session
    do_logout()
    flash("See you next time!", "success")
    return redirect('/')

############ Music Feature Routes ############

@app.route('/music/create_playlist', methods=["GET", "POST"])
def create_playlist():
    """Create a playlist."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    form = PlaylistForm()

    if form.validate_on_submit():
        playlist_name = form.name.data

        # Create playlist and add to database
        playlist = Playlist(name=playlist_name, user_id=session[CURR_USER_KEY])
        db.session.add(playlist)
        db.session.commit()
        return redirect(f'/music/{playlist.id}/prompt')

    return render_template('/music-feature/create-playlist.html', form=form)

@app.route('/music/<int:playlist_id>/edit')
def edit_playlist(playlist_id):
    """Allow user to edit their playlist songs."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    # Set playlist's mood to None
    playlist = Playlist.query.get_or_404(playlist_id)
    playlist.mood = None
    
    # Delete all the songs from the playlist
    Song.query.filter(Song.playlist_id == playlist_id).delete()
    db.session.commit()

    # Redirect the user to the prompts page
    flash("Let's recurate your playlist again...", "info")
    return redirect(f'/music/{playlist_id}/prompt')
    

@app.route('/music/<int:playlist_id>/prompt', methods=["GET", "POST"])
def playlist_prompts(playlist_id):
    """Prompt user with questions to curate their playlist."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = MusicForm()
    playlist = Playlist.query.get(playlist_id)

    # Prevent the user from going back to the prompts page and adding more songs
    if len(playlist.songs) == 30:
        flash("Going back will cause a form resubmission. To edit, click the 'Edit Playlist' button.", "info")
        return redirect(f"/music/{playlist_id}/playlist")
    
    # Once user submits their answers, create a playlist
    if form.validate_on_submit():

        # Retreive inputs from user
        mood = form.mood.data
        artist_1 = form.artist_1.data
        artist_2 = form.artist_2.data
        artist_3 = form.artist_3.data

        # Token for all API requests
        token = get_token()

        # Set up lists
        artist_ids = []
        first_tracklist = []

        # Step 1: Get the Spotify ID of the artist using Spotify API request
        artist1_id = get_artist_id(token, artist_1)
        artist2_id = get_artist_id(token, artist_2)
        artist3_id = get_artist_id(token, artist_3)
        
        # Add artist IDs to a list for easy access
        artist_ids.extend([id for id in [artist1_id, artist2_id, artist3_id]])

        # Step 2: Gather songs from the top 3 artists, and add it to the master tracklist
        for id in artist_ids:
            songs = get_songs_by_artist(token, id)
            first_tracklist.extend(songs)
        
        # Step 3: Gather recommendations based on artists and mood, and add it to master tracklist
        tracks = get_recommendations(token, artist1_id, artist2_id, artist3_id, mood)
        for track in tracks:
            first_tracklist.append(track)

        # Step 4: Shuffle master tracklist and limit it to 30 songs
        random.shuffle(first_tracklist)

        # Convert tracklist into a list to slice the first 30 songs
        master_tracklist = first_tracklist[:30]

        # Step 5: Add tracks and songs to the database
        for track in master_tracklist:
            artists = []
            # Get artists of each song
            for artist in track['artists']:
                artists.append(artist['name'])
            
            # If there are multiple artists, separate them by commas
            artists_string = ', '.join(map(str, artists))
            song = Song(name=track['name'], artist=artists_string, playlist_id=playlist_id)
            db.session.add(song)

        # Extra Step: Add mood to playlist for reference
        mood_choices = dict(form.mood.choices)
        mood_label = mood_choices[mood]
        playlist.mood = mood_label
        
        db.session.add(playlist)
        db.session.commit()
        
        flash("Welcome to your running playlist! Feel free to add these songs to a playlist for your next run!", "success")

        return redirect(f"/music/{playlist_id}/playlist")

    return render_template("/music-feature/music-prompts.html", form=form)
    
@app.route('/music/<int:playlist_id>/playlist')
def show_playlist(playlist_id):
    """Show curated playlist."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    playlist = Playlist.query.get(playlist_id)

    # Redirect the user to the prompts page if the playlist has been made but no songs have been added
    if len(playlist.songs) == 0:
        flash("This playlist needs a little more before it's complete...", "info")
        return redirect(f'/music/{playlist_id}/prompt')

    return render_template("/music-feature/playlist.html", playlist=playlist)

@app.route('/music/<int:playlist_id>/delete')
def delete_playlist(playlist_id):
    """Delete playlist."""

    playlist = Playlist.query.get(playlist_id)
    db.session.delete(playlist)
    db.session.commit()

    return redirect('/')

@app.route('/artist-suggestions', methods=['POST'])
def retrieve_10_artists():
    """Retrieve array from Spotify API based on query (this route is called from 'search.js')."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    # Get JSON and convert into Python dictionary
    output = request.get_json()
    js_result = json.loads(output)

    # Retrieve list of artists
    token = get_token()
    results = search_for_artist(token, js_result['query'], 10)

    # Create a new array with the top 10 artists returned from the search
    artist_results = []
    for result in results:
        artist_results.append(result["name"])
    return artist_results

############ Running Log Routes ############

@app.route("/log/<int:user_id>")
def show_running_log(user_id):
    """Display running log."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    # Get all runs for the user
    runs = (Run.query.filter(Run.user_id == user_id).all())

    return render_template("/running-log/running-log.html", user_id=user_id, runs=runs)

@app.route("/log/<int:user_id>/new", methods=["GET", "POST"])
def add_new_run(user_id):
    """Add a new run to the running log."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    form = NewRunForm()
    
    if form.validate_on_submit():
        # Exract data from the submitted form
        week = form.week.data
        day = form.day.data
        distance = form.distance.data
        time = form.time.data
        pace = form.pace.data
        notes = form.notes.data

        run = Run(week=week, day=day, distance=distance, time=time, pace=pace, notes=notes, user_id=user_id)
        db.session.add(run)
        db.session.commit()

        return redirect(f"/log/{user_id}")
    
    return render_template("/running-log/new-run.html", form=form)

@app.route("/delete-run", methods=["POST"])
def delete_run():
    """Delete run from database."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    # Get JSON and convert into Python dictionary
    output = request.get_json()
    js_result = json.loads(output)

    run = Run.query.get_or_404(js_result['run_id'])
    db.session.delete(run)
    db.session.commit()
    return 'ok'

############ Homepage Routes ############

@app.route("/")
def homepage():
    """Show homepage:
    
    - anon users: signup/login page
    - logged in: music page
    """

    if g.user:
        playlists = Playlist.query.filter_by(user_id=g.user.id).all()
        return render_template('home.html', playlists=playlists)

    else:
        return render_template("home-anon.html")

############ Artist and Song Functions ############

def get_artist_id(token, artist):
    """Get the Spotify ID of the artist using a Spotify API request."""

    # Use search_for_artist function to contact Spotify's API
    result = search_for_artist(token, artist, 1)
    artist_id = result[0]["id"]

    return artist_id


############ Spotify API Functions ############
# In order to send requests to the Spotify API, we need to get an access token using the Client ID and Client Secret
# provided by the Spotify Web API.

load_dotenv()

# Set Client ID and Client Secret
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    """Get access token with client_id and client_secret, which we will use in requests to the API to retrieve data."""

    # Set up parameters for the request
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    # From Spotify's API Web Documentation
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    # Get token through POST request
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_headers(token):
    """Gets the header for any future requests with the generated access token from get_token()."""
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, query, limit):
    """Search for artists to show as suggstions under search bar."""

    # Set up the URL for the API request
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_headers(token)
    query = f"?q=artist:{query}&type=artist&limit={limit}"

    query_url = url + query
    result = get(query_url, headers=headers)

    # Parse the JSON string returned from Spotify API into a Python object
    json_result = json.loads(result.content)["artists"]["items"]
    return json_result
    
def get_songs_by_artist(token, artist_id):
    """Get top songs of artist."""

    # Set up the URL for the API request
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_headers(token)

    result = get(url, headers=headers)
    # Parse the JSON string returned from Spotify API into a Python object
    json_result = json.loads(result.content)["tracks"]
    
    return json_result

def get_recommendations(token, artist1, artist2, artist3, mood):
    """Get recommendations based on top artists and mood."""
    
    # Based on the user's mood, set the following parameters:
    # Valence - the musical positvieness of a song.
    # Danceability - how suitable a song is for dancing based on tempo, rhythm, and other elements.
    # Energy - the percepted intensity and activity.
    if mood == 'low':
        min = 0
        max = 0.33
    elif mood == 'mid':
        min = 0.34
        max = 0.66
    elif mood == 'high':
        min = 0.67
        max = 1.00
    
    url = f'https://api.spotify.com/v1/recommendations?market=US&seed_artists={artist1},{artist2},{artist3}&limit=30&min_valence={min}&max_valence={max}&min_danceability={min}&max_danceability={max}&min_energy={min}&max_energy={max}'
    headers = get_auth_headers(token)

    result = get(url, headers=headers)
    json_result = json.loads(result.content)['tracks']
    return json_result