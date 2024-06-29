# Running with Music

### Running with Music is an two-feature application designed to help a runner decide what music they want to listen to and keep track of their runs.

[Try out Running with Music here!](https://running-with-music.onrender.com)

## Setup and Dependencies
To run the project locally on your computer, please see the following steps.

1. Clone the repository to your computer by typing `git clone git@github.com:hatchways-community/capstone-project-one-7877b031c63b401391e27c4a72169c0b.git`.

2. Navigate to the project folder `running-app` and create a virtual environment.

```
cd running-app
python3 -m venv [NAME OF VIRTUAL ENVIRONMENT]
```

3. Enter the virtual environment and install the dependencies from `requirements.txt` using `pip`.
```
source venv/bin/activate
pip install -r requirements.txt
```
*NOTE* Some computers will have a newer version of Python. If `pip install` doesn't work, try `pip3 install...`.

4. Once all dependencies have been installed, run the following command to start the application.
```
flask run
```

5. Congratulations, you can now use the app locally! Paste the local host URL in your browser to start the application.

## Features
1. The first feature of this application features a custom curation of a playlist from Spotify's API based on a user's music preferences. The application captures:
- The runner's mood for the day
- The runner's top 3 artists that best fit their music preferences

User will enter their mood:
![alt text](/readme-images/prompts.png)

As well as search for artists with the help of Spotify's search:
![alt text](/readme-images/search.png)

To be factored into creating the custom playlist:
![alt text](/readme-images/playlist.png)

2. The second feature is a running log. This feature allows the user to enter the distance, pace, and time of an individual run so that he or she can keep track of their runs over time (running log is currently capped at 10 weeks).

Enter a new run:
![alt text](/readme-images/new-run.png)

The running log:
![alt text](/readme-images/running-log.png)

## User Flow
The user will be prompted to create an account first or log in if they already have an existing account. From there, there are two main user flows.

#### Music
He or she will see the home page, which defaults to the music tab. Here, a new playlist can be created by clicking the "Create My Playlist" button. The user will enter their playlist name and create their playlist. From there, the user will select the mood that he or she is feeling, as well as search for artists that match his or her listening preferences. 

*NOTE*: You can search for an artist in each input box, as shown below.

![alt text](/readme-images/multiple-search.png)

From there, the user will be shown a custom curated playlist of 30 songs to be listened to on his or her next run. The user can also recreate or delete a playlist if desired. Once a playlist is created, the user will be able to see existing playlists on the home page. 

#### Running Log
The user can also go to the "Running Log" tab, where the user's runs will be displayed in the form of a running log. Creating a new run will prompt the user with the week, day, distance, time, pace, and additional notes of the run. Once runs have been added, the user can filter the running log view based on the week. The user can also delete a run if desired.

## Spotify API
### Link to Spotify's API: https://developer.spotify.com/

## Roadblocks with Spotify's API
Spotify's API was a little difficult to implement at first because the documentation was a little confusing to understand. However, after watching a YouTube tutorial and browsing through some Stack Overflow discusssions, I was able to successfully implement the API.

## Technologies Used
- HTML5/CSS3
- Python
- Flask
- Jinja
- JavaScript
- jQuery
- Bootstrap