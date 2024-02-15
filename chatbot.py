from datetime import datetime, timedelta
import logging
from matplotlib.pylab import f
import schedule
import io
import pathlib
from telegram import InputFile, Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, CallbackContext
import gpt_formater
from ics import Calendar, Event
import pickle

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
        "📆 Show events in the next week\n\n"
        "For more information, type /info.",
        reply_markup=reply_markup,
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /info is issued."""
    await update.message.reply_html("This bot is hosted by LTKY(?) and was developed by Bence Bánsághi.\n"
                                    "For any issues, ideas or questions about the bot, please contact <a href='https://www.ltky/'>LTKY</a>.\n"
                                    "The code of the bot is available on <a href='https://github.com/bencebansaghi/Student-events'>GitHub</a>. "
                                    "For any inquiries about the code, feel free to contact me.\n")

async def event_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if "event" in update.message.text.lower(): #general case for all events printing
        with open("active_events_pickle", "rb") as f:
            all_events = []
            try:
                all_events = pickle.load(f)
            except Exception as e:
                print(f"Error while loading events: {e}")
            # Sort all events based on date
            all_events.sort(key=lambda x: x["date"])
            
            if "events in the next week" in update.message.text.lower(): # If the user wants to see events in the next week
                next_week_events = []
                today = datetime.now().date()
                for event in all_events:
                    if today <= event["date"] <= today + timedelta(days=8):
                        next_week_events.append(event)
                all_events = next_week_events
                
            if not all_events or all_events == []:
                await update.message.reply_text("No events found.")
                return
            for event in all_events:
                formatted_message = (
                    f"*Name of the event:* {event["name"]}\n"
                    f"*Date:* {event["date"].strftime('%Y %B %d')}\n\n"
                    f"*Description:* {event["description"]}\n"
                )

                callback_data=f"add_to_calendar:{event["date"]}:{event["name"]}"
                callback_data = callback_data[:64] # The maximum length of callback_data is 64 characters, just to make sure it doesn't exceed that
                
                keyboard = [[InlineKeyboardButton("Add to Calendar", callback_data=callback_data),
                            InlineKeyboardButton("Open Instagram Post", url=event["link"])]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_markdown(formatted_message, reply_markup=reply_markup)

# This function handle the "add to calendar" button
# It will create an iCalendar file and send it to the user
async def button_click(update: Update, context: CallbackContext) -> None:
    """Handle button clicks, including 'Add to Calendar' button."""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data.split(':')

    if data[0] == "calendar":
        date_str = data[1]
        event_name = data[2]

        # Convert the date string to a datetime object with midnight time
        event_date = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=0, minute=0, second=0)

        # Generate iCalendar file
        cal = Calendar()
        event = Event()
        event.name = event_name
        event.begin = event_date
        event.make_all_day()
        cal.events.add(event)

        # Convert the calendar to bytes
        cal_str = cal.serialize()
        cal_bytes = cal_str.encode('utf-8')

        # Send the iCalendar file as a document using InputFile
        cal_file_input = InputFile(io.BytesIO(cal_bytes), filename=f"{event_name}.ics")
        await context.bot.send_document(chat_id=user_id, document=cal_file_input)



async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

# function that fetches the new events from the instagram accounts and adds them to "active_events_pickle"
def fetch_daily_events():
    print("Fetching daily events")
    profiles = ["aether_ry", "lahoevents", "aleksinappro", "lasolary", "lymo.ry", "lirory", "Moveolahti", "koe_opku", "linkkiry", "lastu_ry_", "fuusio_ry","sosa.ry","liikuapprolahti","kapital_ry","lut_es","rela.ry","lahti_es","cozycorner_club","lahti_es"]
    session_file_path = str(pathlib.Path(__file__).parent.resolve()) # Get the path of the script
    session_file_name = "\\session-bencebansaghi" # Name of the session file
    result_dicts=gpt_formater.return_formated_events(profiles,session_file_path,session_file_name)
    print(result_dicts)
    if result_dicts is None or result_dicts == []:
        print("No new events added to the file.")
        return
    count = 0
    try:
        with open("active_events_pickle", "rb") as f:
            events=pickle.load(f)
    except EOFError:
        events = []
    except Exception as e:
        print(f"Error while loading previously added events: {e}")
        events = []
    for one_dict in result_dicts:
        try:
            one_dict["date"]= datetime.strptime(one_dict["date"], "%d.%m.%Y").date()
            events.append(one_dict)
            count += 1
        except Exception as e:
            print(f"Error while converting date: {e}")
            continue
    with open("active_events_pickle", "wb") as f:
        pickle.dump(events, f)
    print(count, "new events added to the file.")
                
# function that removes the old events from active_events_pickle
def remove_old_events():
    print("Removing old events")
    events = []
    count=0
    with open("active_events_pickle", "rb") as f:
        events=pickle.load(f)
    with open("active_events_pickle", "wb") as f:
        today=datetime.now().date()
        for event in events:
            if event["date"] < today:
                events.remove(event)
                count += 1
        pickle.dump(events, f)
    print(count, "old events removed from the file.")

def main():
    application = Application.builder().token("6824458794:AAFg_y1TNYDbb6ff2dgJfeFPT4UL_f6vdb0").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, event_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CallbackQueryHandler(button_click))
    
    schedule.every().day.do(fetch_daily_events)
    schedule.every().day.do(remove_old_events)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
