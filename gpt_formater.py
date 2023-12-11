import pathlib
from openai import OpenAI
from get_insta_posts import return_captions
import api_key

def return_formated_events(profiles):
    api_key = api_key.get_api_key() # Get the API key from api_key.py
    # Initialize the OpenAI client with the API key
    client = OpenAI(api_key=api_key)

    # List of Instagram profiles to process

    # Fetch captions from the specified Instagram profiles
    session_file_path = str(pathlib.Path(__file__).parent.resolve()) # Get the path of the script
    session_file_name = "\\session-bencebansaghi" # Name of the session file
    session_file = session_file_path + session_file_name # Full path of the session file
    captions = return_captions(profiles,session_file)

    # Create a stream to process the captions using the OpenAI API
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user", 
            "content": f"You will receive Instagram captions as one block of text. They might be in English or Finnish, but translate everything to English. Your job is to check for any possible events and return their data in the following format: [{{date of the event in the format %d.%m.%Y}},{{name of the event}},{{short description of the event (maximum 6 sentences)}}]. Here are the captions as a block: {str(captions)} Remember to make sure you translate all events to English, both their names and descriptions. Also make sure to stick to the format to the closest detail. If no concrete date is given for an event, ignore it."
        }],
        stream=True,
    )

    # Process and append the output from the stream to an array
    output_array = []
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            output_array.append(chunk.choices[0].delta.content)

    return output_array

    
                
                
if __name__ == "__main__":
    profiles = ["aether_ry", "lahoevents", "koeputkiappro", "aleksinappro", "lasolary", "lymo.ry", "lirory", "Moveolahti", "koe_opku", "linkkiry"]
    result = return_formated_events(profiles)
    print(result)

