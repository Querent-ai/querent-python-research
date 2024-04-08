# # -----------------------Upload-------------------------------------

# import boto3

# # Your AWS credentials and the S3 bucket details
# aws_access_key_id = 'AKIA5ZFZH6CA6LDWIPV5'
# aws_secret_access_key = 'wdlGk5xuwEukpN6tigXV0S+CMJKdyQse2BgYjw9o'
# bucket_name = 'pstreamsbucket1'
# file_path = 'english.pdf'  # The local path to the file
# file_key = 'english.pdf'  # The key under which to store the file in S3

# # Create an S3 client
# s3 = boto3.client(
#     's3',
#     aws_access_key_id=aws_access_key_id,
#     aws_secret_access_key=aws_secret_access_key,
#     # If you're using a specific region, uncomment and set the region_name parameter
#     # region_name='your-bucket-region'
# )

# # Upload the file
# with open(file_path, 'rb') as file:
#     s3.upload_fileobj(
#         Fileobj=file,
#         Bucket=bucket_name,
#         Key=file_key,
#         ExtraArgs={'ContentType': 'application/pdf'}
#     )

# print(f"File {file_path} uploaded to {bucket_name}/{file_key}")


# # ----------------------------------Delete--------------------------------------
# import boto3

# # Your AWS access key ID and secret access key
# aws_access_key_id = 'AKIA5ZFZH6CA6LDWIPV5'
# aws_secret_access_key = 'wdlGk5xuwEukpN6tigXV0S+CMJKdyQse2BgYjw9o'

# # The name of the bucket and the key (file name) you want to delete
# bucket_name = 'pstreamsbucket1'
# file_key = 'sample123.pdf'

# # Create an S3 client
# s3 = boto3.client(
#     's3',
#     aws_access_key_id=aws_access_key_id,
#     aws_secret_access_key=aws_secret_access_key,
#     # If you're using a specific region, uncomment and set the region_name parameter
#     # region_name='your-bucket-region'
# )

# # Function to delete a file from the specified S3 bucket
# def delete_file(bucket, key):
#     try:
#         response = s3.delete_object(Bucket=bucket, Key=key)
#         print(f"File {key} deleted from bucket {bucket}.")
#     except Exception as e:
#         print(e)

# delete_file(bucket_name, file_key)


# ------------------------------------List --------------------------------------
# import boto3

# # Your AWS access key ID and secret access key
# aws_access_key_id = 'AKIA5ZFZH6CA6LDWIPV5'
# aws_secret_access_key = 'wdlGk5xuwEukpN6tigXV0S+CMJKdyQse2BgYjw9o'

# # The name of the bucket you want to list files from
# bucket_name = 'pstreamsbucket1'

# # Create an S3 client
# s3 = boto3.client(
#     's3',
#     aws_access_key_id=aws_access_key_id,
#     aws_secret_access_key=aws_secret_access_key,
#     # If you're using a specific region, uncomment and set the region_name parameter
#     # region_name='your-bucket-region'
# )

# # List files in the specified S3 bucket
# def list_files(bucket):
#     try:
#         response = s3.list_objects_v2(Bucket=bucket)
#         if 'Contents' in response:
#             for file in response['Contents']:
#                 print(file['Key'])
#         else:
#             print("No files found.")
#     except Exception as e:
#         print(e)

# list_files(bucket_name)
