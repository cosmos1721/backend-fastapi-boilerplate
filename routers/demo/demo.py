import os , uuid , json, time

from fastapi import APIRouter, Form,Request,File ,UploadFile,Depends, Body

from utils.invalid_response_class import InternalServerError
from utils.response_manipulator import CustomResponse
from utils.exception import CustomException
from utils.rate_limiter import RateLimiter
from utils.logData import LogDataClass

DEMO_ROUTE = APIRouter(dependencies=[Depends(RateLimiter())] )

@DEMO_ROUTE.post('/demo' )
def demo(request: Request ):
    try:
        
        log=LogDataClass(Request)
        # Dummy Response
        time.sleep(1)
        data={
            "resp":"Success" 
        }
        log.general_AI_log(data)
        return CustomResponse(resp_code='HTTP_200_SUCCESS', data=data, message='Success', request=request).respond()
        
    except:
        raise CustomException().raise_exception(request_id=request.state.request_token)