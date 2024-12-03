from gcloud import storage
import os

def upload_file(local_file:str, project:str, bucket:str) -> str:
    client = storage.Client(project=project)
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(local_file)
    blob.upload_from_filename(local_file)

    return blob.public_url