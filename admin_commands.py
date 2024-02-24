import os
import csv
from dotenv import load_dotenv

load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")
if not CSV_FILE_PATH:
    raise Exception("CSV file path not found in environment variables.")

def read_events():
    with open(CSV_FILE_PATH, mode='r',encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

def write_events(events):
    with open(CSV_FILE_PATH, mode='w', newline='',encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['date', 'name', 'description', 'link'])
        writer.writeheader()
        for event in events:
            writer.writerow(event)

def modify_event(events, event_id):
    events,event_to_modify = remove_event(events,event_id)
    if not event_to_modify or not events:
        return
    modify=input("What would you like to modify? Include all numbers (1: Date, 2: Name, 3: Description, 4: Link): ")
    if "1" in modify:
        event_to_modify['date'] = input(f"Enter the new date (current value: {event_to_modify['date']}): ")
    if "2" in modify:
        event_to_modify['name'] = input(f"Enter the new name (current value: {event_to_modify['name']}): ")
    if "3" in modify:
        event_to_modify['description'] = input(f"Enter the new description (current value: {event_to_modify['description']}): ")
    if "4" in modify:
        event_to_modify['link'] = input(f"Enter the new link (current value: {event_to_modify['link']}): ")
    events.append(event_to_modify)
    return events
    

def add_event(events):
    print("Enter the details for the new event:")
    new_event = {
        'date': input("Date: "),
        'name': input("Name: "),
        'description': input("Description: "),
        'link': input("Link (not mandatory): ")
    }
    if new_event['date'] and new_event['name'] and new_event['description']:
        events.append(new_event)
    return events
    
def remove_event(events,remove_id):
    try:
        removed=events.pop(int(remove_id))
        return events,removed
    except IndexError:
        print("Event not found.")
        return None,None
    except ValueError:
        print("Invalid ID.")
        return None,None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None,None


def run_menu():
    events = read_events()
    while True:
        print(f"These are the current events:")
        event_id=0
        for event in events:
            print(f"ID = {event_id} {event['name']} on {event['date']} at {event['link']}")
            print(f"Description: {event['description']}\n")
            event_id+=1
        
        choice = input("Enter your choice (1: Remove, 2: Modify, 3: Add, 4: Quit): ")
        
        if choice == "1":
            remove_id=input("Enter the event ID to remove: ")
            temp_events,_=remove_event(events,remove_id)
            if temp_events:
                events=temp_events
                print("Event removed successfully.")
        elif choice == "2":
            modify_id=input("Enter the event ID to modify: ")
            temp_events=modify_event(events,modify_id)
            if temp_events:
                events=temp_events
                print("Event modified successfully.")
            else:
                print("Error while modifying event.")
        elif choice == "3":
            temp_events=add_event(events)
            if temp_events:
                events=temp_events
                print("Event added successfully.")
            else:
                print("Error while adding event.")
        elif choice == "4":
            save_changes(events)
            break
        else:
            print("Invalid choice. Please try again.")
            continue
        if input("Type 4 to quit or press enter to continue.") == "4":
            save_changes(events)
            break
        
def save_changes(events):
    first=input("Do you want to save the changes? Type 'yes' or 'y' to save.")
    if first.lower() == "yes" or first.lower() =="y":
        write_events(events)
        print("Changes saved.")
    else:
        last=input("Last chance to save your changes. They will be discarded unless you type 'save'.")
        if last.lower() == "save":
            write_events(events)
            print("Changes saved.")

if __name__ == "__main__":
    password = input("Enter the admin password: ")
    
    if password == ADMIN_PASSWORD:
        run_menu()
    else:
        print("Incorrect password. Access denied.")
