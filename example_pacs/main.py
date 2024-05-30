from flask import Flask
import json
import mimetypes
import os
import base64

IMAGE_DIR = "images"

app = Flask(__name__)

@app.route("/")
def home():
    """
    If not path is specified, responds with how to get image data.
    """
    return "Get images using the path \"/{patient_id}/{image_id}\"."

@app.route("/<patient_id>/<image_id>")
def show_image(patient_id, image_id):
    """
    Retrieves the imagery data for the given `patient_id` and `image_id`.
    Responds in JSON format with the following information:
    - Image ID
    - Patient ID
    - MIME Type
    - Base64 encoding of the image
    """
    try:
        image_url = get_image_url(patient_id, image_id)
        encoded_image = get_encoded_image(image_url)
        mime_type = mimetypes.guess_type(image_url)[0]
        image_obj = {
            'id':image_id,
            'type':mime_type,
            'image':str(encoded_image),
            'subject_id':patient_id
        }

        return json.dumps(image_obj, indent=2)
    except Exception as e:
        print(e)
        errorStr = f"Patient with id '{patient_id}' or image with id '{image_id}' does not exist."
        return json.dumps({"error": errorStr}, indent=2)


def get_image_url(patient_id, image_id):
    """
    Returns the path to the image that corresponds to the `patient_id` and `image_id`.
    """
    files = os.listdir(IMAGE_DIR)
    for file in files:
        if patient_id in file and image_id in file:
            file_path = os.path.join(IMAGE_DIR, file)
            return file_path

    raise Exception(f"Could not find imagery with id {image_id}")

def get_encoded_image(image_url):
    """
    Returns a base64 encoding of the image.
    """
    with open(image_url, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()
