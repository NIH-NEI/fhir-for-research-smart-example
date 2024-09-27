#!/bin/bash

# Check if a folder name is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <folder_name>"
  exit 1
fi

FOLDER="$1"

# Check if the FHIR_SERVER environment variable is set
if [ -z "$FHIR_SERVER" ]; then
  echo "FHIR_SERVER environment variable is not set."
  exit 1
fi

# Function to POST JSON files to the FHIR server
post_files() {
  local pattern="$1"
  for file in "$FOLDER"/$pattern; do
    if [ -f "$file" ]; then
      echo "Posting $file to $FHIR_SERVER"
      curl -X POST -H "Content-Type: application/json" -d @"$file" "$FHIR_SERVER" >> out.log 2>&1
    fi
  done
}

# Post hospitalInformation JSON files
post_files "hospitalInformation*.json"
post_files "_hospitalInformation*.json"

# Post practitionerInformation JSON files
post_files "practitionerInformation*.json"
post_files "_practitionerInformation*.json"

# Post all other JSON files
for file in "$FOLDER"/*.json; do
  if [ -f "$file" ] && [[ ! "$file" =~ (hospitalInformation|_hospitalInformation|practitionerInformation|_practitionerInformation) ]]; then
    echo "Posting $file to $FHIR_SERVER"
    curl -X POST -H "Content-Type: application/json" -d @"$file" "$FHIR_SERVER" >> out.log 2>&1
  fi
done