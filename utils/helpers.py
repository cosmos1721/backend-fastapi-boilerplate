import random
import string
import datetime
import hashlib
import time
import json
import base64
import aiofiles
import aiohttp
from fastapi import UploadFile
import pytz
import requests
from typing import Any, Dict, List

from db.service_utils.services import verify_id

#helpers to be used in the project as needed, so no need to write the same code again and again

adjectives = [
    'Bold', 'Cool', 'Dark', 'Epic', 'Fast',
    'Glad', 'Hero', 'Jolt', 'Keen', 'Lone',
    'Mega', 'Nerd', 'Oaky', 'Pure', 'Quick',
    'Rude', 'Star', 'Tidy', 'Vast', 'Wise'
]

nouns = [
    'Wolf', 'Bear', 'Hawk', 'Lynx', 'Stag',
    'Lion', 'Frog', 'Toad', 'Owl', 'Puma',
    'Dove', 'Duck', 'Fish', 'Lamb', 'Goat',
    'Mole', 'Newt', 'Seal', 'Swan', 'Deer'
]

class CUSTOM_ENCODER(json.JSONEncoder):
    """
    A custom JSON encoder that can serialize objects with a '__dict__' attribute
    and datetime objects to their ISO format.

    Example output:
    '{"name": "example", "date": "2024-08-05T10:00:00"}'
    """
    def default(self, obj: Any) -> Any:
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)

async def generate_uuid_string(size: int=12, usage: str = None) -> str:
    """
    Generate a random string of specified size.

    Usage:
        uuid_string(size=10, usage='game')

    Example output:
    'A1B2C3D4E5'
    """
    uuid = ''.join(random.choices(string.ascii_letters + string.digits, k=size))
    if usage == 'game':
        while True:
            uuid = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            if not await verify_id(id=uuid, usage='game'):  # If game_id is not a duplicate, return it
                return uuid
    elif usage == 'user_id':
        while True:
            uuid = ''.join(random.choices(string.digits, k=10))
            if not await verify_id(id=uuid, usage='user_id'):
                return uuid
    elif usage == 'project_id':
        while True:
            uuid = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            if not await verify_id(id=uuid, usage='project_id'):
                return uuid
    return uuid

def determine_user_role(email):
    # Define the roles
    roles = {
        "employee": ["input domain here"],
        "admin": "************",
        "premium": [],
        "invester": []
    }
    
    # Check if the email is admin
    if any(email.startswith(roles["admin"] + "@") and email.endswith(domain) for domain in roles["employee"]):
        return "admin"
    
    # Check if the email belongs to an employee
    if any(email.endswith(domain) for domain in roles["employee"]):
        return "employee"
    
    # Check if the email belongs to an invester
    if any(email.endswith(domain) for domain in roles["invester"]):
        return "invester"
    
    # Check if the email belongs to a premium user
    if any(email.endswith(domain) for domain in roles["premium"]):
        return "premium"
    
    # If none of the above, return normal user
    return "normal"

def get_profile_image(name: str) -> str:
    # Replace spaces in the name with '+'
    formatted_name = name.replace(' ', '+')
    
    # Create the full URL
    url = f"https://ui-avatars.com/api/?name={formatted_name}"
    
    return url

def current_datetime() -> str:
    """
    Get the current datetime in IST timezone with milliseconds.

    Usage:
        current_datetime()

    Example output:
    '2024-08-05 15:30:45.123'
    """
    IST = pytz.timezone('Asia/Kolkata')
    utc_now = datetime.datetime.now()
    ist_now = utc_now.astimezone(IST)
    return ist_now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Include milliseconds and trim microseconds

def content_are_different(content1, content2, content_type: str='json'):
    try:
        if content_type == 'json':
            # Check if the content is already a dictionary
            if isinstance(content1, dict) and isinstance(content2, dict):
                dict1 = content1
                dict2 = content2
            else:
                try:
                    # Parse the JSON strings into Python dictionaries
                    dict1 = json.loads(content1)
                    dict2 = json.loads(content2)
                except json.JSONDecodeError as e:
                    # Handle the case where the JSON is invalid
                    raise ValueError(f"Invalid JSON input: {e}")
            # Compare JSON objects
            return dict1 != dict2
        elif content_type == 'text':
            # Split the texts into lines and compare them
            text1_lines = content1.splitlines()
            text2_lines = content2.splitlines()
            # Compare text line by line
            return text1_lines != text2_lines
        else:
            raise ValueError("Unsupported content type. Use 'text' or 'json'.")
    except Exception as e:
        return f"An error occurred while comparing the content: {e}"


def add_time(minutes: int) -> str:
    """
    Add a specified number of minutes to the current datetime in IST timezone
    and return the new datetime with milliseconds.

    Args:
        minutes (int): The number of minutes to add to the current time.

    Returns:
        str: The new datetime in IST timezone after adding the minutes.
    """
    IST = pytz.timezone('Asia/Kolkata')
    utc_now = datetime.datetime.now()
    ist_now = utc_now.astimezone(IST)
    new_time = ist_now + datetime.timedelta(minutes=minutes)
    return new_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Include milliseconds and trim microseconds

def otp_generator(size: int) -> str:
    """
    Generate a numeric OTP of specified size.

    Usage:
        otp_generator(6)

    Example output:
    '123456'
    """
    return ''.join(random.choices("0123456789", k=size))

