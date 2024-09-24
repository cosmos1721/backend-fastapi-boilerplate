import sys
import traceback
import json
from sentry_sdk import push_scope, capture_exception
from utils.invalid_response_class import InternalServerError

class CustomException:
    """
    Handles exceptions by capturing details, logging them to Sentry, and providing a structured JSON response.

    Attributes:
        Error_data (dict): Contains detailed information about the exception.
        exception_obj (dict): A structured object containing the status, message, traceback, and error data.

    Methods:
        raise_exception(request_id): Raises an InternalServerError with the captured error data.
        return_json(): Returns the captured exception details as a JSON string.
    """

    def __init__(self):
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        self.Error_data = {
            "exception_type": str(exception_type),
            "exception_object": str(exception_object),
            "exception_traceback": str(traceback.format_exc()),
            "line_number": str(line_number),
            "filename": str(filename),
        }
        with push_scope() as scope:
            scope.set_extra("custom_exp_obj", self.Error_data)
            capture_exception(exception_object)
        
        self.exception_obj = {
            "status": 500,
            "message": str(exception_object),
            "traceback": str(traceback.format_exc()),
            "Error_Data": self.Error_data,
        }
#not logging rate limit exceptions and request timeout exceptions
    def raise_exception(self, request_id):
        """Raises an InternalServerError with the captured error data.

        Args:
            request_id (str): The unique identifier for the request that triggered the exception.
        """
        raise InternalServerError(self.Error_data, request_id)
    
    def return_json(self): 
        """Returns the captured exception details as a JSON string.

        Returns:
            str: A JSON string containing the exception details.
        Example:
            except Exception as e:
            return CustomException().return_json()
        """
        return json.dumps(self.exception_obj)