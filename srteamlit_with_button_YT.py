import streamlit as st
import pandas as pd
import numpy as np
from IPython.display import IFrame
from requests import get
from bs4 import BeautifulSoup as bs
import spotipy
import config
import spotipy
import json
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import random
import pickle
import pytube

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id= config.client_id,
                                                           client_secret= config.client_secret))

def choose_song(results):
    # function allow user to choose song of interest
    #input, user will input song number
    #output: song id
    count=1
    for item in results['tracks']['items']:
        #print(item['name'])
        song_name=item['name']
        id=item['id']
        artist= item['artists'][0]['name']
        print(f"{count}. Song title: {song_name} by: {artist}")
        count+=1
    song=input('choose song by entering 1, 2 or 3')
    song_id=results['tracks']['items'][int(song)-1]['id']

    return song_id    
   

def load(filename = "filename.pickle"): 
    try: 
        with open(filename, "rb") as f: 
            return pickle.load(f) 
    except FileNotFoundError: 
        print("File not found!") 

def transforming_features(track_id):
    au_features = sp.audio_features(track_id)
    df_new_song=pd.DataFrame(au_features)    
    
    df_new_song_features=df_new_song[['danceability', 'energy', 'loudness','speechiness', 'acousticness', 'instrumentalness', 'liveness','valence', 'tempo']]
    scaller_try = load("Model_final/scaler_7.pickle")
    scaled_new_song = scaller_try.transform(df_new_song_features)
    #df_new_song
# Loading the Stabdardscaler
    #df_for_scalling = df_new_song[['danceability', 'energy', 'loudness',  'speechiness',   'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']]
    #df_for_clustering = scaled_new_song[['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness','valence', 'tempo']]
    cluster_new = load("Model_final/kmeans80_9features_of130k.pickle")
    #cluster_new_song = cluster_new.transform(df_for_clustering)
    k_num=cluster_new.predict(scaled_new_song)

    return k_num
    
def random_song_selection(k_num):
##Function: choose random selection of songs based on cluster of chosen song 
# input: k_number
#output: selection of 5 songs
# import df of songs, with cluster columns assigned
#
    df=pd.read_csv('library_cluster_80_130k_9featur.csv', index_col=[0])
    df_by_k=df.loc[df['clusters']==k_num[0]] 
    df_by_k_list=df_by_k['id'].to_list()
    df_by_k_list=list(set(df_by_k_list))
    #print(df_by_k_list)
    #song_selection=random.sample(df_by_k_list, 5)
    #song_selection=random.choices(df_by_k_list, k=5,)
    song_selection = df_by_k_list[:5]
    return song_selection

st.set_page_config(page_title="Music",page_icon="🎵",initial_sidebar_state="expanded")

df = pd.read_csv('library_cluster_80_130k_9featur.csv', index_col=0)

def update_params():
    st.experimental_set_query_params(song=st.session_state.qp)

import textwrap, random
import streamlit.components.v1 as components
mjstr = "🤘🎼🎵🎶 ♩♪♫♬♭♮♯ø 🎤🎸🎻🎷🎺📯🎹📻 🎧🎙🎚🎛📻📣📢🔊🔉🔈"
mjlist = textwrap.wrap(mjstr,width=1)
mj = random.choice(mjlist)
st.title("Music Recommendation by Gemma and Elnara "+mj)

param = st.experimental_get_query_params()
# song = "Lucy in the Sky"
#song = random_song(df['id'])

search = st.sidebar.text_input('Enter Track',key='qp',on_change=update_params)
st.experimental_set_query_params(song = search)
try:
    results = sp.search(q=search,type='track')
    
    track = results['tracks']['items'][0]
    name = track['name']
    album = track['album']['name']
    artist = track['artists'][0]['name']
    duration_ms = track['duration_ms']
    popularity = track['popularity']
    img_album = track['album']['images'][1]['url']
    external_url = track['external_urls']['spotify']
    track_id = track['id']
    st.sidebar.image(img_album, caption=album)
    display = st.selectbox('Display',('Song details','Recommendations'))

    if display == 'Song details':
        
        # Main song panel

        url = "https://open.spotify.com/track/"+str(track_id)
        # st.markdown('![spoticon](../code/spoticon.png)')
        st.markdown('<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Spotify_icon.svg/232px-Spotify_icon.svg.png" width=20>Play: '+url,unsafe_allow_html=True)
        yt = st.button('Find on Youtube')
        uri_link = src="https://open.spotify.com/embed/track/"+track_id+"?utm_source=generator"
        components.iframe(uri_link, height=300)

        if yt:
            try:
                for_yt = artist + name
                r = pytube.Search(for_yt)
                for v in r.results:
                    urls = []
                    #(v.title}\n{v.watch_url}\n")
                    urls.append(v.watch_url)
                st.write(v.title)
                st.video(urls[0])
                             
                
            except:
                st.write('Did not find the track on Youtube')
    
    elif display == "Recommendations":
        k_num=transforming_features(track_id)
        song_selection=random_song_selection(k_num)
        for ele in song_selection:
            src="https://open.spotify.com/embed/track/"+ele+"?utm_source=generator"
            components.iframe(src, height=300)
except:
    st.write('Nothing found yet')