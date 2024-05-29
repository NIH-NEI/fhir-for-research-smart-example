FROM smartonfhir/hapi-5:r4-empty

COPY ./database.tar.gz .
RUN tar -xzvf database.tar.gz
RUN mv h2.mv.db /usr/local/tomcat/target/database/