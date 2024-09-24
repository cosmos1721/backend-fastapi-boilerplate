### **Project Description**

This Set of API can be used by companies to sell AI products to the public, such as virtual try-on tools for cataloging retailers. 

The API is user-friendly and can be easily integrated into existing systems, making it a versatile and powerful tool for enhancing customer experiences and driving sales. 

With the ability to generate highly realistic images and videos, our API has the potential to revolutionize the way companies interact with and sell to their customers.



### Fast-api Framework

FastAPI framework, high performance, easy to learn, fast to code, ready for production

## ENVIRONMENT
For each Type of environment Create a respective file and pass those variables in **start.sh** file 

**Key** : ENVIRONMENT

**Value** : [PRODUCTION,STAGING,DEVELOPMENT]  (Any One)

**File** : [.env.production, .env.staging, .env.development] (Respective to Value)



## Database Connection

### For Postgres
Add **db_host** , **db_password** , **db_user** , **db_name**  , **db_port**  in env file.

### For NoSQL
Add **MONGO_USER_URI**  or **MONGO_DATA_URI**  if defining diff clusters based on requirement, **MONGO_USER_DB_NAME**  for table name in env file.

**Note:** Although using SQLAlchemy and MongoDB but that is just to create connection, Can implement models with respect to your needs.

## AWS Connection

Add **AMAZON_SECRET_KEY** , **AMAZON_ACCESS_KEY**,  **AWS_BUCKET_UI_ASSETS** , **AWS_BUCKETS** (add buckets in key pair), **AMAZON_REGION**  in the env file

## Mail Service

Brevo SMTP is used to configure mail service

Add **BREVO_SENDER_NAME** , **BREVO_SENDER_EMAIL** , **BREVO_API_KEY**  in env file.
If you want to use the current configuration to use login methods, add HOSTING_URL as well. 

**Note:** Although using Brevo but can implement models with respect to your needs.


## JWT Authentication
Add **SECRET_KEY**  in env file, can create it  by multiple means, also change the authentication type according to your needs

## Sentry Configuration
Add **DSN** in env file 

## TO RUN PROJECT

**Requirement** : Docker

To run just use command "**bash start.sh**"  on linux need to configure for other OS.

Created Reponse, Logging Common Structure
Added request_id(Can also be passed from Nginx Server) which can be helpful for debugging


## Boilerplate
https://github.com/cosmos1721/backend-fastapi-boilerplate

## CONTRIBUTION
Still Learning,

So feel free, Anything You wanna contirubute.

