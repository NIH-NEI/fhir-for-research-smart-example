# Synthetic patients with retinoblastoma

This folder contains synthetic patient `.json` files and a script to add a retinoblastoma diagnosis to their records. To do this:

1. Load the `.json` files in this folder into a HAPI database using `load.sh` (see directions in the `README.md` file in the root of this repository).
2. Set the URL for the FHIR server in your shell's environment: for example, `export FHIR_SERVER="http://localhost:8080/hapi-fhir-jpaserver/fhir"
cd synthetic_data`.
3. Run `curl -s "$FHIR_SERVER/Patient" | jq -r '.entry[].resource.id'` (if you do not have `jq` installed, see <https://jqlang.github.io/jq/download/>). This will list the ids of the patients on the FHIR server. If your test server already has a large number of patients, you may need to use the FHIR API to search specifically for the patients in the `.json` files based on a value like their synthetic medical record number.
4. Pick the id of the patient you want to add the retinoblastoma condition to using the `PATIENT_ID` environment variable, and then add it using the provided script: for example, `PATIENT_ID=86 bash cds-retinoblastoma/add_retinoblastoma_condition.sh`.