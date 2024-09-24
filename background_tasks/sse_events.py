import asyncio
import requests
from queue import LifoQueue
from datetime import datetime, timedelta

from utils.logData import LogDataClass
# Dictionary to hold queues for each client
queues = {}

# Function to calculate expiry time based on type
def calculate_expiry(event_type: str) -> datetime:
    if event_type == "global":
        return datetime.now() + timedelta(days=1)
    elif event_type == "errors":
        return datetime.now() + timedelta(hours=2)
    elif event_type in ["normal", "game_creation_status", "assets"]:
        return datetime.now() + timedelta(minutes=10)
    elif event_type == "explicit":
        return None  # No expiry for explicit
    else:
        return datetime.now() + timedelta(minutes=10)  # Default expiry

# Function to add current time, expiry, and manage queue
async def add_event(client_id: str, event: dict):
    event["created"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event["expires"] = calculate_expiry(event["type"]).strftime("%Y-%m-%d %H:%M:%S") if calculate_expiry(event["type"]) else None
    
    if client_id not in queues:
        queues[client_id] = LifoQueue()

    if event["type"] in ["global", "explicit"]:
        await delete_specific_events(client_id, ["global", "explicit"])
    queues[client_id].put(event)
    # print(f"final state of queue for client {client_id}: {list(queues[client_id].queue)}") to checkout queue
    # print(f"Current queue size: {queues[client_id].qsize()}") to checkout queue size


# Function to delete specific types of events for a client
async def delete_specific_events(client_id: str, event_types: list):
    if client_id in queues:
        new_queue = LifoQueue()
        while not queues[client_id].empty():
            event = queues[client_id].get()
            if event["type"] not in event_types:
                new_queue.put(event)
        queues[client_id] = new_queue  # Replace with filtered queue

# Event generator to continuously check the queue
async def event_generator(client_id: str):
    while True:
        if client_id in queues:
            while not queues[client_id].empty():
                event = queues[client_id].get()
                yield f"data: {event}\n\n"

        await asyncio.sleep(0.1)  # Small sleep to prevent a tight loop

# Direct function call for sending events TODO
async def sse_alert(request, event_data : dict):  
    try: 
        # Using requests to send an event
        log=LogDataClass(request.state.request_token)
        headers = {
            'accept': 'application/json',
            'Authorization': f"Bearer {request.state.request_token}"
        }
        resp = requests.post("http://0.0.0.0:8000/backend/alert/", json=event_data)
        if resp.status_code == 200:
            log.general_log(resp.status_code, event_data, log_type="SSE")
            return True
        else:
            log.general_log(resp.status_code, event_data, log_type="SSE", error=True)
            return False
    except:
        return False
