"""

Extract Images from FHIR
========================

This script extracts the base64-encoded images contained in the FHIR Bundles in the `fhir/` folder,
and saves them as `.jpg` files in the `images/` folder.

Run with:

    pipenv exec python extract_images_from_fhir.py

"""

import base64
import json
import os
import pathlib
import re

from fhir.resources.bundle import Bundle
from fhirpathpy import evaluate


def open_file(filename):
    f = open(filename)
    data = json.load(f)
    return data


def write_image(image_string, image_name, image_path):
    image_data = base64.b64decode(image_string)
    filename = os.path.join(image_path, image_name)
    with open(filename, "wb") as f:
        f.write(image_data)

def main():
    path = pathlib.Path(__file__).parent.resolve()

    for bundle_filename in os.listdir(os.path.join(path, "..", "synthetic_data")):
        if re.match(r"^[A-Z].*\.json$", bundle_filename):

            data = open_file(os.path.join(path, "..", "synthetic_data", bundle_filename))

            media = evaluate(
                data, "Bundle.entry.resource.where(resourceType = 'Media')"
            )
            for i, m in enumerate(media):
                media_id = evaluate(m, "Media.partOf.reference")[0]
                media_id = media_id[media_id.rfind(":") + 1 :]

                # Find the ImagingStudy referenced here
                fpath = f"Bundle.entry.resource.where(resourceType = 'ImagingStudy').where(id = '{media_id}')"
                imaging_study = evaluate(data, fpath)
                imaging_id = evaluate(imaging_study, 'ImagingStudy.identifier.value')[0]
                imaging_id = imaging_id[imaging_id.rfind(":") + 1 :]

                write_image(
                    m["content"]["data"],
                    bundle_filename.replace(".json", f"_{imaging_id}.jpg"),
                    os.path.join(path, 'images'),
                )

if __name__ == "__main__":
    main()
