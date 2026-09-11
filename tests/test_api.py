"""
Pashu Suraksha - Automated Test Suite
Verifies API endpoints, triage accuracy, geospatial calculations, IVR flow, and database integrity.
"""

import sys
import os
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from core.triage_engine import assess_symptoms
from core.weather_risk import calculate_environmental_risk

class TestPashuSuraksha(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_01_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "ONLINE")

    def test_02_triage_fmd(self):
        res = self.client.post("/api/triage/assess", json={
            "species": "Cattle",
            "symptoms": ["oral_vesicles", "hoof_lesions", "excessive_salivation"],
            "has_fever": True,
            "affected_count": 3
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["top_diagnosis"]["code"], "FMD")
        self.assertGreater(data["top_diagnosis"]["confidence"], 70)
        self.assertEqual(data["urgency"], "CRITICAL")
        self.assertTrue(data["trigger_containment_ring"])

    def test_03_triage_anthrax_biohazard(self):
        res = self.client.post("/api/triage/assess", json={
            "species": "Cattle",
            "symptoms": ["sudden_unexplained_death", "unclotted_dark_blood"],
            "has_fever": False,
            "mortality_count": 1
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["top_diagnosis"]["code"], "ANTHRAX")
        self.assertTrue(data["is_zoonotic"])
        self.assertIn("EXTREME DANGER", data["biohazard_alert"])

    def test_04_animal_ehr(self):
        res = self.client.get("/api/animals/100982347101")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["tag_number"], "100982347101")
        self.assertIn("vaccinations", data)
        self.assertIn("treatments", data)

    def test_05_ivr_flow(self):
        # Step 1: Start
        r1 = self.client.post("/api/ivr/process", json={"step": "START"})
        self.assertEqual(r1.status_code, 200)
        d1 = r1.get_json()
        self.assertEqual(d1["next_step"], "SPECIES_SELECTION")

        # Step 2: Select Cattle (1)
        r2 = self.client.post("/api/ivr/process", json={"step": "SPECIES_SELECTION", "digits": "1"})
        self.assertEqual(r2.status_code, 200)
        d2 = r2.get_json()
        self.assertEqual(d2["selected_species"], "Cattle")

        # Step 3: Select Blisters / Salivation (1)
        r3 = self.client.post("/api/ivr/process", json={
            "step": "SYMPTOM_SELECTION",
            "digits": "1",
            "selected_species": "Cattle",
            "caller_phone": "9998887776"
        })
        self.assertEqual(r3.status_code, 200)
        d3 = r3.get_json()
        self.assertEqual(d3["next_step"], "COMPLETED")
        self.assertEqual(d3["triage_code"], "FMD")

    def test_06_weather_risk(self):
        res = self.client.get("/api/weather-risk")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreater(len(data), 0)
        self.assertIn("meteorological_conditions", data[0])
        self.assertIn("indices", data[0])

    def test_07_multilingual_advisories(self):
        res = self.client.get("/api/advisories/preview?alert_type=FMD_OUTBREAK&lang=hi")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("खुरपका", data["title"])
        self.assertIn("लाल दवा", data["voice_script"])

    def test_08_dashboard_stats(self):
        res = self.client.get("/api/stats/dashboard")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("metrics", data)
        self.assertIn("disease_breakdown", data)

    def test_09_auth_login_credentials(self):
        res = self.client.post("/api/auth/login", json={
            "username": "farmer",
            "password": "farm123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["role"], "FARMER")
        self.assertEqual(data["user"]["full_name"], "Ramcharan Yadav")

    def test_10_auth_role_quick_switch(self):
        res = self.client.post("/api/auth/login", json={"role": "DVO"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["role"], "DVO")
        self.assertEqual(data["user"]["username"], "dvo_hisar")

    def test_11_auth_otp_flow(self):
        # Step 1: Send OTP
        r1 = self.client.post("/api/auth/otp/send", json={"phone": "9876543210"})
        self.assertEqual(r1.status_code, 200)
        d1 = r1.get_json()
        self.assertTrue(d1["success"])
        self.assertEqual(d1["simulated_otp"], "1962")

        # Step 2: Verify OTP
        r2 = self.client.post("/api/auth/otp/verify", json={"phone": "9876543210", "otp": "1962"})
        self.assertEqual(r2.status_code, 200)
        d2 = r2.get_json()
        self.assertTrue(d2["success"])
        self.assertEqual(d2["user"]["phone"], "9876543210")

    def test_12_auth_logout(self):
        res = self.client.post("/api/auth/logout")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])

    def test_13_image_diagnosis(self):
        # 1. Test Presets list
        res_presets = self.client.get("/api/image-diagnosis/presets")
        self.assertEqual(res_presets.status_code, 200)
        presets_data = res_presets.get_json()
        self.assertIsInstance(presets_data, list)
        self.assertGreaterEqual(len(presets_data), 5)

        # 2. Test Image Diagnostic analysis on LSD sample
        res_diag = self.client.post("/api/image-diagnosis", json={
            "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAAEBAREA/8QAFQABAQAAAAAAAAAAAAAAAAAAAAf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAE/AH//2Q==",
            "filename": "lsd_cow_skin_nodule.jpg",
            "hint": "lumpy skin nodule",
            "species": "Cattle"
        })
        self.assertEqual(res_diag.status_code, 200)
        diag_data = res_diag.get_json()
        self.assertTrue(diag_data["success"])
        self.assertEqual(diag_data["disease_code"], "LSD")
        self.assertGreater(diag_data["visual_confidence"], 60)
        self.assertIn("immediate_home_care", diag_data)

    def test_14_chatbot_query(self):
        # 1. Hindi query about FMD symptoms
        res_hi = self.client.post("/api/chatbot", json={
            "message": "गाय के पैर और मुंह में छाले हैं क्या करें?",
            "language": "hi",
            "species": "Cattle"
        })
        self.assertEqual(res_hi.status_code, 200)
        data_hi = res_hi.get_json()
        self.assertTrue(data_hi["success"])
        self.assertEqual(data_hi["intent"], "FMD_TREATMENT")
        self.assertTrue(data_hi["is_emergency"])
        self.assertIn("खुरपका", data_hi["reply"])

        # 2. English query about drug withdrawal period
        res_en = self.client.post("/api/chatbot", json={
            "message": "What is the milk withdrawal time for enrofloxacin?",
            "language": "en"
        })
        self.assertEqual(res_en.status_code, 200)
        data_en = res_en.get_json()
        self.assertTrue(data_en["success"])
        self.assertEqual(data_en["intent"], "WITHDRAWAL_STEWARDSHIP")
        self.assertIn("withdrawal", data_en["reply"].lower())

if __name__ == "__main__":
    unittest.main()

