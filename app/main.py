from fastapi import FastAPI
from mangum import Mangum
from .models import UnicornPayloadSchema
import json
import boto3
import os


app = FastAPI(title="Unicorn API")


@app.get("/")
def hello():
    return {"Hello": "World"}


@app.post("/unicorn")
def post_unicorn(unicorn: UnicornPayloadSchema):
    #return UUID or some sort of unique id
    return unicorn


@app.get("/unicorn/{id}")
def get_unicorn(uid: str):
    # create athena query and return data set
    pass


# this is where I'll write data to s3 for athena
def s3_write(data: dict) -> int:
    s3 = boto3.client('s3')
    bucket_name = os.environ['BUCKET_NAME']
    # Add a file to s3 Object Store
    response = s3.put_object(
        Bucket=bucket_name,
        Key='Object Name',
        Body=json.dump(data),
        ACL='onpublic-read'
        )
    return response


handler = Mangum(app)

