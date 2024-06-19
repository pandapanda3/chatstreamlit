import pymysql
import boto3
from botocore.exceptions import ClientError
import json


# get the information of mysql and openai key
def get_secret():

    secret_name = "chatstreamlit/mysql"
    region_name = "eu-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    secret_dict = json.loads(secret)
    return secret_dict

# connect to the database
def get_connection():
    secret_dict = get_secret()
    return pymysql.connect(
        host=secret_dict['host'],
        user=secret_dict['username'],
        password=secret_dict['password'],
        database=secret_dict['dbInstanceIdentifier'],
        port=secret_dict['port'],
        charset='utf8mb4'
    )
   


