from instaloader import Instaloader, Profile
from datetime import datetime, timedelta

def return_captions(profiles):
    L = Instaloader()
    captions = []
    for username in profiles:
        profile = Profile.from_username(L.context, username)
        posts = sorted(profile.get_posts(), key=lambda post: post.likes, reverse=True)
        
        now = datetime.now()
        one_week_ago = now - timedelta(weeks=1)

        selected_range = [post for post in posts if one_week_ago <= post.date <= now]
        for post in selected_range:
            L.download_post(post, username)
            captions.append(post.caption)

    return captions
        
if __name__ == "__main__":
    print(return_captions(["lahoevents","aether_ry"]))
