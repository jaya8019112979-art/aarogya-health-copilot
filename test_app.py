import unittest

from app import (
    answer_record_question,
    compare_observations,
    create_downloadable_summary,
    create_summary,
    explain_medical_term,
    extract_health_data,
    make_fhir_bundle,
)


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

    def test_comparison_only_returns_tests_present_in_multiple_records(self):
        records = [
            {
                "name": "first report",
                "record_date": "2025-05-14",
                "health_data": extract_health_data(
                    "Hemoglobin: 10.2 g/dL (12-16)\nGlucose: 90 mg/dL (70-100)"
                ),
            },
            {
                "name": "second report",
                "record_date": "2025-06-14",
                "health_data": extract_health_data(
                    "Hemoglobin: 11.5 g/dL (12-16)\nPlatelets: 250 10^9/L (150-400)"
                ),
            },
        ]

        result = compare_observations(records)

        self.assertEqual(len(result), 2)
        self.assertEqual({row["Test"] for row in result}, {"Hemoglobin"})
        self.assertEqual({row["Record"] for row in result}, {"first report", "second report"})

    def test_report_questions_only_return_source_backed_details(self):
        record = {
            "name": "lab report",
            "record_date": "2025-05-14",
            "category": "Lab report",
            "text": "Hemoglobin: 10.2 g/dL (12-16)\nReport date: 2025-05-14",
            "health_data": extract_health_data(
                "Hemoglobin: 10.2 g/dL (12-16)\nReport date: 2025-05-14"
            ),
        }

        answer = answer_record_question("What is my hemoglobin?", record)
        unsupported = answer_record_question("What treatment should I take?", record)

        self.assertIn("10.2 g/dL", answer)
        self.assertIn("Low", answer)
        self.assertIn("couldn't find", unsupported)
        self.assertIn("does not generate medical advice", unsupported)

    def test_medical_term_glossary_supports_english_and_telugu(self):
        self.assertIn("red blood cells", explain_medical_term("Anemia"))
        self.assertTrue(explain_medical_term("hemoglobin", "Telugu"))
        self.assertIsNone(explain_medical_term("unknown term"))

    def test_summary_download_includes_record_context_and_safety_note(self):
        record = {
            "name": "lab report",
            "record_date": "2025-05-14",
            "category": "Lab report",
            "health_data": extract_health_data("Hemoglobin: 10.2 g/dL (12-16)"),
        }

        output = create_downloadable_summary(record, "English")

        self.assertIn("Source: lab report", output)
        self.assertIn("Category: Lab report", output)
        self.assertIn("not a diagnosis", output)


if __name__ == "__main__":
    unittest.main()
