# Student-events
A telegram chatbot which displays the information about student events in Lahti at LUT University.

## get_insta_posts.py

This script uses the `instaloader` library to fetch Instagram posts from specified profiles. It logs in to Instagram using either environment variables or a session file, then fetches the captions of posts from the last week of the given profiles.

### Functionality

The main function, `return_captions(profiles_array, session_file_path)`, takes an array of Instagram profile names and a path to a session file. It returns an array of captions from the posts of the last week from the given profiles.

The script first tries to log in using the Instagram username and password stored in environment variables. If this fails, it tries to load a session from a file. If both methods fail, it prints an error message.

### Usage

1. Install the required Python libraries with `pip install -r requirements.txt`.
2. Set your Instagram username and password as environment variables `INSTA_USERNAME` and `INSTA_PASSWORD`, or create a session file as described in the [instaloader troubleshooting guide](https://instaloader.github.io/troubleshooting.html).
3. Run the script with `python get_insta_posts.py`.

### Environment Variables

- `INSTA_USERNAME`: Your Instagram username.
- `INSTA_PASSWORD`: Your Instagram password.

### Session File

If you prefer not to use environment variables, you can create a session file as described in the [instaloader troubleshooting guide](https://instaloader.github.io/troubleshooting.html). The script will attempt to use this if the environment variables are not set.

### Dependencies

- `instaloader`: Used to fetch Instagram posts.
- `datetime`: Used to calculate the date one week ago.
- `itertools`: Used to iterate over the posts until one week ago.
- `time`: Used to delay between requests to Instagram.
- `dotenv`: Used to load environment variables from a .env file.
- `os`: Used to access environment variables.

Please ensure these are installed in your Python environment before running the script.

## gpt_formater.py

This script uses the OpenAI API to process captions fetched from Instagram posts. It sends the captions to the OpenAI API, which checks for any possible events and returns their data in a specific format.

### Functionality

The script fetches captions from specified Instagram profiles using the `return_captions` function. It then creates a stream to process the captions using the OpenAI API. The API is instructed to return event data in the following format: `{date of the event in the format %d.%m.%Y},{name of the event},{short description of the event (maximum 6 sentences)}`.

The script processes the output from the stream and appends it to an array.

### Usage

1. Install the required Python libraries with `pip install -r requirements.txt`.
2. Set your OpenAI API key as an environment variable `OPENAI_API_KEY` or create an api_key.py file, which returns your api key.
3. Run the script with `python gpt_formater.py`.

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key.

### Dependencies

- `openai`: Used to interact with the OpenAI API.
- `os`: Used to access environment variables.
- `dotenv`: Used to load environment variables from a .env file.

Please ensure these are installed in your Python environment before running the script.


## Chatbot.py

This Python script is a part of a Telegram bot application. It uses the `telegram` library to interact with the Telegram API and the `ics` library to handle calendar events.

### Dependencies

- `datetime`: For handling date and time related tasks.
- `json`: For parsing and manipulating JSON data.
- `logging`: For logging events for debugging and analysis.
- `schedule`: For scheduling tasks.
- `io` and `pathlib`: For handling file and path operations.
- `telegram`: For interacting with the Telegram API.
- `gpt_formater`: A custom module for formatting text.
- `ics`: For handling calendar events.

### Logging

The script sets up basic logging with a specific format and logging level. It also sets a higher logging level for `httpx` to avoid logging all GET and POST requests.

### Command Handlers

The script defines command handlers for the `/start` and `/help` commands.

- The `/start` command sends a message to the user and presents them with a custom keyboard with two options: "All Events" and "Events in the next week".
- The `/help` command sends a message to the user with the text "Help!".

### How to Use

To use this script, you need to have a Telegram bot token. You can get this token by creating a new bot on Telegram. Once you have the token, you can run the script and interact with the bot on Telegram.
