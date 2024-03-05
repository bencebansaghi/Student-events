from datetime import datetime, timedelta, time
import logging
import os
from dotenv import load_dotenv
import io
import pathlib
from telegram import (
    InputFile,
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    CallbackContext,
)
import gpt_formater
from ics import Calendar, Event
import aiofiles
import csv
import aiocsv

# Logging
logging.basicConfig(
    filename=os.path.join(pathlib.Path(__file__).parent.resolve(),'studentevents.log'),
    filemode='a',
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Constants
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
INSTAGRAM_PAGES = os.getenv("INSTAGRAM_PAGES")
if INSTAGRAM_PAGES:
    INSTAGRAM_PAGES = INSTAGRAM_PAGES.split(",")
    if len(INSTAGRAM_PAGES) == 0:
        logging.error("INSTAGRAM_PAGES environment variable is empty.")
        INSTAGRAM_PAGES = None
else:
    logging.error("INSTAGRAM_PAGES environment variable is not set.")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")
if not CSV_FILE_PATH:
    logging.error("CSV_FILE_PATH environment variable is not set.")
    CSV_FILE_PATH = "active_events.csv"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user 
    keyboard = [
        [{"text": "All Events"}],
        [{"text": "Events in the next week"}],
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=True, resize_keyboard=True
    )

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
    await update.message.reply_html(
        "This bot is funded by LTKY and is maintained and ran by Bence Bánsághi.\n"
        "For any ideas for bot functionality, please contact <a href='https://www.ltky.fi'>LTKY</a>.\n"
        "The code of the bot is available on <a href='https://github.com/bencebansaghi/Student-events'>GitHub</a>. "
        "For any inquiries or issues about the code or bot functionality, feel free to contact me at on github or any of my socials.\n"
    )


async def event_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if "event" in update.message.text.lower():
        all_events = await get_dicts_from_file()
        
        all_events.sort(key=lambda x: x["date"])

        if "events in the next week" in update.message.text.lower():
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
                f"*Name of the event:* {escape_markdown(event['name'])}\n"
                f"*Date:* {escape_markdown(event['date'].strftime('%Y %B %d'))}\n\n"
                f"*Description:* {escape_markdown(event['description'])}\n"
            )

            calendar_date_string = event["date"].strftime("%Y-%m-%d")
            callback_data = f"calendar:{calendar_date_string}:{event['name']}"
            callback_data = callback_data[
                :64
            ]  # The maximum length of callback_data is 64 characters

            if (
                not event["link"] or event["link"] == ""
            ):  # Manually added events might not have a link
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Add to Calendar", callback_data=callback_data
                        )
                    ]
                ]
            else:
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Add to Calendar", callback_data=callback_data
                        ),
                        InlineKeyboardButton("Open Instagram Post", url=event["link"]),
                    ]
                ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            try:
                await update.message.reply_markdown_v2(
                    formatted_message, reply_markup=reply_markup
                )
            except Exception as e:
                logging.error(
                    f"Error while sending message in event {event['name']}: {e}"
                )


# This function handle the "add to calendar" button
# It will create an iCalendar file and send it to the user
async def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data.split(":")

    if data[0] == "calendar":
        date_str = data[1]
        event_name = data[2]

        # Convert the date string to a datetime object with midnight time
        event_date = datetime.strptime(date_str, "%Y-%m-%d").replace(
            hour=0, minute=0, second=0
        )

        # Generate iCalendar file
        cal = Calendar()
        event = Event()
        event.name = event_name
        event.begin = event_date
        event.make_all_day()
        cal.events.add(event)

        # Convert the calendar to bytes
        cal_str = cal.serialize()
        cal_bytes = cal_str.encode("utf-8")

        # Send the iCalendar file as a document using InputFile
        cal_file_input = InputFile(io.BytesIO(cal_bytes), filename=f"{event_name}.ics")
        await context.bot.send_document(chat_id=user_id, document=cal_file_input)


