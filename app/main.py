from fastapi import FastAPI
from mangum import Mangum
from .models import UnicornPayloadSchema
import boto3
from os import environ

app = FastAPI(title="Unicorn API")


@app.get("/")
def hello():
    return {"Hello": "World"}


@app.post("/unicorn")
def post_unicorn(unicorn: UnicornPayloadSchema):
    #return UUID or some sort of unique id
    r = s3_write(unicorn.json())
    return r


@app.get("/unicorn/{id}")
def get_unicorn(uid: str):
    # create athena query and return data set
    pass


# this is where we write data to s3 for athena
def s3_write(data ) -> int:
    s3 = boto3.client('s3')
    bucket_name = environ.get("BUCKET_NAME", "unicorn")
    # Add a file to s3 Object Store
    r = s3.put_object(Bucket=bucket_name, Key='test', Body=data)
    print(r)
    return r


handler = Mangum(app)

