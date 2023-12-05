from instaloader import Instaloader, Profile
from datetime import datetime, timedelta
from itertools import dropwhile, takewhile

def return_captions(profiles):
    L = Instaloader(quiet=True)
    captions = []
    for username in profiles:
        posts = Profile.from_username(L.context, username).get_posts() 
        now = datetime.now()
        one_week_ago = now - timedelta(weeks=1)
        for post in takewhile(lambda p: p.date > one_week_ago, dropwhile(lambda p: p.date > now, posts)):
            L.download_post(post, username)
            captions.append(post.caption)

    return captions
        
if __name__ == "__main__":
    profiles = ["aether_ry", "lahoevents", "koeputkiappro", "aleksinappro", "lasolary", "lymo.ry", "lirory", "Moveolahti", "koe_opku", "linkkiry"]
    captions = return_captions(profiles)
    for caption in captions:
        print(caption)

