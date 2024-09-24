import os
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
# import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from routers.demo.demo import DEMO_ROUTE


path=os.getenv('ENVIRONMENT')
if path:

    if path=='PRODUCTION':
        os.environ["ENVIRONMENT_PATH"] = '.env.production'
    elif path=='DEVELOPMENT':
        os.environ["ENVIRONMENT_PATH"] = '.env.development'
    elif path=='STAGING':
        os.environ["ENVIRONMENT_PATH"] = '.env.staging'
    else:
        raise RuntimeError('InCorrect  Environment')

    file_path = os.environ["ENVIRONMENT_PATH"]
    isFile = os.path.isfile(file_path) 
    if isFile==False:
        raise RuntimeError(file_path+' file not present')

else:
    raise RuntimeError('Missing  Environment')

load_dotenv(dotenv_path=str(os.getenv('ENVIRONMENT_PATH')))

# if os.getenv('ENVIRONMENT')=="PRODUCTION" or os.getenv('ENVIRONMENT')=="STAGING":

#     dsn = os.getenv('DSN')
#     sentry_sdk.init(
#         dsn= f"{dsn}",

#         # Set traces_sample_rate to 1.0 to capture 100%
#         # of transactions for performance monitoring.
#         # We recommend adjusting this value in production.
#         traces_sample_rate=1.0,
#         environment=str(os.getenv("ENVIRONMENT"))
#     )

from middleware.middleware import *
from utils.invalid_response_class import *
from utils.response_manipulator import CustomResponse
from utils.logging import init_logging

init_logging()
if path == "PRODUCTION":
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, title="Backend", version="1.0.0")
else:
    app = FastAPI(title="Backend", version="1.0.0")

app.add_middleware(SentryAsgiMiddleware)
 

app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(DEMO_ROUTE, prefix='/backend', tags=["Demo/Health Checks"],dependencies=[Depends(create_request_id), Depends(authorisation)] )
# app.include_router(EXCLUDE_ROUTE, prefix='/backend', tags=["Exclude Paths"], dependencies=[Depends(create_request_id)] )


# @app.exception_handler(CreditInsufficientError)
# async def credit_insufficient_error(request: Request, exc: CreditInsufficientError):
#     return CustomResponse(request=request, resp_code='CREDIT_402_INSUFFICIENT_CREDITS',  details={"available_credits": exc.details['data']['available_credits']}).respond()

@app.exception_handler(AuthenticationError)
async def invalidation_exception_handler(request: Request, exc: AuthenticationError):
    return CustomResponse(resp_code='HTTP_401_UNAUTHORIZED', message=exc.message, request=request).respond()
    
@app.exception_handler(AuthenticationMissing)
async def internal_server_error(request: Request, exc: AuthenticationMissing):
    return CustomResponse(resp_code='HTTP_401_AUTHORIZATION_MISSING', request=request).respond()

@app.exception_handler(RequestValidationError)
async def handle_error(request: Request, exc: RequestValidationError):
    data=jsonable_encoder(exc.errors())
    return CustomResponse(request=request, resp_code='HTTP_400_BAD_REQUEST', details=data).respond()

@app.exception_handler(InternalServerError)
async def internal_server_error(request: Request, exc: InternalServerError):
    return CustomResponse(resp_code='HTTP_500_SERVER_ERROR', request=request).respond()

@app.exception_handler(RequestTimeoutError)
async def internal_server_error(request: Request, exc: RequestTimeoutError):
    return CustomResponse(resp_code='HTTP_429_TOO_MANY_REQUEST', request=request).respond()



@app.get('/', tags=['root'])
async def read_root():
    return {"status": True,
            "message": "server is running",}

@app.get('/health-check', tags=['system'])
async def ping():
    return {"status":True,
            "message": "server health ok",}
