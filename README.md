# Telegram chatbot from instagram pages
A telegram chatbot which displays the information about events found on instagram pages using Instaloader and OpenAI.

## Table of Contents
- Getting Started
  - Prerequisites
  - Installation
- Usage
- Files
  - get_insta_posts.py
  - gpt_formatter.py
  - chatbot.py
  - admin_commands.py
- Acknowledgments

## Getting started 

These instructions will get you a copy of the project up and running on your local machine for development and execution purposes.

### Prerequisites

Before you begin, ensure you have met the following requirements:
- You have installed the latest version of python and pip

### Installation

1. Clone the repository:
git clone https://github.com/bencebansaghi/Student-events
2. Navigate to the project directory:
cd Student-events
3. Install the required packages:
pip install -r requirements.txt


## Usage

To use the chatbot, follow these steps:

1. Set up your `.env` file in project directory. Required parameters: 
- BOT_TOKEN - Instructions for getting the token can be found at https://core.telegram.org/bots/tutorial
- OPENAI_API_KEY - Requires OpenAI API access
- INSTA_USERNAME
- INSTA_PASSWORD
- INSTAGRAM_PAGES - list of instagram handles seperated by commas without space
- CSV_FILE_PATH
- ADMIN_PASSWORD - used for `admin_commands.py`
- PROFILES_DIR_PATH - select profiles directory manually, if not selected it will be saved in cwd
2. Run the bot:
>python chatbot.py

## Files

You can find the descriptions of the files used in this project. All files use asynchronous functions where longer execution times are expected as not to disturb the main bot functionalities during updating the events.

### get_insta_posts.py

This script is used to fetch Instagram posts from specified profiles using the `instaloader` library. It includes the following functions:

- `return_instaloader_session_with_login(session_file_path, session_file_name)`: This function creates an `Instaloader` session with login. It first tries to log in using a session file, and if that fails, it tries to log in using environment variables.

- `purge_profiles_dir(session_file_path)`: This function deletes and recreates the directory where profile data is stored.

- `get_post_info_from_last_xdays(L: Instaloader, username, days_amount=1, start_from_day=0)`: This function fetches posts from the last `x` days from a given Instagram profile.

- `get_captions_and_links_dicts(profile_names_array, session_file_path, session_file_name)`: This function fetches post captions and links from a list of Instagram profiles. This is also the endpoint of the file.

### gpt_formater.py

This script uses the OpenAI GPT-3 model to process Instagram post captions and return information about any events mentioned in the captions. It includes the following functions:

- `make_OpenAI_client(api_key_value)`: This function creates an `AsyncOpenAI` client using the provided API key.

- `create_stream_for_post(client:AsyncOpenAI,post)`: This function creates a stream of completions from the GPT-3 model for a given Instagram post. The model is asked to identify any events in the post caption and return their information.

- `return_formated_events(profiles,session_file_path,session_file_name)`: This function fetches post captions and links from a list of Instagram profiles, creates a stream of completions for each post, and returns a list of dictionaries with the formatted event information.

### chatbot.py

This is the main file that runs the chatbot. It uses the Telegram API to interact with users and provide them with information about events. The bot can show all events, events in the next week, and it also allows users to add events to their calendar.

The file contains several functions:

- `start`: This function is triggered when a user starts a conversation with the bot. It sends a greeting message and provides a keyboard with options to the user.
- `info_command`: This function sends a message with information about the bot and its maintainers.
- `event_command`: This function is triggered when a user requests to see events. It fetches the events from a CSV file, sorts them by date, and sends them to the user.
- `button_click`: This function handles the "add to calendar" button. It creates an iCalendar file for the event and sends it to the user.
- `get_dicts_from_file`: This function reads the events from a CSV file and returns them as a list of dictionaries.
- `file_and_header_exists`: This function checks if the CSV file exists and if it has a header.
- `escape_markdown`: This function escapes special characters in a text for markdown formatting.
- `write_new_events_to_file`: This function writes new events to the CSV file.
- `fetch_new_events_to_dicts`: This function fetches new events from Instagram pages and returns them as a list of dictionaries.
- `add_new_events`: This function fetches new events and writes them to the CSV file.
- `remove_old_events`: This function removes old events from the CSV file.
- `main`: This is the main function that runs the bot. It sets up the bot, adds handlers for different commands and messages, and starts the bot.

The bot uses environment variables for the bot token, Instagram pages to fetch events from, and the path to the CSV file. It logs all its activities to a log file.

### admin_commands.py

This script provides an interface for admins to manage events. It reads and writes events from/to a CSV file. The file path is specified in an environment variable. The script includes the following functions:

- `read_events()`: This function reads the events from the CSV file and returns them as a list of dictionaries.
- `write_events(events)`: This function writes a list of events to the CSV file.
- `modify_event(events, event_id)`: This function modifies an event in the list of events. It asks the admin what they want to modify and updates the event accordingly.
- `add_event(events)`: This function adds a new event to the list of events. It asks the admin for the event details.
- `remove_event(events, remove_id)`: This function removes an event from the list of events based on its ID.
- `run_menu()`: This function runs the main menu for the admin interface. It allows the admin to remove, modify, or add events, and to save their changes.
- `save_changes(events)`: This function asks the admin if they want to save their changes and writes the events to the CSV file if they do.

The script also includes a main section that asks for the admin password and runs the main menu if the password is correct. The admin password is specified in an environment variable.

## Acknowledgments

This project started as a university course project work, but after it had very basic functionalities and no backend aside from the bot, it was developed solely by me. The people working on the original project were LUT University students:

 - Pouya Amiri
 - Salman Babar
 - Mengshi Qi
 - Vera Stojcheva
 - Suthinee Segkhoonthod
 - Thet Htar Zin