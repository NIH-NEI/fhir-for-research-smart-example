FROM tiangolo/uwsgi-nginx-flask:python3.11
COPY ../requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY *.py /app

ADD https://github.com/NIH-NEI/fhir-for-research-workshop.git /app/workshop
