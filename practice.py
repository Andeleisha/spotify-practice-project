import spotipy
spotify = spotipy.Spotify()
results = spotify.search(q='artist:' + 'Adele', type='artist')
print(results)