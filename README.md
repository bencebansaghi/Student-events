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
