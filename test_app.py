import unittest

from app import create_summary, extract_health_data, make_fhir_bundle


class HealthDataExtractionTests(unittest.TestCase):
    def test_extracts_report_values_medicines_dates_and_diagnosis(self):
        text = (
            "Report date: 2025-05-14\n"
            "Hemoglobin: 10.2 g/dL (12-16)\n"
            "Glucose: 90 mg/dL (70-100)\n"
            "Metformin 500 mg twice daily\n"
            "Diagnosis: Follow-up requested"
        )

        result = extract_health_data(text)

        self.assertEqual(result["dates"], ["2025-05-14"])
        self.assertEqual(
            [(item["name"], item["status"]) for item in result["observations"]],
            [("Hemoglobin", "Low"), ("Glucose", "Within provided range")],
        )
        self.assertEqual(result["medications"][0]["name"], "Metformin")
        self.assertEqual(result["diagnoses"], ["Follow-up requested"])

    def test_summary_only_compares_values_with_reported_ranges(self):
        data = extract_health_data("Vitamin D: 20 ng/mL\n")

        summary, disclaimer = create_summary(data, "English")

        self.assertIn("No structured lab values", summary)
        self.assertIn("not a diagnosis", disclaimer)

    def test_qualified_lab_values_are_not_treated_as_exact_numbers(self):
        data = extract_health_data("Marker: <5 mg/L (10-20)\n")
        record = {
            "name": "lab.pdf",
            "content_type": "application/pdf",
            "created_at": "2025-05-14T10:00:00+05:30",
            "health_data": data,
        }

        summary, _ = create_summary(data, "English")
        bundle = make_fhir_bundle("Demo Patient", "DEMO-001", [record])
        observation = bundle["entry"][2]["resource"]

        self.assertEqual(data["observations"][0]["status"], "Not compared (qualified result)")
        self.assertIn("not automatically compared", summary)
        self.assertEqual(observation["valueString"], "<5 mg/L")
        self.assertNotIn("valueQuantity", observation)

    def test_demo_bundle_contains_patient_documents_and_observations(self):
        data = extract_health_data("Hemoglobin: 10.2 g/dL (12-16)")
        records = [
            {
                "name": "lab.pdf",
                "content_type": "application/pdf",
                "created_at": "2025-05-14T10:00:00+05:30",
                "health_data": data,
            }
        ]

        bundle = make_fhir_bundle("Demo Patient", "DEMO-001", records)
        resource_types = [entry["resource"]["resourceType"] for entry in bundle["entry"]]

        self.assertEqual(bundle["resourceType"], "Bundle")
        self.assertEqual(resource_types, ["Patient", "DocumentReference", "Observation"])


if __name__ == "__main__":
    unittest.main()
