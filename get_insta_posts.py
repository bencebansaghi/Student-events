from instaloader.instaloader import Instaloader
from instaloader.structures import Profile
from datetime import datetime, timedelta
from itertools import dropwhile, takewhile
import instaloader.exceptions
import time
from dotenv import load_dotenv
import os
import shutil

def purge_profiles_dir(session_file_path): # Deletes all the files in the profiles directory
    profiles_file = session_file_path+"\\profiles"
    shutil.rmtree(profiles_file)
    if not os.path.exists(profiles_file):
        os.makedirs(profiles_file)

def return_captions(profiles_array, session_file_path,session_file_name): # Returns the captions of the posts from the last week of the given profiles as an array
    with Instaloader(quiet=True,dirname_pattern=".\\profiles",max_connection_attempts=1) as L:
        try: #first we try to login with .env variables
            load_dotenv()
            L.login(str(os.getenv("INSTA_USERNAME")), str(os.getenv("INSTA_PASSWORD"))) #casting to string is necessary because of the way dotenv works
            print("Logged in with .env variables")
        except Exception as e:
            print(".env variable login failed, trying to log in with session file.")
            try:  #if that fails, we try to load the session from a file
                L.load_session_from_file(session_file_name.split("-")[1], filename=session_file_path+session_file_name) # You can get the session file by following the steps at https://instaloader.github.io/troubleshooting.html
                print("Logged in with session file")
            except instaloader.exceptions.ConnectionException as e:
                print(f"Login error: {e}")
            except FileNotFoundError as e:
                print(f"File not found error: {e}\nPlease make sure the session is saved to the same dir as the script.")
            except Exception as e:
                print(f"Both login methods failed, unknown error: {e}")

    captions = []
    for username in profiles_array:
        print(f"Getting posts of {username}")
        try:
            posts = Profile.from_username(L.context, username).get_posts() 
        except instaloader.exceptions.ProfileNotExistsException as e:
            print(f"Profile {username} does not exist: {e}")
            continue
        except Exception as e:
            print(f"Unknown error: {e}")
            continue
        now = datetime.now()
        one_day_ago = now - timedelta(days=1) 
        for post in takewhile(lambda p: p.date > one_day_ago, dropwhile(lambda p: p.date > now, posts)): # Get the posts from the last day
            try:
                L.download_post(post, username)
                print("Post downloaded.")
                captions.append(post.caption)
            except Exception as e:
                print(f"Error while downloading post: {e}")
    captions = [caption.replace('\n', '') for caption in captions] # The gpt formatter does not like newlines
    try:
        purge_profiles_dir(session_file_path) #The way instaloader works, it downloads the posts to the profiles directory, so we need to delete them after we are done
        print("Profiles folder emptied")
    except Exception as e:
        print(f"Unknown error while emptying profiles folder: {e}")
    return captions

if __name__ == "__main__":
    import pathlib
    profiles = ["aether_ry", "lahoevents", "koeputkiappro", "aleksinappro", "lasolary", "lymo.ry", "lirory", "Moveolahti", "koe_opku", "linkkiry"]
    session_file_path = str(pathlib.Path(__file__).parent.resolve()) # Get the path of the script
    session_file_name = "\\session-bencebansaghi" # Name of the session file
    captions = return_captions(profiles,session_file_path,session_file_name)
    for caption in captions:
        print(caption)

