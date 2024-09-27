# CDS Hook Examples

This is not part of the `compose.yaml` file because it was not used in the May 2024 workshop. It was added to this repository in September 2024 for potential use in the future, and to support self-directed use.

## Running the CDS Hook service example

```bash
cd example_cds_hook_service
docker build -t example-cds-hooks-service-image .
docker run -it -p 3000:3000 -v ${PWD}:/usr/src/app example-cds-hooks-service-image
```

This will mount this folder in the Docker container, and the Node server will automatically restart when app.js is changed.

To background the server once it is running via docker, type `ctrl-p` and then `ctrl-q`.

To kill the server, run `docker ps --filter "ancestor=example-cds-hooks-service-image" -q | xargs docker kill`.

## HAPI FHIR server

In order for the example CDS Hooks to work, patients that meet the CDS Hook criteria are necessary. These are available via a pre-populated database for the HAPI FHIR server. To run this:

1. `mkdir hapi`
2. Unzip the `synthetic_data/cds-hapi.zip` file in the `hapi/` folder to create `hapi/h2.mv.db
3. Run the following Docker command to start the HAPI server using this database: `docker run -it -p 8080:8080 -v ${PWD}/hapi:/usr/local/tomcat/target/database smartonfhir/hapi-5:r4-empty`

## Testing the CDS Hooks examples

Navigate to the following URL: <https://sandbox.cds-hooks.org/?fhirServiceUrl=http%3A//localhost%3A8080/hapi-fhir-jpaserver/fhir/&serviceDiscoveryURL=http%3A//localhost%3A3000/cds-services&patientId=86>.

Assuming that HAPI is running on `localhost:8080` and the example CDS Hooks service is running on `localhost:3000`, you should see the record for a synthetic patient named `Chauncey770 Houston994 Hegmann834` with a retinoblastoma CDS Hook card.

You can modify the `patientId=XX` parameter in the URL to change the ID of the patient.

The following patient ids can be used to test, assuming you are running the provided HAPI database:

- `patientId=86`: retinoblastoma condition
- `patientId=314`: retinoblastoma condition
- `patientId=642`: no retinoblastoma condition