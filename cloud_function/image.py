import os
import tempfile

from google.cloud import storage, vision
from wand.image import Image

storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()

  
def thumbnail_images(data):
    file_data = data

    file_name = file_data["name"]
    bucket_name = file_data["bucket"]
    
    print(f"Bucket Name {bucket_name}.")
    bucket = storage_client.get_bucket(bucket_name)
    print(f"Bucket  {bucket}.")
    print(f"Filename {data['name']}.")
    blob = bucket.blob(data["name"])
    #blob.download_to_filename("test.jeg")
    
   # blob = storage_client.get_bucket(bucket_name).get_blob(file_name)
    print(f"Blob {blob}.")
    blob_uri = f"gs://{bucket_name}/{data['name']}"
    print(f"Blob URL {blob_uri}.")
    blob_source = vision.Image(source=vision.ImageSource(image_uri=blob_uri))

    # Ignore already-blurred files
    if file_name.startswith("thumbnail-"):
        print(f"The image {data['name']} is already thumbnail.")
        return

    print(f"Analyzing {data['name']}.")

    result = vision_client.safe_search_detection(image=blob_source)
    detected = result.safe_search_annotation

    # Process image
    return __thumbnail(blob)
  
    #if detected.adult == 5 or detected.violence == 5:
 #       print(f"The image {file_name} was detected as inappropriate.")
   #     return __blur_image(blob)
  #  else:
  #      print(f"The image {file_name} was detected as OK.")

def __thumbnail(current_blob):
    print(f"Inside thumb function {current_blob}.")
    file_name = current_blob.name
    _, temp_local_filename = tempfile.mkstemp()

    # Download file from bucket.
    current_blob.download_to_filename(temp_local_filename)
    print(f"Image {file_name} was downloaded to {temp_local_filename}.")

    # Blur the image using ImageMagick.
    with Image(filename=temp_local_filename) as image:
        image.resize(100)
        image.save(filename=temp_local_filename)
    
    print(f"Image {file_name} was thumbnail.")
    
    

    # Upload result to a second bucket, to avoid re-triggering the function.
    # You could instead re-upload it to the same bucket + tell your function
    # to ignore files marked as blurred (e.g. those with a "blurred" prefix)
    blur_bucket_name = os.getenv("BLURRED_BUCKET_NAME")
    blur_bucket = storage_client.bucket(blur_bucket_name)
    new_blob = blur_bucket.blob(file_name)
    new_blob.upload_from_filename(temp_local_filename)
    print(f"thumbnail image uploaded to: gs://{blur_bucket_name}/{file_name}")

    # Delete the temporary file.
    os.remove(temp_local_filename)
    
