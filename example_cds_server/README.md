To test without Docker, run:

    PACS=http://quartorunner.mitre.org:8082 FHIR_SERVER=http://quartorunner.mitre.org:8080/hapi-fhir-jpaserver/fhir python -m flask --app main run --port 8081
