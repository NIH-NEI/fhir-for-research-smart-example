#!/bin/bash

# Check if environment variables are set
if [[ -z "$FHIR_SERVER" || -z "$PATIENT_ID" ]]; then
  echo "FHIR_SERVER and PATIENT_ID environment variables must be set."
  exit 1
fi

# Get the most recent encounter for the patient
echo "Fetching the most recent encounter for patient ID: $PATIENT_ID"
response=$(curl -s "$FHIR_SERVER/Encounter?patient=$PATIENT_ID&_sort=-date&_count=1")

# Extract the encounter ID
encounter_id=$(echo "$response" | jq -r '.entry[0].resource.id')

if [[ -z "$encounter_id" || "$encounter_id" == "null" ]]; then
  echo "No encounters found for patient ID: $PATIENT_ID"
  exit 1
fi

echo "Most recent encounter ID: $encounter_id"

# Get the current date and time
current_datetime=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Create a Condition resource
condition_json=$(cat <<EOF
{
  "resourceType": "Condition",
  "meta": {
    "profile": [ "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition-encounter-diagnosis" ]
  },
  "clinicalStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
        "code": "active"
      }
    ]
  },
  "verificationStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
        "code": "confirmed"
      }
    ]
  },
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/condition-category",
          "code": "encounter-diagnosis",
          "display": "Encounter Diagnosis"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "19906005",
        "display": "Retinoblastoma (morphologic abnormality)"
      }
    ],
    "text": "Retinoblastoma"
  },
  "subject": {
    "reference": "Patient/$PATIENT_ID"
  },
  "encounter": {
    "reference": "Encounter/$encounter_id"
  },
  "onsetDateTime": "$current_datetime",
  "recordedDate": "$current_datetime"
}
EOF
)

# Post the Condition to the FHIR server
echo "Posting Condition to FHIR server..."
post_response=$(curl -s -X POST -H "Content-Type: application/fhir+json" -d "$condition_json" "$FHIR_SERVER/Condition")

# Check if the POST was successful
if echo "$post_response" | grep -q '"resourceType":"Condition"'; then
  echo "Condition successfully posted."
else
  echo "Failed to post Condition."
  echo "Response: $post_response"
fi
