FROM python:3.8.12-slim

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# ENV ENVIRONMENT=STAGING
WORKDIR /code/
# Install dependencies
#RUN pip install pipenv
#RUN pipenv install 
COPY Pipfile  /code/
RUN pip install pipenv
RUN pipenv install

RUN pipenv install --system --dev
COPY . /code/

EXPOSE 7443
CMD ["uvicorn", "main:app","--proxy-headers", "--host", "0.0.0.0", "--port", "7443", "--workers" ,"2", "--loop","asyncio"]
