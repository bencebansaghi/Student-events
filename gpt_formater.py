from datetime import datetime
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from get_insta_posts import return_captions
import api_key

def return_formated_events(profiles,session_file_path,session_file_name):
    api_key_value=None
    try: #first we try to get API key from .env variables
        load_dotenv()
        api_key_value = str(os.getenv("API_KEY")) #casting to string is necessary because of the way dotenv works
        if api_key_value is None:
            raise Exception("API key not found in .env variables")
        print("Got API key from .env variables")
    except Exception as e:
        api_key_value = api_key.get_api_key() # Get the API key from api_key.py
        print("Got API key from api_key.py")
    if api_key_value is None: #double check if API key is found
        print("API key could not be found. Please make sure you have an .env file with the OPENAI_API_KEY variable or a file called api_key.py with a get_api_key() function that returns the API key. Terminating.")
        return None
    
    try:
        client = OpenAI(api_key=api_key_value)
    except Exception as e:
        print(f"Error while creating OpenAI client: {e}")
        return None
    
    # Fetch captions from the specified Instagram profiles
    try:
        captions = return_captions(profiles,session_file_path,session_file_name)
    except Exception as e:
        print(f"Error while fetching captions: {e}")
        return None
    if captions is None or len(captions) == 0:
        print("No captions found")
        return None
    

    
    # Create a stream to process the captions using the OpenAI API
    gptd_post_array = []
    for post in captions:
        try:
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user", 
                    "content": f'data: {post["caption"]}. Your task is to identify any events in the data and return their information. The event must have a specific or easily recognizable name, date, and description. If the data does not have an event or a date, return None. Otherwise, return a dictionary with these keys and values: {{"date" : the event date in %d.%m.%Y format, "name" : the name of the event in English (up to 35 characters), "description" : a short summary of the event in English (up to four sentences)}}. Do not include anything else in the response. Translate the event name and description to English if they are in another language. If the data only has the month and day of the event, use {datetime.now().year} for the year. If the event lasts for more than one day, use the first day as the date and indicate that duration in the description.'
                }],
                stream=True,
            )
            
            # Process and append the output from the stream to an array
            output_array = []
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    output_array.append(chunk.choices[0].delta.content)
        except Exception as e:
            print(f"Error while creating stream: {e}")
            return None
        combined_output = ''.join(output_array)
        if "date" not in combined_output or "name" not in combined_output or "description" not in combined_output or "None" in combined_output:
            continue
        try:
            combined_output_dict=json.loads(combined_output)
        except Exception as e:
            continue
        combined_output_dict["link"]=post["link"]
        gptd_post_array.append(combined_output_dict)


    return gptd_post_array
    

    
if __name__ == "__main__":
    import pathlib
    profiles = ["aether_ry", "lahoevents", "koeputkiappro", "aleksinappro", "lasolary", "lymo.ry", "lirory", "Moveolahti", "koe_opku", "linkkiry"]
    session_file_path = str(pathlib.Path(__file__).parent.resolve()) # Get the path of the script
    session_file_name = "\\session-bencebansaghi" # Name of the session file
    result = return_formated_events(profiles,session_file_path,session_file_name)
    print(result)

