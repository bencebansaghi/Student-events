from instaloader.instaloader import Instaloader
from instaloader.structures import Profile
from datetime import datetime, timedelta
from itertools import dropwhile, takewhile
import instaloader.exceptions
import time
from dotenv import load_dotenv
import os




def return_captions(profiles_array, session_file_path): # Returns the captions of the posts from the last week of the given profiles as an array
    with Instaloader(quiet=True,dirname_pattern=".\\profiles") as L:
        try: #first we try to login with .env variables
            load_dotenv()
            L.login(str(os.getenv("INSTA_USERNAME")), str(os.getenv("INSTA_PASSWORD"))) #casting to string is necessary because of the way dotenv works
            print("Logged in with .env variables")
        except Exception as e:
            try:  #if that fails, we try to load the session from a file
                L.load_session_from_file("bencebansaghi", filename=session_file_path) # You can get the session file by following the steps at https://instaloader.github.io/troubleshooting.html
                print("Logged in with session file")
            except instaloader.exceptions.ConnectionException as e:
                print(f"Login error: {e}")
            except FileNotFoundError as e:
                print(f"File not found error: {e}\nPlease make sure the session is saved to the same dir as the script.")
            except Exception as e:
                print(f"Both login methods failed, unknown error: {e}")

    captions = []
    for username in profiles_array:
        try:
            posts = Profile.from_username(L.context, username).get_posts() 
        except instaloader.exceptions.ProfileNotExistsException as e:
            print(f"Profile {username} does not exist: {e}")
            continue
        except Exception as e:
            print(f"Unknown error: {e}")
            continue
        now = datetime.now()
        one_week_ago = now - timedelta(weeks=1) 
        for post in takewhile(lambda p: p.date > one_week_ago, dropwhile(lambda p: p.date > now, posts)): # Get the posts from the last week
            L.download_post(post, username)
            captions.append(post.caption)
        time.sleep(0.5) # To avoid spamming the server
    captions = [caption.replace('\n', '') for caption in captions]
    return captions

if __name__ == "__main__": #example usage
    import pathlib
    profiles = ["aether_ry", "lahoevents", "koeputkiappro", "aleksinappro", "lasolary", "lymo.ry", "lirory", "Moveolahti", "koe_opku", "linkkiry"]
    session_file_path = str(pathlib.Path(__file__).parent.resolve()) # Get the path of the script
    session_file_name = "\\session-bencebansaghi" # Name of the session file
    session_file = session_file_path + session_file_name # Full path of the session file
    captions = return_captions(profiles,session_file)
    for caption in captions:
        print(caption)

