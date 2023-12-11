# Student-events
A telegram chatbot which displays the information about student events in Lahti at LUT University.

## Table of contents


# get_insta_posts.py

This Python script is used to fetch Instagram posts from a list of profiles. It uses the `instaloader` library to interact with Instagram's API.

## How it works

The script iterates over a list of Instagram usernames, fetching the posts from each profile. It handles exceptions for cases where a profile does not exist or any other unknown error occurs.

The script fetches posts from the last two weeks. It downloads each post and appends the caption to a list. After each profile, the script pauses for half a second to avoid hitting Instagram's rate limits.

The list of captions is returned at the end of the script.

## Usage

To use this script, you need to have a list of Instagram usernames. This list is defined in the `profiles` variable at the bottom of the script.

The script also uses a session file, the path of which is defined by the `session_file_path` and `session_file_name` variables.

To run the script, simply execute it in a Python environment where the `instaloader` library is installed.

## Dependencies

This script depends on the following Python libraries:

- `instaloader`
- `datetime`
- `time`
- `pathlib`

Please ensure these are installed in your Python environment before running the script.

# gpt_formater.py

This Python script uses the OpenAI API to process Instagram captions fetched from a list of profiles. It uses the `openai` library to interact with the OpenAI API.

## How it works

The script takes a list of Instagram profiles as input and fetches their captions using the `return_captions` function from the `get_insta_posts` module. 

It then sends these captions to the OpenAI API, which processes them and returns any possible events in the captions in a specific format. The OpenAI model used is `gpt-3.5-turbo`.

The script also handles the translation of captions from Finnish to English.

## Usage

To use this script, you need to have a list of Instagram usernames. This list should be passed as an argument to the `return_formated_events` function.

The script also uses a session file, the path of which is defined by the `session_file_path` and `session_file_name` variables.

To run the script, simply execute it in a Python environment where the `openai` and `pathlib` libraries are installed.

## Dependencies

This script depends on the following Python libraries:

- `openai`
- `pathlib`
- `get_insta_posts`
- `api_key`

Please ensure these are installed in your Python environment before running the script.
