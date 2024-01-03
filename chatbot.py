from calendar import c
from datetime import datetime
from itertools import count
import json
import logging
import threading
import schedule
import time
import pathlib


from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, Updater

import gpt_formater

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

# This is the function that prints the events
async def event_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #Send a message when the command /events is issued.
    with open("active_events.csv", "r") as f:
        lines = f.readlines()
        await update.message.reply_text("Here are the events:")
        for line in lines:
            await update.message.reply_text(line)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

def fetch_weekly_events():
    print("Fetching weekly events")
    profiles = ["aether_ry", "lahoevents", "koeputkiappro", "aleksinappro", "lasolary", "lymo.ry", "lirory", "Moveolahti", "koe_opku", "linkkiry"]
    session_file_path = str(pathlib.Path(__file__).parent.resolve()) # Get the path of the script
    session_file_name = "\\session-bencebansaghi" # Name of the session file
    session_file = session_file_path + session_file_name # Full path of the session file
    result_string = str(gpt_formater.return_formated_events(profiles,session_file))
    #add the events to "active_events.csv"
    result_list_dict=json.loads(result_string)
    count = 0
    for item in result_list_dict:
        with open("active_events.csv", "a") as f:
            #if date is in format %d.%m.%Y, append it to the file
            try:
                # Convert the string date to a datetime object
                datetime.strptime(item["date"], "%d.%m.%Y")
                f.write(f"{item['date']},{item['name']},{item['description']}\n")
                count+=1
            except ValueError:
                pass
    print(count, "new events added to the csv file.")
                
# funtion that removes the events from "active_events.csv" when their date has passed
def remove_old_events():
    print("Removing old events")
    with open("active_events.csv", "r") as f:
        lines = f.readlines()
    with open("active_events.csv", "w") as f:
        for line in lines:
            if line.split(",")[0] > datetime.now().strftime("%d.%m.%Y"):
                f.write(line)

def main():
    application = Application.builder().token("6824458794:AAFg_y1TNYDbb6ff2dgJfeFPT4UL_f6vdb0").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("events", event_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    schedule.every().week.do(fetch_weekly_events)
    schedule.every().day.do(remove_old_events)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

