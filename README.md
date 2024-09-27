# SMART on FHIR for Eye Research Example

To run, you will need `docker` and `docker compose` installed on a `AMD64` host. Then run:

    docker compose up -d

To see the logs, run:

    docker compose logs --follow

To shut down, run:

    docker compose down

## Components

Running `docker compose up` will start the following components

| Component                                                       | Port   |
| --------------------------------------------------------------- | ------ |
| HAPI FHIR server with pre-loaded synthetic eye data             | `8080` |
| EHR Launch simulator                                            | `8010` |
| Sample Clinical Decision Support (CDS) back-end server (Python) | `8081` |
| Sample [PACS] server                                            | `8082` |
| SMART on FHIR app user interface                                | `3000` |

[PACS]: https://en.wikipedia.org/wiki/Picture_archiving_and_communication_system

## Updating HAPI Data

The HAPI FHIR server is pre-loaded with synthetic eye data. If you wish to update the data, follow the following steps:

1. Create a local folder to store the HAPI database:

        mkdir empty-hapi-db

2. Start a separate instance of the HAPI FHIR server ([details here](https://github.com/smart-on-fhir/hapi)), mounting your local folder to the location of the container's HAPI server database:

        docker run -it -p 8080:8080 -v ${PWD}/empty-hapi-db:/usr/local/tomcat/target/database smartonfhir/hapi-5:r4-empty

    It will take a few minutes for the server to start up. When it does, you should be able to see a generic Apache Tomcat landing page at <http://localhost:8080>.

3. Run the `synthetic_data/load.sh` script to load in all the JSON files from the specified folder. For example, to load the data in `synthetic_data/2024-05-workshop`, run this command:

        cd synthetic_data
        FHIR_SERVER="http://localhost:8080/hapi-fhir-jpaserver/fhir" bash load.sh 2024-05-workshop

    This command will take a while to run because the FHIR bundles are quite large. You can watch progress in the Terminal window where the `docker` command above is running -- you should see output lines like `Beginning batch with 774 resources` and `Batch completed in 82339ms` as each JSON file is POSTed to the server.

    You can also run `tail -f out.log` in a separate window to watch the progress of `load.sh`.

    The `synthetic_data/out.log` file will show the FHIR resources returned by the HAPI server with their IDs. You can use this to do a test query to make sure some of the resources are loaded:

        curl http://localhost:8080/hapi-fhir-jpaserver/fhir/Patient/some-id-here

4. After all the desired FHIR resources are loaded into HAPI, close out the `docker run` process with `ctrl-c` and zip up the database file in the `empty-hapi-db/` folder you made in step 1:

        cd /path/to/empty-hapi-db
        tar -czvf database.tar.gz h2.mv.db

4. Replace `hapi/database.tar.gz` with the file you created in Step 4.

----

## License

Copyright 2024 The MITRE Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

----

MITRE: Approved for Public Release / Case #24-0169
