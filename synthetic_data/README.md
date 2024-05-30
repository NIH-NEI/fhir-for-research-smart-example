# Synthetic data - FHIR

This folder contains synthetic FHIR patient data in JSON format. When loading into a FHIR server, first load `_hospitalInformation1714415605031.json` and `_practitionerInformation1714415605031.json` before loading any of the patient files -- the patient files contain references to hospital (Organization) and Practitioner resource instances.