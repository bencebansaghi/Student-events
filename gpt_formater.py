import json
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from get_insta_posts import get_captions_and_links_dicts

def make_OpenAI_client(api_key_value):
    if api_key_value is None:
        raise Exception("API key not found in environment variables.")
    try:
        client = AsyncOpenAI(api_key=api_key_value)
    except Exception as e:
        raise Exception(f"Error while creating OpenAI client: {e}")
    return client

async def create_stream_for_post(client:AsyncOpenAI,post):
    try:
        current_year=datetime.now().year
        stream = await client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user", 
                "content": f'data: {post["caption"]}. Your task is to identify any events in the data and return their information. The event must have a specific or easily recognizable name, date, and description. If the data does not have an event or a date, return None. Otherwise, return a dictionary with these keys and values: {{"date" : the event date in strictly %d.%m.%Y format, "name" : the name of the event in English (up to 35 characters), "description" : a short summary of the event in English (up to four sentences)}}. Do not include anything else in the response. Translate the event name and description to English if they are in another language. If the data only has the month and day of the event, use {current_year} for the year. If the event lasts for more than one day, use the first day as the date and indicate that duration in the description.'
            }],
            stream=True,
        )
        # Process and append the output from the stream to an array
        output_array = []
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                output_array.append(chunk.choices[0].delta.content)
        if output_array is []:
            return None
        return output_array
    except Exception as e:
        logging.error(f"Error while creating stream for post {post['link']}: {e}")
        return None

async def return_formated_events(profiles,session_file_path,session_file_name):
    load_dotenv()
    api_key_value = os.getenv("OPENAI_API_KEY")
    client = make_OpenAI_client(api_key_value)
    logging.info("OpenAI client successfully created.")
    
    captions_links_dicts = await get_captions_and_links_dicts(profiles,session_file_path,session_file_name)
    if not captions_links_dicts:
        logging.info("No captions found.")
        return None

    final_posts_array = []
    for post in captions_links_dicts:
        stream = await create_stream_for_post(client,post)
        if stream is None:
            continue
        combined_stream_output = ''.join(stream)
        if "date" not in combined_stream_output or "name" not in combined_stream_output or "description" not in combined_stream_output or "None" in combined_stream_output:
            continue
        try:
            combined_output_dict=json.loads(combined_stream_output)
        except Exception as e:
            logging.error(f"Error while converting OpenAI output to dict: {e}")
            continue
        combined_output_dict["link"]=post["link"]
        final_posts_array.append(combined_output_dict)
    if not final_posts_array:
        return None
    return final_posts_array
    
if __name__ == "__main__":
    import pathlib
    import asyncio
    profiles = ["aether_ry", "lahoevents", "koeputkiappro", "aleksinappro", "lasolary", "lymo.ry", "lirory", "Moveolahti", "koe_opku", "linkkiry", "lut_es"]
    session_file_path = str(pathlib.Path(__file__).parent.resolve()) # Get the path of the script
    session_file_name = "session-lut_student_events" # Name of the session file
    #session_file_name = "session-bencebansaghi" # Name of the session file
    loop = asyncio.get_event_loop()
    captions_and_links = loop.run_until_complete(return_formated_events(profiles, session_file_path, session_file_name))
    print(captions_and_links)

