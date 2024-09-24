from aiobotocore.session import get_session
import os , mimetypes, json
import boto3
from requests.utils import quote
from utils.exception import CustomException

class S3_SERVICE(object):
    """ 
    A service class to interact with AWS S3 and SQS. This class provides methods for uploading files to S3, 
    sending messages to SQS, and retrieving files from S3 buckets.
    """

    def __init__(self,*args, **kwargs):
        self.AMAZON_ACCESS_KEY_id = os.getenv('AMAZON_ACCESS_KEY')
        self.aws_secret_access_key = os.getenv('AMAZON_SECRET_KEY')
        self.amazon_region=os.getenv('AMAZON_REGION')
        self.session = boto3.Session(aws_access_key_id = self.AMAZON_ACCESS_KEY_id , aws_secret_access_key = self.aws_secret_access_key , region_name=self.amazon_region)
        self.AWS_BUCKETS=json.loads(os.getenv('AWS_BUCKETS'))
        self.default_aws_bucket = self.AWS_BUCKETS['USER_STORE']
        self.region = os.getenv('AMAZON_REGION')
        self.generate_project_sqs=os.getenv('GENERATE_PROJECT_SQS')
        self.generate_project_sqs_production=os.getenv('GENERATE_PROJECT_SQS_PRODUCTION')
        
   

    async def upload_fileobj(self, fileobject, key,bucket=None):
        """
        Upload a file object to the specified S3 bucket.
        
        Args:
            fileobject: The file object to be uploaded.
            key: The S3 key (path) where the file will be stored.
            bucket: The S3 bucket name.

        Returns:
            str: The URL of the uploaded file if successful, otherwise False.
        """
        if not bucket:
            bucket = self.default_aws_bucket
        if not None and (bucket in self.AWS_BUCKETS):
            return "invalid_bucket" # create exception

        session = get_session()
        content_type = mimetypes.guess_type(key)[0] or 'application/octet-stream'
         
        async with session.create_client('s3', region_name=self.region,
                                         aws_secret_access_key=self.aws_secret_access_key,
                                         aws_access_key_id=self.AMAZON_ACCESS_KEY_id) as client:
            file_upload_response = await client.put_object( Bucket=bucket, Key=key, Body=fileobject, ContentType=content_type)

            if file_upload_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                key = quote(key) # convert # to %23
                return f"https://{bucket}.s3.amazonaws.com/{key}"
        return False

    async def upload_filecontent(self, file_content, key, bucket=None):
        """
        Upload file content to the specified S3 bucket.
        
        Args:
            file_content: The content of the file to be uploaded.
            key: The S3 key (path) where the file will be stored.
            bucket: The S3 bucket name.

        Returns:
            str: The URL of the uploaded file if successful, otherwise False.
        """
        if not bucket:
            bucket = self.default_aws_bucket
        if not None and (bucket in self.AWS_BUCKETS):
            return "invalid_bucket" # create exception
        
        session = get_session()
        content_type = mimetypes.guess_type(key)[0]
        async with session.create_client('s3', region_name=self.region,
                                         aws_secret_access_key=self.aws_secret_access_key,
                                         aws_access_key_id=self.AMAZON_ACCESS_KEY_id) as client:
            file_upload_response = await client.put_object(Bucket=bucket, Key=key, Body=file_content, ContentType=content_type)

            if file_upload_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                key = quote(key)  # convert # to %23
                return f"https://{bucket}.s3.amazonaws.com/{key}"
        return False

    async def add_message_on_sqs(self, sqs_url_key, message, group_id, dedup_id):
        """
        Send a message to the specified SQS queue.
        
        Args:
            sqs_url_key: The SQS URL key to identify the SQS queue.
            message: The message to be sent to the SQS queue.
            group_id: The message group ID for FIFO queues.
            dedup_id: The message deduplication ID for FIFO queues.

        Returns:
            dict: A dictionary containing the status and the SQS response.
        """
        sqs_url = self.__dict__.get(sqs_url_key)
        
        if not sqs_url:
            return {"status": 400, "sqs_message": {}, "error_message": "wrong sqs_key!"}  # TODO need to handle this return case to raise exception rather than returning the object.
        sqs_client = self.session.client('sqs')
        sqs_response = sqs_client.send_message(
            QueueUrl=sqs_url,
            MessageBody=json.dumps(message, default=str),
            MessageAttributes={},
            MessageGroupId=group_id,
            MessageDeduplicationId=dedup_id,
        )
        
        return {"status": 200, "sqs_response": sqs_response}
    
    async def get_attributes_sqs(self, sqs_url_key):
        """
        Retrieve the attributes of the specified SQS queue.
        
        Args:
            sqs_url_key: The SQS URL key to identify the SQS queue.

        Returns:
            dict: A dictionary containing the status and the SQS attributes.
        """
        sqs_url = self.__dict__.get(sqs_url_key)
        
        if not sqs_url:
            return {"status": 400, "sqs_message": {}, "error_message": "wrong sqs_key!"}  # TODO need to handle this return case to raise exception rather than returning the object.
        sqs_client = self.session.client('sqs')
        sqs_response = sqs_client.get_queue_attributes(
            QueueUrl=sqs_url,
            AttributeNames=['All']
        )
        
        return {"status": 200, "sqs_response": sqs_response}
    
    async def fetch_files_(self, folderId, bucket):
        """
        Fetch files from the specified folder in the S3 bucket.
        
        Args:
            folderId: The folder ID (prefix) in the S3 bucket.
            bucket: The S3 bucket name.

        Returns:
            list: A list of dictionaries containing image names and their URLs.
        """
        if not bucket:
            bucket = self.default_aws_bucket
        if not (bucket in self.AWS_BUCKETS):
            return "invalid_bucket"

        session = get_session()
        async with session.create_client('s3', region_name=self.region,
                                         aws_secret_access_key=self.aws_secret_access_key,
                                         aws_access_key_id=self.AMAZON_ACCESS_KEY_id) as client:
            paginator = client.get_paginator('list_objects_v2')
            operation_parameters = {'Bucket': bucket, 'Prefix': folderId}
            page_iterator = paginator.paginate(**operation_parameters)
            
            files = []
            async for page in page_iterator:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        key = obj["Key"]
                        if key != folderId:  # Skip the folderId itself
                            key = quote(key)
                            url = f"https://{bucket}.s3.amazonaws.com/{key}"
                            image_name = os.path.basename(key)
                            files.append({"imageName": image_name, "url": url})
            
            return files
