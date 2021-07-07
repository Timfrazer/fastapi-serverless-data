import pytest
from fastapi.testclient import TestClient
from app.main import app
from moto import mock_s3
import boto3
import os


@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def aws_credentials():
    # Mock AWS Credentials for moto
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def s3_client(aws_credentials):
    with mock_s3():
        conn = boto3.client("s3", region_name="us-east-1")
        yield conn