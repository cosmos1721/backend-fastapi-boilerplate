import os
import asyncio
from bson import ObjectId
import motor.motor_asyncio

# Load MongoDB URIs from environment variables
MONGO_DATA_URI = os.getenv("MONGO_DATA_URI")
MONGO_USER_URI = os.getenv("MONGO_USER_URI")

# Initialize MongoDB client for the data database
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DATA_URI)
client.get_io_loop = asyncio.get_event_loop
mongo_data_db_name = str(os.getenv('MONGO_DATA_DB_NAME'))
mongo_RAG_db_name = "test"
mongo_rag = client[mongo_RAG_db_name]
mongo_data = client[mongo_data_db_name]

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DATA_URI)
client.get_io_loop = asyncio.get_event_loop
mongo_data_db_name = str(os.getenv('MONGO_DATA_DB_NAME'))
mongo_data = client[mongo_data_db_name]

# Initialize MongoDB client for the user database
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_USER_URI)
client.get_io_loop = asyncio.get_event_loop
mongo_user_db_name = str(os.getenv('MONGO_USER_DB_NAME'))
mongo_user = client[mongo_user_db_name]

class PyObjectId(ObjectId):
    """
    Custom ObjectId class for handling BSON ObjectId validation and schema modifications.
    """

    @classmethod
    def __get_validators__(cls):
        """
        Yields the validator function for ObjectId.
        """
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """
        Validates if the given value is a valid ObjectId.
        
        Args:
            v (str): The value to validate.
        
        Returns:
            ObjectId: The validated ObjectId.
        
        Raises:
            ValueError: If the value is not a valid ObjectId.
        """
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        """
        Modifies the schema to represent ObjectId as a string in JSON.
        
        Args:
            field_schema (dict): The schema to modify.
        """
        field_schema.update(type="string")
