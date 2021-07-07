import pytest
import boto3
from moto import mock_s3
from app.main import s3_write
import json


@mock_s3
def test_s3_put():
	conn = boto3.resource('s3', region_name='us-east-1')
	conn.create_bucket(Bucket='unicorn')
	test_obj = json.dumps({"name": "honey", "rainbow": True})
	s3_write(test_obj)
	body = conn.Object('unicorn', 'test').get()['Body'].read().decode("utf-8")

	assert body == json.dumps({"name": "honey", "rainbow": True})
