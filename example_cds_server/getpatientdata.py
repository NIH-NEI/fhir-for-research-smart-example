import pandas as pd
import uuid

import os

FHIR_SERVER = os.environ["FHIR_SERVER"]

from fhir_pyrate import Pirate

# API to query FHIR servers and convert FHIR bundles into dataframes.
search = Pirate(
    auth=None, # the demo fhir server does not require authentication
    base_url=FHIR_SERVER,
    print_request_url=True, # If set to true, you will see all requests
)

def get_patient(patient_id):
    """
    Retrieves the patient with id `patient_id` and places the following information
    into a dataframe:
    - Given name
    - Family name
    - Birth date
    - FHIR ID
    - EHR ID
    """
    df_patient = search.steal_bundles_to_dataframe(
        resource_type="Patient",
        request_params={"identifier":patient_id},
        fhir_paths=[
            ("given_name", "Patient.name.where(use = 'official').given"),
            ("family_name", "Patient.name.where(use = 'official').family"),
            ("birth_date", "Patient.birthDate"),
            ("fhir_id", "Patient.id"),
            ("ehr_id", "Patient.identifier.where(type.coding.system = 'http://terminology.hl7.org/CodeSystem/v2-0203' and type.coding.code = 'MR').value")
        ]
    )
    return df_patient

def get_conditions(patient_id):
    """
    Retrieves the most recent conditions for the patient with id `patient_id`
    and places the following information into a dataframe:
    - Coding
      - System
      - Code
      - Display
    - ID
    - Onset date
    """
    df_conditions = search.steal_bundles_to_dataframe(
        resource_type="Condition",
        request_params={
            "subject":patient_id,
            "_sort":"-onset-date"
        },
        fhir_paths=[
            ("coding_system", "Condition.code.coding.system"),
            ("coding_code", "Condition.code.coding.code"),
            ("coding_display", "Condition.code.coding.display"),
            ("id", "Condition.id"),
            ("date", "Condition.onsetDateTime")
        ],
        num_pages=1
    )

    return df_conditions

def get_observations(patient_id):
    """
    Retrieves the most recent Hemoglobin A1c/Hemoglobin.total in Blood observations
    for the patient with id `patient_id` and places the following information into
    a dataframe:
    - Coding
      - System
      - Code
      - Display
    - ID
    - Effective Date
    - Value
    """
    # only retrieving "Hemoglobin A1c/Hemoglobin.total in Blood" (code: 4548-4) observations
    # to limit number of observations returned.
    df_observations = search.steal_bundles_to_dataframe(
        resource_type="Observation",
        request_params={
            "subject":patient_id,
            "_sort":"-date",
            "code":"4548-4"
        },
        fhir_paths=[
            ("coding_system", "Observation.code.coding.system"),
            ("coding_code", "Observation.code.coding.code"),
            ("coding_display", "Observation.code.coding.display"),
            ("id", "Observation.id"),
            ("date", "Observation.effectiveDateTime"),
            ("value", "Observation.valueQuantity.value")
        ],
        num_pages=1
    )

    return df_observations

def get_medications(patient_id):
    """
    Retrieves the most recent medications for the patient with id `patient_id`
    and places the following information into a dataframe:
    - Coding
      - System
      - Code
      - Display
    - ID
    - Authored on date
    """
    df_medications = search.steal_bundles_to_dataframe(
        resource_type="MedicationRequest",
        request_params={
            "subject":patient_id,
            "_sort":"-authoredon"
        },
        fhir_paths=[
            ("coding_system", "MedicationRequest.medicationCodeableConcept.coding.system"),
            ("coding_code", "MedicationRequest.medicationCodeableConcept.coding.code"),
            ("coding_display", "MedicationRequest.medicationCodeableConcept.coding.display"),
            ("id", "MedicationRequest.id"),
            ("date", "MedicationRequest.authoredOn"),
        ],
        num_pages=1
    )

    return df_medications

def get_imaging_studies(patient_id):
    """
    Retrieves the most recent imaging studies for the patient with id `patient_id`
    and places the following information into a dataframe:
    - Coding
      - System
      - Code
      - Display
    - ID
    - Encounter ID
    - Image ID
    """
    df_imaging_studies = search.steal_bundles_to_dataframe(
        resource_type="ImagingStudy",
        request_params={
            "subject":patient_id,
            "_sort":"-started"
        },
        fhir_paths=[
            ("coding_system", "ImagingStudy.procedureCode.coding.system"),
            ("coding_code", "ImagingStudy.procedureCode.coding.code"),
            ("coding_display", "ImagingStudy.procedureCode.coding.display"),
            ("id", "ImagingStudy.id"),
            ("picture_id", "ImagingStudy.identifier.value"),
            ("encounter_id", "ImagingStudy.encounter.reference"),
        ],
        num_pages=1
    )

    df_imaging_studies['encounter_id'] = df_imaging_studies['encounter_id'].apply(
        lambda a: parse_encounter_id(a)
    )
    df_imaging_studies['picture_id'] = df_imaging_studies['picture_id'].apply(
       lambda a: parse_picture_id(a)
    )

    return df_imaging_studies

def get_encounters(df_image_studies):
  """
    Retrieves the encounters associated with each image study in the dataframe
    using the image study's `encounter_id`, places the following information into
    a dataframe:
    - Coding
      - System
      - Code
      - Display
    - ID
    - Start date
  """
  encounter_ids = set(df_image_studies['encounter_id'].to_list())
  encounters = []

  for encounter_id in encounter_ids:
    encounter = search.steal_bundles_to_dataframe(
        resource_type="Encounter",
        request_params={
            "_id":encounter_id
        },
        fhir_paths=[
            ("coding_system", "Encounter.type.coding.system"),
            ("coding_code", "Encounter.type.coding.code"),
            ("coding_display", "Encounter.type.coding.display"),
            ("id", "Encounter.id"),
            ("date", "Encounter.period.start"),
        ],
    )
    encounters.append(encounter)

  df_encounters = pd.concat(encounters, ignore_index=True)
  return df_encounters

def parse_encounter_id(e_id):
  # some references are formatted like 'Encounter/<id>'. This gets whatever trails the last '/' if it exists.
  e_id = e_id.rsplit('/', 1)[-1]
  try:
    e_id = uuid.UUID(e_id) # this gets rid of the urn namespace if it exists
  except:
    pass # encounter id is not a uuid so do nothing
  return str(e_id)

def parse_picture_id(p_id):
  # image id formatted like urn:oid:asdf. Getting rid of the urn:oid: substring
  p_id = p_id[p_id.rfind(':')+1:]
  return p_id
