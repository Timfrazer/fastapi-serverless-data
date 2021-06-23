---
title: "Serverless Python API"
date: 2021-05-26T16:46:14-04:00
draft: false
---

# Serverless API using fastAPI + Pydantic & Athena datastore
## Intro

In this article, we will look at creating an API and datastore using the serverless framework on AWS with API gateway and creating it all using the modern python framework FastAPI with pydantic.
Perhaps, you need to create an API that scales or costs you little to run, and you would rather not bother with setting up the infrastructure. Now there are plenty of downsides to running serverless ( warmup, 15 min runtime etc.); however, I have found that you can, with a few tweaks, have a scalable API that, when combined with the serverless framework, creates an API that can validate incoming data fast, and that makes development quick and cheap to run.
After we have stood up the API we will store the results in AWS Athena. Amazon Athena is a query service for analyzing data in S3 with SQL under the hood. Athena uses a distributed SQL engine called [Presto](https://prestodb.io/), which is used to run the SQL queries against your data in S3.

## Objectives

By the end of this article, you should be able to:
1. Develop a restful API on AWS Lambda combined with a simple HTTP API gateway using mostly Python.
2. Ingest and validate data using pydantic and more in-depth validators for clean data.
4. Create tests with code coverage for your API.
5. Store the validated data in the AWS Athena datastore.
6. Add authentication with AWS Cognito all in the serverless framework - too much for the article?
7. Add domains api.yourdomain.com/endpoint - too much for the article?

## Assumptions

You have access to a working AWS account so you can deploy your service. All testing is done locally however you will miss out on all the fun stuff if you can't deploy. You will also need to setup  the serverless framework and have it installed [serverless framework](https://github.com/serverless/serverless) 

## Section 1
We will setup the project using [FastAPI](https://fastapi.tiangolo.com/) and [Mangum](https://github.com/jordaneremieff/mangum).
Mangum is an adapter for using ASGI (Asynchronous Server Gateway Interface) for AWS Lambda.
We will use FastAPI however, you could use Quart, Django-rest etc with [Mangum](https://github.com/jordaneremieff/mangum)
The wrapper helps handle things like [lifespan](https://asgi.readthedocs.io/en/latest/specs/lifespan.html) think of it like [uvicorn](https://github.com/encode/uvicorn) for AWS Lambda.


The directory and  is going to look like the following by the time we are done.

```
fastapi-serverless-api
    ├── serverless.yml
    ├── venv
    ├── requirements.txt
    └── app
        ├── __init__.py
        │   └── main.py
        |   └── models.py
        └── tests
            ├── __init__.py
            └── conftest.py
            └── test_main.py
```

We will be using `Python 3.8`, but let's create the directory structure and setup the virtual env for development.
```
$ mkdir fastapi-serverless-api && cd fastapi-serverless-api
$ mkdir app && cd app
$ mkdir test
$ cd ..
$ python3.8 -m venv venv
$ source venv/bin/activate
(env)$ pip install flask==1.1.2
```

For the `requirements.txt` file just add the following.
```txt
fastapi==0.65.1
pydantic
# required for serverless
mangum==0.11.0
# local development & testing
pytest==6.2.1
uvicorn==0.14.0
```
Run `pip install -r requirements.txt` .

Personally, I use [poetry](https://python-poetry.org/) for most of my dependecnie management these days but for this article 
 
Now let's setup the basic app in the `main.py` with routes for sending data and testing.

```python
#/app/main.py
from fastapi import FastAPI

from mangum import Mangum

app = FastAPI(title="Unicorn API")


@app.get("/")
def hello():
    return {"Hello": "World"}


@app.post("/unicorn")
def post_unicorn():
    return {}

handler = Mangum(app)
```
Let's start the server and make sure everything is up and running locally.
Run this in your terminal at the root of the project. `uvicorn app.main:app --reload`  this will the auto-reload after ever change you make and you could keep it running in the background as you make code changes.

Navigate in your browser to `http://127.0.0.1:8000 ` you should see your docs for your new API.
[PLACE IMAGE HERE]

## Section 2
Lets start writing tests for the endpoints and create our first data model so we can validate that our unicorn endpoint accepts only valid unicorns.

```python
#app/tests/test_main.py
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World!"}
```

Time to create our first model for our unicorn with its basic data model.

```python
#/app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from mangum import Mangum

app = FastAPI(title="Unicorn API")


class Unicorn(BaseModel):
    name: str
    rainbow: bool

@app.get("/")
def hello():
    return {"Hello": "World"}


@app.post("/unicorn")
def post_unicorn(unicorn: Unicorn):
    return {unicorn}

handler = Mangum(app)
```
Lets' go ahead and check out the API `http://127.0.0.1:8000 ` and we can see that the model has been introduced.
[PLACE IMAGE HERE]

Now, let's go ahead and create a proper testing harness that we will want to use later. let's put the TestClient into a `conftest.py` as we will be using it a lot and having the fixture autoload makes sense.

```python
#app/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def test_app():
    with TestClient(app) as test_client:
        yield test_client
```

Here, we imported Starlette's TestClient, which uses the requests library to make requests against the FastAPI app.
when the route is hit with a POST request, FastAPI will read the body of the request and validate the data:
If valid, the data will be available in the payload parameter. FastAPI also generates JSON Schema definitions that are then used to automatically generate the OpenAPI schema and the API documentation.
If invalid, an error is immediately returned.


 `http --json POST http://localhost:8004/unicorn/ data={ "name": "honey", "rainbow": True }`

## Section 3
install 
sls plugin install -n serverless-python-requirements

Serverless config file 

```yaml
service: serverless-fastapi

provider:
  name: aws
  runtime: python3.8
  logs:
    httpApi: true
  stage: ${env:STAGE}
  region: ${env:REGION}

functions:
  app:
    handler: app.main.handler
    events:
      - httpApi:
          path: '*'

custom:
  pythonRequirements:
    dockerizePip: non-linux

package:
  exclude:
    - node_modules/**
    - venv/**
    - .direnv/**
    - tests/**

plugins:
  - serverless-python-requirements
```


TODO: Deploy our service to aws

## Section 4
In this section we will create another data model and setup our tests for code coverage.
time to breakup our main.py a little bit and make it more manageble for future unicorn models.

The SummaryResponseSchema model inherits from the SummaryPayloadSchema model, adding an id field.


## Section 5
Since AWS Athena, just queries S3 data and we have validated it we can safely put the data into S3.
We will also create a service that 
In this section we will setup AWS athena and send our validated unicorn data into S3
we will also use the moto mocking library so that we can test everything locally without deploying our code to AWS.
This will allow for quicker development, and create a sense of ease before we start creating objects in s3.
## Section 6
In this section we will bring it all together and deploy our new unicorn data service.

## Conclusion
we covered a lot in this article. We created and tested an API with FastAPI, pytest, and serverless with api gateway using tests.
FastAPI is a powerful framework that makes it easy and a joy to develop RESTful APIs. With the power of pydantic you can  check the inbound data coming from other sources and even coerce the data when needed or do deeper type validation creating a more reliable data pipeline. Also, we stood up our datastore so that our analysts and datascience team could use our validated unicorn data for future machine learning models and insights.

### Further 
You would most definitly want to add authencation to your api - and it's fairly straightforward to add aws Cognito without too much effort.  

TODO more resources 
datamodel-codegen --input petstore.json --output model.py