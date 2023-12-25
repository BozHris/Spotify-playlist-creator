from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import os

#web scraping stage
your_date = input("Please enter the date you want your song to be created. Enter like YYYY-MM-DD: ")
billboard_songs_url = f"https://www.billboard.com/charts/hot-100/{your_date}/"
response = requests.get(billboard_songs_url).text
soup = BeautifulSoup(response, "html.parser")
songs = soup.select("li ul li h3")
final_songs = [i.getText().strip() for i in songs]
artists = soup.select('li ul li h3 + span')
final_artists = [i.getText().strip() for i in artists]




#spotify stage
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"

client_data ={
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'client_credentials'
}
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID,
                                                           client_secret=CLIENT_SECRET))
#
spotify_token = requests.post("https://accounts.spotify.com/api/token",
                              headers=headers,
                              data=client_data
                              )

access_token = spotify_token.json()['access_token']
print(spotify_token.json())
#getting the songs

#getting the artists list ready by replacing " " with "+" in the artist's name
final_artists = [i.replace(" ","+") for i in final_artists]



song_header = {"Authorization": "Bearer"+" "+f"{spotify_token.json()['access_token']}"}
#
def search_song_uri(name, artist):
    search_url = "https://api.spotify.com/v1/search"
    query = f"?q={name}+{artist}&type=track&limit=1"
    query_url = search_url + query

    song = requests.get(url=query_url, headers=song_header)
    try:
        song_uri = song.json()["tracks"]["items"][0]["uri"]
    except KeyError:
        pass
    else:
        return song_uri

song_uris = []

for i in range(0,len(final_songs)):
    song_uris.append(search_song_uri(final_songs[i],final_artists[i]))


#getting user_id


user_url = "https://api.spotify.com/v1/me/"

#
response = requests.get(url=user_url,headers=song_header).json()
print(response)
user_id = response["id"]
user = requests.get(url=user_url, headers=song_header)
print(user.json())

#creating the playlist and adding the songs to it

playlist_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
#
body = {
     "name": f"Bilboard top 100 {your_date}",
     "description": "New playlist description",
     "public": False,


 }
playlist_header = {
    "Content-Type": "application/json",
    "Authorization": "Bearer"+" "+f"{access_token}"
}
#
playlist = requests.post(url=playlist_url,data=json.dumps(body),headers=playlist_header)
playlist_id = playlist.json()["id"]

#ADDING TRACKS
track_adding_endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

for i in range(len(song_uris)):
    body = {
        "uris": [song_uris[i]],
        "position": i
    }
    add_tracks = requests.post(url=track_adding_endpoint,data=json.dumps(body),headers=playlist_header)

