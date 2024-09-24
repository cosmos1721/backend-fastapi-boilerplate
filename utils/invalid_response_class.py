import json
from utils.logData import LogDataClass
from loguru import logger

class AuthenticationError(Exception):
    def __init__(self, message: str):
        self.message = message

class InternalServerError(Exception):
    def __init__(self, exception_dict : dict, request_id : str):
        LogDataClass(request_id).exception_log(exception_dict)

# class CreditInsufficientError(Exception):
#     def __init__(self, request_id: str, details: dict):
#         # self.message = message
#         self.details = details

class AuthenticationMissing(Exception):
    def __init__(self, message: str):
        self.message = message
        
class RequestTimeoutError(Exception):
    def __init__(self, message: str = None):
        self.message = message