def generate_profileId() -> str:
# profile id generator, there are 3,600,000 unique combinations, the likelihood of a collision is very low.
    """
    Generate a unique profile ID using an adjective, noun, and random number with 3,600,000 unique combinations.

    Usage:
        generate_profileId()

    Example output:
    'BoldWolf#1234'
    """
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    random_number = str(random.randint(1000, 9999))
    return f"{adjective}{noun}#{random_number}"



async def get_hashed_string(text: str) -> str:
    """
    Return the SHA-1 hash of the input text.

    Usage:
        await get_hashed_string('example')

    Example output:
    '5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8'
    """
    return hashlib.sha1(text.encode()).hexdigest()

def current_timestamp(n: int = 3) -> float:
    """
    Return the current timestamp scaled by a factor of 10^n.

    Usage:
        current_timestamp(3)

    Example output:
    1625055806123.0
    """
    return time.time() * pow(10, n)

def merge_patch_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any], key_to_replace: List[str] = [], replace_path: str = '') -> Dict[str, Any]:
    """
    Merge two dictionaries with special handling for nested dictionaries and keys to replace.

    Usage:
        merge_patch_dicts(dict1, dict2, key_to_replace=[], replace_path='')

    Example output:
    {'key1': 'value1', 'key2': {'nestedKey': 'newValue'}}
    """
    if not dict1:
        dict1 = {}
    if not dict2:
        dict2 = {}
        
    merged_dict = dict1.copy()
    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            replace_key = key if not replace_path else replace_path + '_' + key
            if key_to_replace.count(replace_key):
                merged_dict[key] = dict2[key]
            else:
                merged_dict[key] = merge_patch_dicts(dict1[key], dict2[key], key_to_replace, replace_key)
        elif dict2.get(key) is not None:
            merged_dict[key] = dict2[key]

    return merged_dict

def decode_base_64_string(encoder_string: str) -> Dict[str, Any]:
    """
    Decode a base64 encoded string and parse it as JSON.

    Usage:
        decode_base_64_string('eyJrZXkiOiAidmFsdWUifQ==')

    Example output:
    {'key': 'value'}
    """
    decoded_string = base64.b64decode(encoder_string).decode()
    return json.loads(decoded_string)

def encode_base_64_string(data: Dict[str, Any]) -> str:
    """
    Encode a dictionary as a base64 string.

    Usage:
        encode_base_64_string({'key': 'value'})

    Example output:
    'eyJrZXkiOiAidmFsdWUifQ=='
    """
    json_string = json.dumps(data, cls=CUSTOM_ENCODER)
    return base64.b64encode(json_string.encode()).decode()

def calculate_time_difference(time1: str, time2: str) -> float:
    """
    Calculate the difference between two timestamps in seconds.

    Usage:
        calculate_time_difference('2024-08-05 15:30:45.123', '2024-08-05 15:30:46.456')

    Example output:
    1.333
    """
    datetime_format = '%Y-%m-%d %H:%M:%S.%f'
    dt1 = datetime.datetime.strptime(time1, datetime_format)
    dt2 = datetime.datetime.strptime(time2, datetime_format)
    return abs((dt2 - dt1).total_seconds())

def convert_datetime_timezone(datetime_str: str, from_tz: str, to_tz: str) -> str:
    """
    Convert a datetime string from one timezone to another.

    Usage:
        convert_datetime_timezone('2024-08-05 10:00:00.000', 'UTC', 'Asia/Kolkata')

    Example output:
    '2024-08-05 15:30:00.000'
    """
    from_timezone = pytz.timezone(from_tz)
    to_timezone = pytz.timezone(to_tz)
    naive_datetime = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')
    localized_datetime = from_timezone.localize(naive_datetime)
    converted_datetime = localized_datetime.astimezone(to_timezone)
    return converted_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

async def fetch_json(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return {"error": response.status_code}


async def filter_json_data(data, include_keys=None, exclude_keys=None):
    # example usage: 
    # include_keys = ["userID", "game_id", "gameName", ("ai_generated", "code-url")
    result = {}

    if include_keys:
        for key in include_keys:
            if isinstance(key, str) and key in data:
                result[key] = data[key]
            elif isinstance(key, tuple) and len(key) == 2:
                parent_key, child_key = key
                if parent_key in data and isinstance(data[parent_key], dict):
                    if child_key in data[parent_key]:
                        result[child_key] = data[parent_key][child_key]
    elif exclude_keys:
        for key in exclude_keys:
            if isinstance(key, str) and key in result:
                del result[key]
            elif isinstance(key, tuple) and len(key) == 2:
                parent_key, child_key = key
                if parent_key in result and isinstance(result[parent_key], dict):
                    if child_key in result[parent_key]:
                        del result[parent_key][child_key]
    else:
        result = data.copy()
    
    return result

async def fetch_data(source: Any, is_url: bool = True) -> str:
    if is_url:
        # Fetch data from URL
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(source) as response:
                    response.raise_for_status()  # Raise an error for bad status codes
                    return await response.text()
        except aiohttp.ClientError as e:
            return f"An error occurred while fetching data from URL: {e}"
    else:
        # Handle UploadFile (read file directly)
        try:
            data = await source.read()  # Read the file content into memory
            return data.decode('utf-8')
        except Exception as e:
            return f"An error occurred while reading the file: {e}"
