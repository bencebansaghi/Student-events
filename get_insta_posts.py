import logging
from instaloader.instaloader import Instaloader
from instaloader.structures import Profile
from datetime import datetime, timedelta
from itertools import dropwhile, takewhile
import instaloader.exceptions
from dotenv import load_dotenv
import os
import shutil

load_dotenv()
PROFILES_FILE_PATH = os.getenv("PROFILES_FILE_PATH")
if not PROFILES_FILE_PATH:
    logging.warning("PROFILES_FILE_PATH not found in environment variables.")
PROFILES_FILE_PATH = os.path.join(os.getcwd(), "profiles")


def return_instaloader_session_with_login(session_file_path, session_file_name):
    L = Instaloader(
        quiet=True,
        dirname_pattern=PROFILES_FILE_PATH,
        download_pictures=False,
        download_videos=False,
    )
    try:  # session file should be the primary login method, because it is more reliable and does not raise instagram red flags
        # You can get the session file by following the steps at https://instaloader.github.io/troubleshooting.html
        L.load_session_from_file(
            "-".join(session_file_name.split("-")[1:]),
            filename=os.path.join(session_file_path, session_file_name),
        )
        if not L.test_login():
            raise Exception(f"Invalid or expired session file.")
        logging.info("Logged in to instaloader with session file.")
        return L
    except FileNotFoundError as e:
        # Make sure the session is saved to the same dir as the script and has the following naming convention: 'session-*profilename*'.
        logging.warning(f"Session file not found: {e}.")
    except Exception as e:
        logging.warning(f"Session file login failed, {e}")
    load_dotenv()
    username = os.getenv("INSTA_USERNAME")
    password = os.getenv("INSTA_PASSWORD")
    if not username or not password:
        raise Exception("Username or password not found in environment variables.")
    try:  # if that fails, we try to login with .env variables
        L.login(username, password)
        logging.info("Logged in to instaloader with environment variables.")
        try:
            L.save_session_to_file(session_file_path)
        except Exception as e:
            logging.error(f"Failed to save session file: {e}")
        return L
    except instaloader.exceptions.ConnectionException as e:
        raise instaloader.exceptions.ConnectionException(f"Login error: {e}")
    except Exception as e:
        raise Exception(f"Environment variable login failed: {e}")


def purge_profiles_dir(session_file_path):
    profiles_dir = PROFILES_FILE_PATH
    if os.path.exists(profiles_dir):
        shutil.rmtree(profiles_dir)
    os.makedirs(profiles_dir)


async def get_post_info_from_last_xdays(
    L: Instaloader, username, days_amount=1, start_from_day=0
):
    try:
        posts = Profile.from_username(L.context, username).get_posts()
    except instaloader.exceptions.ProfileNotExistsException as e:
        logging.warning(f"Profile {username} does not exist: {e}")
        return None
    except Exception as e:
        logging.warning(f"Unknown error with profile {username}: {e}")
        return None
    from_date = datetime.now() - timedelta(days=start_from_day)
    to_date = from_date - timedelta(days=days_amount)
    posts_array = []
    for post in takewhile(
        lambda p: p.date > to_date, dropwhile(lambda p: p.date > from_date, posts)
    ):
        try:
            L.download_post(post, username)
            posts_array.append(
                {
                    "link": "https://www.instagram.com/p/" + post.shortcode,
                    "caption": str(post.caption).replace("\n", ""),
                }
            )
        except Exception as e:
            logging.error(f"Error while downloading post: {e}")
    return posts_array


async def get_captions_and_links_dicts(
    profile_names_array, session_file_path, session_file_name
):
    try:
        L = Instaloader(
            quiet=True,
            dirname_pattern=PROFILES_FILE_PATH,
            download_pictures=False,
            download_videos=False,
        )
    except Exception as e:
        logging.warning(f"Could not get instaloader session without logging in: {e}")
        try:
            L = return_instaloader_session_with_login(
                session_file_path, session_file_name
            )
        except Exception as e:
            logging.error(f"Error while creating instaloader session: {e}")
            return None

    posts_array = []
    for username in profile_names_array:
        temp_array = await get_post_info_from_last_xdays(L, username)
        if temp_array is None or len(temp_array) == 0:
            continue
        for dict in temp_array:
            posts_array.append(dict)
    try:
        purge_profiles_dir(
            session_file_path
        )  # The way instaloader works, it downloads the posts to the profiles directory, so we need to delete them after we are done
    except Exception as e:
        logging.warning(f"Unknown error while emptying profiles folder: {e}")
    return posts_array


if __name__ == "__main__":
    import pathlib
    import asyncio

    profiles = [
        "aether_ry",
        "lahoevents",
        "koeputkiappro",
        "aleksinappro",
        "lasolary",
        "lymo.ry",
        "lirory",
        "Moveolahti",
        "koe_opku",
        "linkkiry",
    ]
    session_file_path = str(
        pathlib.Path(__file__).parent.resolve()
    )  # Get the path of the script
    session_file_name = "session-lut_student_events"  # Name of the session file
    # session_file_name = "session-bencebansaghi" # Name of the session file
    loop = asyncio.get_event_loop()
    captions_and_links = loop.run_until_complete(
        get_captions_and_links_dicts(profiles, session_file_path, session_file_name)
    )
    print(captions_and_links)
