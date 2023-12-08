from tkinter import E
from instaloader.instaloader import Instaloader
from instaloader.structures import Profile
from datetime import datetime, timedelta
from itertools import dropwhile, takewhile
from dotenv import load_dotenv
import instaloader.exceptions
from requests import session
import os



def return_captions(profiles,session_file):
    

    with Instaloader(quiet=True) as L:
        try:
            L.load_session_from_file("bencebansaghi",filename=session_file)
        except instaloader.exceptions.ConnectionException as e:
            print(f"Login error: {e}")
        except Exception as e:
            print(f"Unknown error: {e}")

    captions = []
    for usernames in profiles:
        posts = Profile.from_username(L.context, usernames).get_posts() 
        now = datetime.now()
        one_week_ago = now - timedelta(weeks=1)
        for post in takewhile(lambda p: p.date > one_week_ago, dropwhile(lambda p: p.date > now, posts)):
            L.download_post(post, usernames)
            captions.append(post.caption)

    return captions

if __name__ == "__main__":
    profiles = ["aether_ry", "lahoevents", "koeputkiappro", "aleksinappro", "lasolary", "lymo.ry", "lirory", "Moveolahti", "koe_opku", "linkkiry"]
    session_file_path = os.getcwd()
    session_file_name = "\\session-bencebansaghi"
    session_file = session_file_path + session_file_name
    captions = return_captions(profiles,session_file)
    for caption in captions:
        print(caption)

