from google.cloud import storage

def list_gcs_files(bucket_name):
    """Lists all the files in a GCS bucket."""
    # Create a storage client.
    storage_client = storage.Client()

    # Get the GCS bucket.
    bucket = storage_client.get_bucket(bucket_name)

    # List all objects in the bucket.
    blobs = bucket.list_blobs()

    # Print the names of the objects in the bucket.
    for blob in blobs:
        print(blob.name)

if __name__ == "__main__":
    # Set your GCS bucket name here.
    bucket_name = 'querent-test'
    list_gcs_files(bucket_name)
