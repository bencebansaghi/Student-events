from calendar import c
from datetime import datetime, timedelta
from itertools import count
import json
import logging
import threading
import schedule
import time
import io
import pathlib
from telegram import ForceReply, InputFile, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, Updater, CallbackQueryHandler, CallbackContext
import gpt_formater
from instaloader.structures import Post
from ics import Calendar, Event

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
    # Create a custom keyboard with two buttons
    keyboard = [
        [{"text": "All Events"}],
        [{"text": "Events in the next week"}],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    # Starting message
    await update.message.reply_html(
        f"Hi, {user.mention_html()}!"
        "\nChoose an option from the keyboard below to get started.\n\n"
        "Available options:\n"
        "📅 Show all events\n"
        "📆 Show events in the next week",
        reply_markup=reply_markup,
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

# This is the function that prints the events
async def event_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a formatted message with an 'Add to Calendar' button."""
    # This part handles the "All Events" button
    if update.message.text.lower() == "all events":
        with open("active_events.csv", "r") as f:
            lines = f.readlines()
            if not lines:
                await update.message.reply_text("No events found.")
            else:
                # Create a list to store all events
                all_events = []
                today = datetime.now()

                for line in lines:
                    # Split only the first two commas to avoid splitting the description
                    event_data = line.strip().split(",", 2)
                    if len(event_data) >= 3:
                        date_str, name, description = event_data[0], event_data[1], event_data[2]
                        try:
                            event_date = datetime.strptime(date_str, "%d.%m.%Y")
                            all_events.append((date_str, name, description))
                        except ValueError:
                            pass

                # Sort all events based on date
                all_events.sort(key=lambda x: datetime.strptime(x[0], "%d.%m.%Y"))

                # Send the formatted messages for all events
                for event in all_events:
                    date, name, description = event
                    formatted_message = (
                        f"*Name of the event:* {name}\n"
                        f"*Date:* {date}\n\n"
                        f"*Description:* {description}\n\n"
                    )

                    # Create an InlineKeyboardMarkup with 'Add to Calendar' button
                    keyboard = [[InlineKeyboardButton("Add to Calendar", callback_data=f"add_to_calendar:{date}:{name}")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    # Send the formatted message with the 'Add to Calendar' button
                    await update.message.reply_markdown(formatted_message, reply_markup=reply_markup)

    # And this part handles the "Events in the next week" button
    elif "events in the next week" in update.message.text.lower():
        with open("active_events.csv", "r") as f:
            lines = f.readlines()
            if not lines:
                await update.message.reply_text("No events found.")
            else:
                # Create a list to store events within the next week
                next_week_events = []
                today = datetime.now()

                for line in lines:
                    event_data = line.strip().split(",", 2)
                    if len(event_data) >= 3:
                        date_str, name, description = event_data[0], event_data[1], event_data[2]
                        try:
                            event_date = datetime.strptime(date_str, "%d.%m.%Y")
                            # Check if the event is within the next week
                            if today <= event_date <= today + timedelta(days=7):
                                next_week_events.append((date_str, name, description))
                        except ValueError:
                            pass

                # Sort next week events based on date
                next_week_events.sort(key=lambda x: datetime.strptime(x[0], "%d.%m.%Y"))

                # Send the formatted messages for events within the next week
                for event in next_week_events:
                    date, name, description = event
                    formatted_message = (
                        f"*Name of the event:* {name}\n"
                        f"*Date:* {date}\n\n"
                        f"*Description:* {description}\n\n"
                    )

                    # Create an InlineKeyboardMarkup with 'Add to Calendar' button
                    keyboard = [[InlineKeyboardButton("Add to Calendar", callback_data=f"add_to_calendar:{date}:{name}")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    # Send the formatted message with the 'Add to Calendar' button
                    await update.message.reply_markdown(formatted_message, reply_markup=reply_markup)

# This function handle the "add to calendar" button
# It will create an iCalendar file and send it to the user
async def button_click(update: Update, context: CallbackContext) -> None:
    """Handle button clicks, including 'Add to Calendar' button."""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data.split(':')

    if data[0] == "add_to_calendar":
        date_str = data[1]
        event_name = data[2]

        # Convert the date string to a datetime object with midnight time
        event_date = datetime.strptime(date_str, "%d.%m.%Y").replace(hour=0, minute=0, second=0)

        # Generate iCalendar file
        cal = Calendar()
        event = Event()
        event.name = event_name
        event.begin = event_date
        event.make_all_day()  # Set the event to last the whole day
        cal.events.add(event)

        # Convert the calendar to bytes
        cal_str = cal.serialize()
        cal_bytes = cal_str.encode('utf-8')

        # Send the iCalendar file as a document using InputFile
        cal_file_input = InputFile(io.BytesIO(cal_bytes), filename=f"{event_name}.ics")
        await context.bot.send_document(chat_id=user_id, document=cal_file_input)

        await query.answer("Event added to calendar!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

# function that fetches the new events from the instagram accounts and adds them to "active_events.csv"
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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, event_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CallbackQueryHandler(button_click))
    schedule.every().week.do(fetch_weekly_events)
    schedule.every().day.do(remove_old_events)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
