import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, BotoCoreError

def initialize_s3_resource():
    try:
        s3_resource = boto3.resource('s3',
                                     aws_access_key_id='YOUR_ACCESS_KEY',
                                     aws_secret_access_key='YOUR_SECRET_KEY',
                                     region_name='YOUR_REGION')
        return s3_resource
    except (PartialCredentialsError, BotoCoreError) as e:
        print(f"Error initializing S3 resource: {e}")
        return None

def list_objects(bucket_name):
    try:
        s3_resource = initialize_s3_resource()
        if s3_resource is None:
            return []

        bucket = s3_resource.Bucket(bucket_name)
        objects = list(bucket.objects.all())
        return objects
    except BotoCoreError as e:
        print(f"Error listing objects: {e}")
        return []

def download_file(bucket_name, s3_key, local_path):
    try:
        s3_resource = initialize_s3_resource()
        if s3_resource is None:
            return False

        s3_resource.Bucket(bucket_name).download_file(s3_key, local_path)
        return True
    except (BotoCoreError, NoCredentialsError) as e:
        print(f"Error downloading file: {e}")
        return False

def upload_file(bucket_name, s3_key, local_path):
    try:
        s3_resource = initialize_s3_resource()
        if s3_resource is None:
            return False

        s3_resource.Bucket(bucket_name).upload_file(local_path, s3_key)
        return True
    except (BotoCoreError, NoCredentialsError) as e:
        print(f"Error uploading file: {e}")
        return False

def delete_object(bucket_name, s3_key):
    try:
        s3_resource = initialize_s3_resource()
        if s3_resource is None:
            return False

        s3_resource.Object(bucket_name, s3_key).delete()
        return True
    except (BotoCoreError, NoCredentialsError) as e:
        print(f"Error deleting object: {e}")
        return False

# Usage
bucket_name = 'your-s3-bucket-name'
object_list = list_objects(bucket_name)
for obj in object_list:
    print(obj.key)

# Remember to replace 'YOUR_ACCESS_KEY', 'YOUR_SECRET_KEY', and 'YOUR_REGION' with your actual credentials.
