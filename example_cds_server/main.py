import flask
import getpatientdata
import requests
import traceback
import pandas as pd
import json
import os
import pdb

IMAGE_SERVER = os.environ["PACS"]

app = flask.Flask(__name__)

@app.route("/")
def home():
    """
    If no path is provided, responds with how to get CDS data for a patient.
    """

    return flask_response("Get CDS using path \"/{patient_id}\".")

@app.route("/<patient_id>")
def get_cds(patient_id):
    """
    Responds in JSON format with patient data for the patient with medical record number
    `patient_id`, including the CDS recommendation.

    Patient data includes:
    - Basic patient information
    - Most recent 20 conditions
    - Most recent 20 Hemoglobin A1c observations
    - Most recent 20 medications
    - Most recent 20 image studies
    """
    if patient_id == "favicon.ico":
        return flask_response("No icon")

    try:
        print("getting patient with id " + str(patient_id))
        df_patient = getpatientdata.get_patient(patient_id)
        patient_json = df_to_json(df_patient)[0]

        patient_fhir_id = patient_json['fhir_id']

        try:
            print("getting conditions")
            df_conditions = getpatientdata.get_conditions(patient_fhir_id)
            patient_json['conditions'] = df_to_json(df_conditions)
        except Exception as error:
            patient_json['conditions'] = {'error':f'Error getting conditions for patient with id {patient_id}'}
            print(error)
            traceback.print_exc()

        try:
            print("getting observations")
            df_observations = getpatientdata.get_observations(patient_fhir_id)
            patient_json['observations'] = df_to_json(df_observations)
        except Exception as error:
            patient_json['observations'] = {'error':f'Error getting observations for patient with id {patient_id}'}
            print(error)
            traceback.print_exc()

        try:
            print("getting medications")
            df_medications = getpatientdata.get_medications(patient_fhir_id)
            patient_json['medications'] = df_to_json(df_medications)
        except Exception as error:
            patient_json['medications'] = {'error':f'Error getting medications for patient with id {patient_id}'}
            print(error)
            traceback.print_exc()

        try:
            print("getting image studies")
            df_image_studies = getpatientdata.get_imaging_studies(patient_fhir_id)
            df_encounters = getpatientdata.get_encounters(df_image_studies)
            df_pictures = get_pictures(patient_json['ehr_id'], df_image_studies)

            df_images_encounters_pictures = merge_imagestudies_encounters_pictures(df_image_studies, df_encounters, df_pictures)

            patient_json['imagery'] = df_to_json(df_images_encounters_pictures)
        except Exception as error:
            patient_json['imagery'] = {'error':f'Error getting imagery for patient with id {patient_id}'}
            print(error)
            traceback.print_exc()

        try:
            patient_json['cds'] = get_cds(df_patient, df_conditions, df_observations, df_medications, df_images_encounters_pictures)
        except Exception as error:
            patient_json['cds'] = {'error':f'Error getting CDS for patient with id {patient_id}'}
            print(error)
            traceback.print_exc()

        return flask_response(patient_json)

    except Exception as error:
        print(error)
        traceback.print_exc()
        return flask_response({'error':f'Error getting CDS data for patient with id {patient_id}'})

def df_to_json(df):
    """
    Converts a dataframe to a json object.
    """
    json_str = df.to_json(orient="records")
    return json.loads(json_str)

def get_cds(patient, conditions, observations, medications, images):
    """
    Creates an example CDS recommendation based on the Hemoglobin A1c level.
    If the patient's Hemoglobin A1c level is greater than 5.6%, they are labeled
    HIGH RISK.
    """
    if len(observations.index) > 0:
        value = observations.at[0, 'value']

        if value > 5.6:
            cds = f"The patient's Hemoglobin A1c level is {value}%, which is above the normal range of 4% and 5.6%. The patient is considered HIGH RISK."
        elif value <= 5.6 and value >= 4:
            cds = f"The patient's Hemoglobin A1c level is {value}%, which is within the normal range of 4% and 5.6%. The patient is considered LOW RISK."
        else:
            cds = f"The patient's Hemoglobin A1c level is {value}%, which is below the normal range of 4% and 5.6%."
    else:
        cds = "Hemoglobin A1c levels have not been reported for this patient. Unable to make CDS recommendation."

    return {'text':cds}


def get_pictures(patient_id, image_studies_df):
    """
    Retrieves an image and its metadata from the image server.
    """
    picture_ids = set(image_studies_df['picture_id'].to_list())
    responses = []
    for picture_id in picture_ids:
        image_url = f"{IMAGE_SERVER}/{patient_id}/{picture_id}"
        response = requests.get(image_url)
        if response.status_code == 200:
            # responds with a single level json object
            response_dict = response.json()
            # response_dict["id"] = picture_id
            responses.append(response_dict)

    images_df = pd.DataFrame.from_dict(responses)

    return images_df

def merge_imagestudies_encounters_pictures(image_studies, encounters, pictures):
    """
    Merges each image_study with its corresponding encounter and picture.
    Returns the merged dataframe.
    """
    image_encounters = pd.merge(image_studies, encounters,
                                how="left",
                                left_on="encounter_id", right_on="id",
                                suffixes=("_image", "_encounter"))

    image_encounters_pictures = pd.merge(image_encounters, pictures,
                                            how="left",
                                            left_on="picture_id", right_on="id",
                                            suffixes=(None, "_picture"))

    # clean up duplicate columns
    image_encounters_pictures = image_encounters_pictures.drop(['picture_id', 'encounter_id'], axis=1)
    # rename columns for clarity
    image_encounters_pictures = image_encounters_pictures.rename(
        columns = {'date': 'date_encounter',
                    'id': 'id_picture',
                    'type': 'type_picture',
                    'image': 'data_picture',
                    'subject_id': 'id_subject'}
                    )

    return image_encounters_pictures

def flask_response(content):
    """
    Creates a flask response that allows requests from external origins.
    """
    response = flask.make_response(content)

    # Allows requests from other origins. Necessary for most web browsers.
    # See https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS and
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin for
    # more information.
    response.headers['Access-Control-Allow-Origin'] = '*'

    return response
