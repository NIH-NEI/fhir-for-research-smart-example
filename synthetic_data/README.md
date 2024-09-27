# Synthetic data - FHIR

This folder contains synthetic FHIR patient data in JSON format.

When loading into a FHIR server, first load the hospital and practitioner files before loading any of the patient files -- the patient files contain references to hospital (Organization) and Practitioner resource instances.

To facilitate this, the `load.sh` script will handle this automatically for the specified sub-folder. This is described in the README.md file in the root of this repository.