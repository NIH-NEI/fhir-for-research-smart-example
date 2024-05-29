FROM node:22
RUN mkdir site
COPY *.html fhirpath.js /site/
RUN npm install -g http-server
CMD ["http-server", "/site", "--cors"]
