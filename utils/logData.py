import json
import os
import pprint
from loguru import logger
from utils.helpers import current_datetime, calculate_time_difference
from utils.logging import init_logging, logging

# init_logging()

class LogDataClass(object):
    """Class for structured logging of requests, responses, and general data with optional color output in development."""
    
    def __init__(self, request_id) -> None:
        """Initialize the LogDataClass with a request ID."""
        self.request_id = request_id
        self.job_dict = {
            "@fields": {
                'level': "info"
            },
            "@message": {
                "request_id": self.request_id,
                "time": str(current_datetime()),
            }
        }
        
    def log_data(self):
        """Log the data based on the specified log level."""
        level = self.job_dict["@fields"].get("level", "info").upper()
        userAgent = self.job_dict["@message"].get("user-agent", None)
        if os.getenv('ENVIRONMENT') == "DEVELOPMENT":
            if userAgent == "AI":  # add specific term for it
                level = "AI REQ"
            self.color_pprint(self.job_dict, level)
        else:
            if level == "INFO":
                if userAgent == "AI":  # add specific term for it
                    logger.debug(self.job_dict)
                else:
                    logger.info(self.job_dict)
            elif level == "WARN":
                logger.warning(self.job_dict)
            elif level == "ERROR":
                if os.getenv('ENVIRONMENT') == "STAGING":
                    self.color_pprint(self.job_dict, level)
                else:
                    logger.error(self.job_dict)
            elif level == "AI LOG" or level == "SSE LOG":
                logger.debug(self.job_dict)
            else:
                logger.info(self.job_dict)

    def color_pprint(self, data, level):
        """Pretty print data with colors based on log level."""
        try:
            color_codes = {
                "INFO": "\033[0m",  # White
                "WARN": "\033[93m",  # Yellow
                "ERROR": "\033[91m",  # Red
                "AI REQ": "\033[94m",  # Blue
                "AI LOG": "\033[92m",  # Green
                "SSE LOG": "\033[92m",  # Green
                "ENDC": "\033[0m",  # Reset to default
            }
            color = color_codes.get(level, "\033[0m")
            pp = pprint.PrettyPrinter()
            formatted_data = pp.pformat(data)
            try:
                print(f"\n{color}{formatted_data}{color_codes['ENDC']}")
            except Exception as e:
                # Log the error using the standard logging mechanism
                logging.error("Failed to print colored output: %s", e)
                # Fallback to standard pprint without colors
                print(formatted_data)
        except Exception as e:
            print(e)
                  
    async def request_log(self, request):
        """Log the details of an incoming request."""
        self.job_dict["@message"].update(dict(request.headers))
        formData = await request.form()
        if formData:
            self.job_dict["@message"]['formData'] = dict(formData)
        else:
            self.job_dict["@message"]['formData'] = {}
            jsonData = await request.body()
            if jsonData:
                self.job_dict["@message"]['jsonData'] = jsonData
            else:
                self.job_dict["@message"]['jsonData'] = {}
        self.job_dict["@message"]['params'] = dict(request.query_params)
        self.job_dict["@message"]['url'] = str(request.url)
        self.job_dict["@message"]['method'] = str(request.method)
        self.log_data()
        return "Done"
    
    def general_log(self, data, log_type: str= "AI", response=None, error=False):
        """Log general data with AI  and SSE Log level."""
        if log_type == "AI":
            log_level = "AI Log"
        elif log_type == "SSE":
            log_level = "SSE Log"
        self.job_dict['@fields']['level'] = log_level
        self.job_dict['data'] = data
        if response:
            self.job_dict['response'] = response
        self.log_data()
    
    def response_log(self, start_time, response):
        """Log the details of an outgoing response."""
        end_time = str(current_datetime())
        duration = calculate_time_difference(start_time, end_time)
        self.job_dict["@message"]['duration'] = duration
        self.job_dict["@message"].update(dict(response.headers))
        self.job_dict["@message"]['body'] = json.loads(response.body)
        self.job_dict["@message"]['response_status_code'] = response.status_code
        self.log_data()

    def warn_log(self, response):
        """Log a warning response."""
        self.job_dict["@message"].update(dict(response.headers))
        self.job_dict['@fields']['level'] = "Warn"
        self.job_dict["@message"]['body'] = json.loads(response.body)
        self.job_dict["@message"]['response_status_code'] = response.status_code
        self.log_data()

    def exception_log(self, error_dict={}):
        """Log an exception with error details."""
        self.job_dict['@fields']['level'] = "Error"
        self.job_dict['@message'].update(error_dict)
        self.log_data()
