import json
from fastapi.responses import JSONResponse
from utils.logData import LogDataClass
from typing import Union
from pydantic import validate_arguments
from enum import Enum

#https://restfulapi.net/http-status-codes/ for error codes reference

class CustomResponse:
    """
    A class to standardize the creation and handling of HTTP responses in a FastAPI application.

    Attributes:
        LEGAL_RESPONSE_CODES (dict): A dictionary containing HTTP response codes and messages.
        resp_codes (Enum): An enumeration of the response codes.
    """

    LEGAL_RESPONSE_CODES = {
        
        # 2XX Success
        'HTTP_200_SUCCESS': { 
            "status": 200, 
            "message": "Success" 
        },
        'HTTP_201_CREATED': {
            "status": 201,
            "message": "Resource Created"
        },
        'HTTP_202_REQUEST_ACCEPTED': {
            "status": 202,
            "message": "Request successfully accepted"
        },
        'HTTP_204_NO_CONTENT': {
            "status": 204,
            "message": "No Content" 
        },
        'HTTP_207_MULTI_STATUS': {
            "status": 207,
            "message": "Multi-Status"
        },
        
        # 3XX Redirection
        'HTTP_301_MOVED_PERMANENTLY': {
            "status": 301,
            "message": "Moved Permanently"
        },
        'HTTP_304_NOT_MODIFIED': {
            "status": 304,
            "message": "Not Modified"
        },
        'HTTP_305_USE_PROXY': {
            "status": 305,
            "message": "Use Proxy"
        },
        
        # 4XX Client Error
        'HTTP_400_BAD_REQUEST': {
            "status": 400,
            "message": "Bad Request"
        },
        'HTTP_401_UNAUTHORIZED': {
            "status": 401,
            "message": "Invalid Auth Credentials"
        },
        'HTTP_401_AUTHORIZATION_MISSING': {
            "status": 401,
            "message": "Authorization Credentials Missing "
        },
        'CREDIT_402_INSUFFICIENT_CREDITS': {
            "status": 402,
            "message": "Insufficient credits"
        },
        'HTTP_402_PAYMENT_REQUIRED': {
            "status": 402,
            "message": "Payment Required"
        },
        'HTTP_403_FORBIDDEN': {
            "status": 403,
            "message": "Forbidden"
        },
        'HTTP_404_NOT_FOUND': {
            "status": 404,
            "message": "Not Found"
        },
        'HTTP_405_METHOD_NOT_ALLOWED': {
            "status": 405,
            "message": "Method Not Allowed"
        },
        'HTTP_406_NOT_ACCEPTABLE': {
            "status": 406, # accept header not supported
            "message": "Not Acceptable"
        },
        'HTTP_407_PROXY_AUTHENTICATION_REQUIRED': {
            "status": 407,
            "message": "Proxy Authentication Required"
        },
        'HTTP_409_CONFLICT': {
            "status": 409,
            "message": "Conflict"
        },
        'HTTP_429_TOO_MANY_REQUEST': {
            "status": 429, #used with the Retry-After header 
            "message": "Too many Requests. Try again later" 
        },
        
        # 5XX Server Error
        'HTTP_500_SERVER_ERROR': {
            "status": 500,
            "message": "OOPS!! Server Error"
        },
        'AI_ERROR': {
            "status": 500,
            "message": "AI Process/Server Error"
        },
        'AI_502_BAD_GATEWAY': {
            "status": 502,
            "message": "Bad Gateway/AI server."
        },
        'AI_503_CUDA_SERVICE_UNAVAILABLE': {
            "status": 503,
            "message": "CUDA Service Error"
        }
    }

    resp_codes = Enum('resp_codes', {field: field for field in LEGAL_RESPONSE_CODES.keys()}, type=str)

    @validate_arguments
    def __init__(self, request, resp_code: str = 'HTTP_403_FORBIDDEN', data: Union[str, dict, list] = {}, details: Union[str, dict, list] = {}, message: str = ''):
        """
        Initialize the CustomResponse object with the specified parameters.

        Args:
            request (Request): The FastAPI request object.
            resp_code (resp_codes): The response code.
            data (Union[str, dict, list], optional): The response data. Defaults to {}.
            details (Union[str, dict, list], optional): Additional details. Defaults to {}.
            message (str, optional): Custom message for the response. Defaults to ''.

        Attributes:
            request_id (str): The request ID extracted from the request object.
            status (int): The HTTP status code.
            request_url (str): The request URL.
            responseData (dict): The constructed response data dictionary.
        """
        
        resp_status = CustomResponse.LEGAL_RESPONSE_CODES[resp_code]['status']
        resp_message = message if message else CustomResponse.LEGAL_RESPONSE_CODES[resp_code]['message']
        error = bool(resp_status >= 400)

        self.request_id = getattr(request.state, 'request_token', 'unknown')
        self.start_time = getattr(request.state, 'start_time', 'unknown')
        self.status = resp_status
        self.request_url = request.url.path
        self.location = request.url.path or None # write proper logic to get the location
        self.responseData = {
            "code": resp_code,
            "message": resp_message,
            "data": data,
            "error": error,
            "details": details
        }
    
    def respond(self, response: JSONResponse = None):
        """
        Create and return a JSONResponse with the stored status code and response data.

        Args:
            response (JSONResponse, optional): An optional existing JSONResponse to modify. Defaults to None.

        Returns:
            JSONResponse: The created or modified JSONResponse object.
        """
        
        if response is None:
            response = JSONResponse(status_code=self.status, content=self.responseData)
        else:
            response.status_code = self.status
            response.content = self.responseData
            response.body = json.dumps(self.responseData).encode('utf-8')

        if 300 <= self.status < 400 and self.location:
            response.headers['Location'] = self.location

        response.set_cookie(key='request_id', value=self.request_id) # for team to track the request to backend
        
        if self.status >= 400:
            if self.status >=500 and self.responseData["code"] in ['AI_ERROR', 'AI_502_BAD_GATEWAY', 'AI_503_CUDA_SERVICE_UNAVAILABLE']:
                LogDataClass(request_id=self.request_id).general_log(self.responseData, log_type="AI", error=True)
                # todo, notification for staging and specific to prod cases, slack notfications
            else:
                LogDataClass(request_id=self.request_id).warn_log(response)
        else:
            LogDataClass(request_id=self.request_id).response_log(self.start_time, response)
        return response