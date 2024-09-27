const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");

const app = express();
const port = 3000;

// enable cors to allow for use with sandbox.cds-hooks.org
app.use(cors());

// Middleware to parse JSON bodies
app.use(bodyParser.json());

app.get("/cds-services", (req, res) => {
  console.log("GET /cds-services");
  const discoveryResponse = {
    services: [
      {
        id: "retinoblastoma",
        hook: "patient-view",
        title: "Retinoblastoma CDS Service",
        description: "Provides decision support for retinoblastoma cases.",
        "prefetch": {
          "conditions": "Condition?patient={{context.patientId}}",
          "patient": "Patient/{{context.patientId}}"
        }
      },
    ],
  };

  res.json(discoveryResponse);
});

// Define the CDS Service endpoint for the patient-view hook
app.post("/cds-services/retinoblastoma", (req, res) => {
  console.log("POST /cds-services/retinoblastoma");
  const hook = req.body.hook;
  const patientId = req.body.context.patient;

  const prefetchData = req.body.prefetch;
  const patient = prefetchData.patient;
  const conditions = prefetchData.conditions['entry'] || [];

  // Ensure we're handling the correct hook
  if (hook !== "patient-view") {
    return res.status(400).json({error: "Unsupported hook"});
  }

  // Calculate patient's age in days
  const calculateAgeInDays = (dob) => {
    const birthDate = new Date(dob);
    const currentDate = new Date();
    const ageInMilliseconds = currentDate - birthDate;
    return ageInMilliseconds / (1000 * 60 * 60 * 24);
  };

  // Check if the patient is older than 30 days and younger than 18 years
  const ageInDays = calculateAgeInDays(patient['birthDate']);
  const isEligibleAge = ageInDays > 30 && ageInDays < (18 * 365);
  // NOTE: The birth dates of the patients in the synthetic data for testing are fixed, so if
  // `isEleigibleAge` is never `true` with the test data, you will need to adjust the age range
  // or hard-code it to `true`.

  // Filter conditions by SNOMED code for retinoblastoma
  const retinoblastomaCondition = conditions.find(condition =>
    condition.resource.code.coding.some(coding =>
      coding.system === 'http://snomed.info/sct' && coding.code === '19906005'
    )
  );

  // Check if the patient has retinoblastoma
  if (isEligibleAge && retinoblastomaCondition) {
    // Create the CDS Cards
    const cards = [
      {
        summary: "Enrollment Link",
        indicator: "info",
        detail:
          "This patient is diagnosed with retinoblastoma. Please consider referring them to the retinoblastoma recruitment registry if their parents or guardians are interested in being contacted about research opportunities.\n\nClick below to guide the patient’s family through the signing up for the Retinoblastoma Research Recruitment Registry.",
        source: {
          label: "Enrollment App",
        },
        links: [
          {
            label: "Enroll Patient →",
            url: "http://example.com",
            type: "absolute"
          }
        ]
      },
    ];

    // Respond with the CDS cards
    res.json({
      cards: cards,
    });
  } else {
    // No relevant CDS cards for patients without retinoblastoma
    res.json({cards: []});
  }
});

app.listen(port, () => {
  console.log(`CDS Service listening at http://localhost:${port}`);
});