async def get_dicts_from_file():  # Returns list of dictionaries with date object, name, description, link keys, sorted by date
    events = []
    try:
        async with aiofiles.open(
            CSV_FILE_PATH, "r", newline="", encoding="utf-8"
        ) as file:
            reader = aiocsv.AsyncDictReader(file)
            async for event in reader:
                events.append(event)
    except FileNotFoundError:
        logging.error("File not found.")
    events_datetime = []
    for event in events:
        try: # It should always be in this format, but just in case
            event["date"] = datetime.strptime(event["date"], "%d.%m.%Y").date()
        except Exception as e:
            logging.error(f"Error while converting date string to datetime object of event {event['name']}: {e}")
            continue
        events_datetime.append(event)
    return events_datetime


def file_and_header_exists():
    header_exists = False
    try:
        with open(CSV_FILE_PATH, "r", newline="", encoding="utf-8") as f:
            sample = f.read(2048)
            header_exists = csv.Sniffer().has_header(sample)
    except FileNotFoundError:
        pass
    return header_exists


def escape_markdown(text):  # Needed for reply_markdown
    escape_chars = "_*~`>#+-=|{}.!()[]`"
    return "".join(["\\" + char if char in escape_chars else char for char in text])


async def write_new_events_to_file(events_dicts):
    # checkto make sure the file exists and has a header even if there are no events to be added to not disrupt remover function
    if not file_and_header_exists():
        async with aiofiles.open(CSV_FILE_PATH, "w", newline="", encoding="utf-8") as f:
            writer = aiocsv.AsyncDictWriter(
                f, fieldnames=["date", "name", "description", "link"]
            )
            await writer.writeheader()

    if not events_dicts:
        logger.info("No new events added to the file.")
        return

    async with aiofiles.open(CSV_FILE_PATH, "a", newline="", encoding="utf-8") as f:
        writer = aiocsv.AsyncDictWriter(
            f, fieldnames=["date", "name", "description", "link"]
        )
        added_event_counter = 0
        for event in events_dicts:
            await writer.writerow(event)
            added_event_counter += 1
        logging.info(f"{added_event_counter} new events added to the file.")


async def fetch_new_events_to_dicts():
    logging.info("Fetching new events")
    session_file_path = str(pathlib.Path(__file__).parent.resolve())
    session_file_name = "session-lut_student_events"
    result_dicts = []
    if INSTAGRAM_PAGES:
        try:
            result_dicts = await gpt_formater.return_formated_events(
                INSTAGRAM_PAGES, session_file_path, session_file_name
            )
        except Exception as e:
            logging.error(f"Error while fetching events: {e}")

    if result_dicts:
        return result_dicts
    else:
        return


async def add_new_events(context: CallbackContext) -> None:
    new_events = await fetch_new_events_to_dicts()
    await write_new_events_to_file(new_events)


async def remove_old_events(context: CallbackContext) -> None:
    today = datetime.now().date()
    events = []
    removed_event_counter = 0
    tempfile_name = "tempfile.csv"

    if not file_and_header_exists():
        logging.warning(
            "The file does not exist. No old events to remove."
        )  # warning, because this function should only be called after add_new_events, which makes sure in
        return

    async with aiofiles.open(CSV_FILE_PATH, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(await file.read())
        for event in reader:
            event_date = datetime.strptime(event["date"], "%d.%m.%Y").date()
            if event_date > today:
                events.append(event)
            else:
                removed_event_counter += 1

    logging.info(f"{removed_event_counter} old events removed from the file.")

    async with aiofiles.open(tempfile_name, "w", newline="", encoding="utf-8") as f:
        writer = aiocsv.AsyncDictWriter(
            f, fieldnames=["date", "name", "description", "link"]
        )
        await writer.writeheader()
        for event in events:
            await writer.writerow(event)
        os.replace(tempfile_name, "active_events.csv")


def main():
    if BOT_TOKEN is None:
        return
    application = Application.builder().token(BOT_TOKEN).build()
    application.job_queue.run_daily(
        add_new_events, time=time(hour=22, minute=0, second=0, microsecond=0)
    )
    application.job_queue.run_daily(
        remove_old_events, time=time(hour=22, minute=1, second=0, microsecond=0)
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, event_command)
    )
    application.add_handler(CallbackQueryHandler(button_click))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
