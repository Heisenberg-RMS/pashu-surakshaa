"""
Pashu Suraksha - Animal Health Surveillance & Early Warning Decision-Support System
Main Flask Application & REST API Server
"""

import os
import json
import base64
from flask import Flask, request, jsonify, render_template, send_from_directory, session
from database.db import (
    init_db, get_all_reports, get_all_animals, get_animal_by_tag,
    get_all_outbreaks, get_all_lab_referrals, get_all_advisories,
    insert_report, insert_lab_referral, update_lab_referral_status,
    insert_vaccination, log_advisory, get_db_connection,
    authenticate_user, get_user_by_id, get_user_by_phone, get_demo_users
)
from core.triage_engine import assess_symptoms, DISEASE_KNOWLEDGE_BASE
from core.cluster_detector import detect_outbreak_clusters
from core.weather_risk import get_regional_weather_profiles, calculate_environmental_risk
from core.advisory_generator import get_multilingual_advisory, get_all_supported_languages
from core.vision_engine import diagnose_image, VISUAL_DISEASE_PROFILES
from core.chatbot_engine import process_chat_message

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, "static"),
            template_folder=os.path.join(BASE_DIR, "templates"))
app.secret_key = "pashu-suraksha-surveillance-secret-key-2026"

# Ensure DB is initialized
init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/manifest.json")
def manifest():
    return send_from_directory(app.static_folder, "manifest.json")

@app.route("/sw.js")
def service_worker():
    response = send_from_directory(app.static_folder, "sw.js")
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Content-Type"] = "application/javascript"
    return response

# ==========================================
# AUTHENTICATION & IDENTITY APIs
# ==========================================

@app.route("/api/auth/demo-users", methods=["GET"])
def list_demo_users():
    return jsonify(get_demo_users())

@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    role_switch = data.get("role")

    # Quick demo role login
    if role_switch:
        demo_users = get_demo_users()
        user = next((u for u in demo_users if u["role"] == role_switch), None)
        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            return jsonify({"success": True, "user": user, "message": f"Logged in as {user['full_name']}"})

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), 400

    user = authenticate_user(username, password)
    if not user:
        return jsonify({"success": False, "error": "Invalid username or password"}), 401

    session["user_id"] = user["id"]
    session["role"] = user["role"]
    return jsonify({"success": True, "user": user})

@app.route("/api/auth/otp/send", methods=["POST"])
def auth_send_otp():
    data = request.json or {}
    phone = data.get("phone", "").strip()
    if not phone:
        return jsonify({"success": False, "error": "Mobile phone number required"}), 400

    simulated_otp = "1962" # National Animal Disease Helpline code
    return jsonify({
        "success": True,
        "phone": phone,
        "simulated_otp": simulated_otp,
        "message": f"OTP 1962 dispatched to mobile {phone}."
    })

@app.route("/api/auth/otp/verify", methods=["POST"])
def auth_verify_otp():
    data = request.json or {}
    phone = data.get("phone", "").strip()
    otp = data.get("otp", "").strip()

    if otp != "1962":
        return jsonify({"success": False, "error": "Invalid OTP. Please use demo OTP: 1962"}), 400

    user = get_user_by_phone(phone)
    if not user:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO users (username, phone, password, role, full_name, designation, village, block, district, state)
        VALUES (?, ?, 'otp123', 'FARMER', ?, 'Livestock Keeper', 'Dhani Mohabbatpur', 'Hansi', 'Hisar', 'Haryana')
        """, (f"user_{phone[-4:]}", phone, f"Farmer ({phone[-4:]})"))
        new_id = cur.lastrowid
        conn.commit()
        conn.close()
        user = get_user_by_id(new_id)

    session["user_id"] = user["id"]
    session["role"] = user["role"]
    return jsonify({"success": True, "user": user})

@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    user_id = session.get("user_id")
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            return jsonify({"authenticated": True, "user": user})
            
    # Default initial active profile (DVO)
    demo_users = get_demo_users()
    default_user = next((u for u in demo_users if u["role"] == "DVO"), None)
    return jsonify({
        "authenticated": False,
        "user": default_user or {
            "id": 1,
            "username": "dvo_hisar",
            "role": "DVO",
            "full_name": "Dr. Sunil Bishnoi",
            "designation": "District Veterinary Officer (DVO)",
            "district": "Hisar",
            "state": "Haryana"
        }
    })

@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})

# ==========================================
# VISION DIAGNOSTICS & CHATBOT APIs
# ==========================================

@app.route("/api/image-diagnosis", methods=["POST"])
def image_diagnosis():
    filename = ""
    hint = ""
    image_bytes = b""
    
    if "image" in request.files:
        file = request.files["image"]
        filename = file.filename or "upload.jpg"
        image_bytes = file.read()
    elif request.is_json:
        data = request.json or {}
        hint = data.get("hint", "")
        filename = data.get("filename", "")
        data_url = data.get("image_data", "")
        if "," in data_url:
            data_url = data_url.split(",")[1]
        try:
            image_bytes = base64.b64decode(data_url)
        except Exception:
            image_bytes = b"simulated_image_bytes"
            
    result = diagnose_image(image_bytes, filename=filename, metadata_hint=hint)
    return jsonify(result)

@app.route("/api/image-diagnosis/presets", methods=["GET"])
def list_vision_presets():
    presets = []
    for k, v in VISUAL_DISEASE_PROFILES.items():
        presets.append({
            "key": k,
            "title": v["disease_name"],
            "lesion_type": v["lesion_type"],
            "species": v["species"],
            "severity": v["severity"]
        })
    return jsonify(presets)

@app.route("/api/chatbot", methods=["POST"])
def chatbot_reply():
    data = request.json or {}
    message = data.get("message", "").strip()
    language = data.get("language", "hi")
    
    if not message:
        return jsonify({"success": False, "error": "Message cannot be empty"}), 400
        
    reply = process_chat_message(message, language=language)
    return jsonify(reply)

# ==========================================
# SURVEILLANCE & TRIAGE APIs
# ==========================================

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ONLINE",
        "service": "Pashu Suraksha Unified Surveillance API",
        "version": "2.4.0",
        "capabilities": ["Syndromic Triage", "GIS Outbreak Clusters", "Animal EHR", "Lab Chain of Custody", "Multilingual Voice Advisories", "Simulated IVR"]
    })

@app.route("/api/triage/assess", methods=["POST"])
def triage_assess():
    """Real-time syndromic triage calculation without saving."""
    data = request.json or {}
    species = data.get("species", "Cattle")
    symptoms = data.get("symptoms", [])
    has_fever = bool(data.get("has_fever", False))
    mortality = int(data.get("mortality_count", 0))
    affected = int(data.get("affected_count", 1))
    notes = data.get("additional_notes", "")
    
    assessment = assess_symptoms(
        species=species,
        symptoms=symptoms,
        has_fever=has_fever,
        mortality_count=mortality,
        affected_count=affected,
        additional_notes=notes
    )
    return jsonify(assessment)

@app.route("/api/triage/knowledge-base", methods=["GET"])
def get_knowledge_base():
    """Returns available disease definitions and symptoms for UI selectors."""
    return jsonify(DISEASE_KNOWLEDGE_BASE)

@app.route("/api/reports", methods=["GET"])
def list_reports():
    limit = int(request.args.get("limit", 50))
    reports = get_all_reports(limit=limit)
    return jsonify(reports)

@app.route("/api/reports", methods=["POST"])
def create_report():
    """
    Submits a symptom or mortality report, runs triage, checks for cluster outbreaks,
    and updates quarantine recommendations.
    """
    data = request.json or {}
    species = data.get("species", "Cattle")
    symptoms = data.get("symptoms", [])
    has_fever = bool(data.get("has_fever", False))
    mortality = int(data.get("mortality_count", 0))
    affected = int(data.get("affected_count", 1))
    
    # Run triage engine
    triage_result = assess_symptoms(
        species=species,
        symptoms=symptoms,
        has_fever=has_fever,
        mortality_count=mortality,
        affected_count=affected,
        additional_notes=data.get("additional_notes", "")
    )
    
    top_diag = triage_result.get("top_diagnosis", {})
    triage_code = top_diag.get("code", "GENERAL")
    triage_name = top_diag.get("name", "General Sickness")
    confidence = top_diag.get("confidence", 30)
    urgency = triage_result.get("urgency", "LOW")
    is_zoonotic = 1 if triage_result.get("is_zoonotic") else 0
    containment_triggered = 1 if triage_result.get("trigger_containment_ring") else 0
    
    # Prepare record
    record = {
        "reporter_type": data.get("reporter_type", "FARMER"),
        "reporter_name": data.get("reporter_name", "Anonymous Reporter"),
        "reporter_phone": data.get("reporter_phone", "9876543210"),
        "animal_tag": data.get("animal_tag"),
        "species": species,
        "village": data.get("village", "Local Village"),
        "block": data.get("block", "Local Block"),
        "district": data.get("district", "Local District"),
        "latitude": float(data.get("latitude", 29.1023)),
        "longitude": float(data.get("longitude", 76.0125)),
        "symptoms": symptoms,
        "has_fever": has_fever,
        "affected_count": affected,
        "mortality_count": mortality,
        "additional_notes": data.get("additional_notes", ""),
        "photo_url": data.get("photo_url"),
        "triage_code": triage_code,
        "triage_name": triage_name,
        "confidence": confidence,
        "urgency": urgency,
        "is_zoonotic": is_zoonotic,
        "containment_triggered": containment_triggered,
        "status": "VERIFIED" if urgency in ["CRITICAL", "HIGH"] else "PENDING_REVIEW"
    }
    
    report_id = insert_report(record)
    record["id"] = report_id
    
    # Cluster detection check across all recent reports
    all_reports = get_all_reports(limit=100)
    clusters = detect_outbreak_clusters(all_reports)
    
    # Auto-generate lab sample recommendation if high-risk
    lab_barcode = None
    if urgency in ["CRITICAL", "HIGH"]:
        lab_barcode = insert_lab_referral({
            "report_id": report_id,
            "animal_tag": data.get("animal_tag"),
            "sample_type": triage_result.get("recommended_sample", "Serum / Swab"),
            "suspect_disease": triage_name,
            "target_lab": "District Animal Disease Diagnostic Lab",
            "notes": f"Auto-escalated from report {report_id} with urgency {urgency}"
        })
        
    return jsonify({
        "success": True,
        "report_id": report_id,
        "triage_result": triage_result,
        "lab_referral_barcode": lab_barcode,
        "detected_clusters_count": len(clusters),
        "cluster_alert": any(c["disease_code"] == triage_code for c in clusters)
    })

# ==========================================
# ANIMAL & HERD EHR APIs
# ==========================================

@app.route("/api/animals", methods=["GET"])
def list_animals():
    return jsonify(get_all_animals())

@app.route("/api/animals/<tag_number>", methods=["GET"])
def get_animal_ehr(tag_number):
    animal = get_animal_by_tag(tag_number)
    if not animal:
        return jsonify({"error": "Animal tag not found"}), 404
    return jsonify(animal)

@app.route("/api/animals", methods=["POST"])
def register_animal():
    data = request.json or {}
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO animals (tag_number, species, breed, sex, age_months, owner_name, owner_phone, village, block, district, health_status, rfid_uid)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("tag_number"),
        data.get("species", "Cattle"),
        data.get("breed", "Indigenous"),
        data.get("sex", "Female"),
        int(data.get("age_months", 24)),
        data.get("owner_name", "Farmer"),
        data.get("owner_phone", ""),
        data.get("village", ""),
        data.get("block", ""),
        data.get("district", ""),
        "HEALTHY",
        data.get("rfid_uid", "RFID-" + data.get("tag_number", "")[-6:])
    ))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "tag_number": data.get("tag_number")})

@app.route("/api/vaccinations", methods=["POST"])
def add_vaccination():
    data = request.json or {}
    insert_vaccination(data)
    return jsonify({"success": True})

# ==========================================
# GEOSPATIAL & OUTBREAK MAPPING APIs
# ==========================================

@app.route("/api/outbreaks", methods=["GET"])
def list_outbreaks():
    # Fetch declared outbreaks
    declared = get_all_outbreaks()
    # Also run dynamic cluster detection on current reports
    reports = get_all_reports(limit=100)
    detected = detect_outbreak_clusters(reports)
    
    return jsonify({
        "declared_outbreaks": declared,
        "algorithmic_clusters": detected
    })

@app.route("/api/weather-risk", methods=["GET"])
def get_weather_risk():
    profiles = get_regional_weather_profiles()
    return jsonify(profiles)

# ==========================================
# LABORATORY REFERRAL APIs
# ==========================================

@app.route("/api/lab-referrals", methods=["GET"])
def list_lab_referrals():
    return jsonify(get_all_lab_referrals())

@app.route("/api/lab-referrals", methods=["POST"])
def create_lab_referral():
    data = request.json or {}
    barcode = insert_lab_referral(data)
    return jsonify({"success": True, "sample_barcode": barcode})

@app.route("/api/lab-referrals/<barcode>", methods=["PUT"])
def update_lab_referral(barcode):
    data = request.json or {}
    status = data.get("chain_of_custody_status", "TESTING_IN_PROGRESS")
    result = data.get("result_certified", "PENDING")
    notes = data.get("result_notes", "")
    update_lab_referral_status(barcode, status, result, notes)
    return jsonify({"success": True, "sample_barcode": barcode})

# ==========================================
# MULTILINGUAL ADVISORIES & ALERTS
# ==========================================

@app.route("/api/advisories/languages", methods=["GET"])
def list_languages():
    return jsonify(get_all_supported_languages())

@app.route("/api/advisories", methods=["GET"])
def list_advisories():
    return jsonify(get_all_advisories())

@app.route("/api/advisories/preview", methods=["GET"])
def preview_advisory():
    alert_type = request.args.get("alert_type", "FMD_OUTBREAK")
    lang = request.args.get("lang", "hi")
    advisory = get_multilingual_advisory(alert_type, lang)
    return jsonify(advisory)

@app.route("/api/advisories/broadcast", methods=["POST"])
def broadcast_advisory():
    """Simulates broadcasting emergency advisory via SMS/WhatsApp/Voice to farmers."""
    data = request.json or {}
    alert_type = data.get("alert_type", "FMD_OUTBREAK")
    lang = data.get("language", "hi")
    district = data.get("district", "Hisar")
    block = data.get("block", "Hansi")
    radius_km = float(data.get("radius_km", 10.0))
    
    advisory = get_multilingual_advisory(alert_type, lang)
    notified_count = int(radius_km * 45) # simulated density
    
    log_advisory({
        "alert_type": alert_type,
        "title": advisory["title"],
        "message_hi": advisory["text"] if lang == "hi" else None,
        "message_en": advisory["text"] if lang == "en" else advisory["voice_script"],
        "target_district": district,
        "target_block": block,
        "target_radius_km": radius_km,
        "farmers_notified_count": notified_count,
        "channel": data.get("channel", "SMS_AND_VOICE")
    })
    
    return jsonify({
        "success": True,
        "title": advisory["title"],
        "farmers_reached": notified_count,
        "channels_used": ["SMS", "Automated Voice IVR Call", "Pashu Sakhi App"],
        "preview_text": advisory["text"],
        "voice_script": advisory["voice_script"]
    })

# ==========================================
# SIMULATED IVR HOTLINE API
# ==========================================

@app.route("/api/ivr/process", methods=["POST"])
def process_ivr():
    """
    Simulates interactive telephone IVR for low-connectivity/feature-phone users.
    Handles step-by-step keypad/voice inputs.
    """
    data = request.json or {}
    session_step = data.get("step", "START")
    digits = str(data.get("digits", "")).strip()
    language = data.get("language", "hi")
    
    # State machine for IVR
    if session_step == "START":
        return jsonify({
            "next_step": "SPECIES_SELECTION",
            "prompt_text": "पशु स्वास्थ्य हेल्पलाइन में आपका स्वागत है। गाय या भैंस के लिए 1 दबाएं। बकरी या भेड़ के लिए 2 दबाएं। सुअर के लिए 3 दबाएं। मुर्गी के लिए 4 दबाएं।",
            "prompt_text_en": "Welcome to Animal Health Helpline. Press 1 for Cattle or Buffalo. Press 2 for Goat or Sheep. Press 3 for Pig. Press 4 for Poultry.",
            "options": ["1: Cattle/Buffalo", "2: Goat/Sheep", "3: Pig", "4: Poultry"]
        })
        
    elif session_step == "SPECIES_SELECTION":
        species_map = {"1": "Cattle", "2": "Goat", "3": "Pig", "4": "Poultry"}
        selected_species = species_map.get(digits, "Cattle")
        return jsonify({
            "next_step": "SYMPTOM_SELECTION",
            "selected_species": selected_species,
            "prompt_text": f"आपने {selected_species} चुना है। यदि मुंह या खुर में छाले व लार गिर रही है तो 1 दबाएं। यदि शरीर पर गोल गांठें हैं तो 2 दबाएं। यदि तेज बुखार और गला सूजा है तो 3 दबाएं। यदि अचानक मृत्यु हुई है तो 4 दबाएं।",
            "prompt_text_en": f"You selected {selected_species}. Press 1 if blisters in mouth/hooves with drooling. Press 2 if skin nodules. Press 3 if neck swelling and high fever. Press 4 if sudden death.",
            "options": ["1: Blisters & Salivation (FMD)", "2: Skin Nodules (LSD)", "3: Swollen Throat (HS)", "4: Sudden Death (Anthrax)"]
        })
        
    elif session_step == "SYMPTOM_SELECTION":
        symptom_map = {
            "1": (["oral_vesicles", "hoof_lesions", "excessive_salivation"], "FMD", "खुरपका-मुंहपका (FMD)"),
            "2": (["skin_nodules", "limb_edema"], "LSD", "गांठदार त्वचा रोग (LSD)"),
            "3": (["throat_swelling", "stertorous_breathing"], "HS", "गलघोंटू (HS)"),
            "4": (["sudden_unexplained_death", "unclotted_dark_blood"], "ANTHRAX", "एंथ्रेक्स (विषहरि)")
        }
        symptoms, code, name = symptom_map.get(digits, (["oral_vesicles"], "FMD", "FMD"))
        species = data.get("selected_species", "Cattle")
        
        # Run triage
        assessment = assess_symptoms(species=species, symptoms=symptoms, has_fever=True, affected_count=1)
        
        # Log quick IVR report
        report_id = insert_report({
            "reporter_type": "IVR",
            "reporter_name": "Toll-Free IVR Caller",
            "reporter_phone": data.get("caller_phone", "9876500000"),
            "species": species,
            "village": "IVR Village",
            "block": "Central",
            "district": "Hisar",
            "latitude": 29.1023,
            "longitude": 76.0125,
            "symptoms": symptoms,
            "has_fever": True,
            "affected_count": 1,
            "mortality_count": 1 if digits == "4" else 0,
            "additional_notes": f"Automated IVR call. Keypad selection: {digits}",
            "triage_code": code,
            "triage_name": name,
            "confidence": assessment["top_diagnosis"]["confidence"],
            "urgency": assessment["urgency"],
            "is_zoonotic": assessment["is_zoonotic"],
            "containment_triggered": 1 if assessment["trigger_containment_ring"] else 0
        })
        
        advisory_msg = f"आपकी रिपोर्ट संख्या {report_id} दर्ज कर ली गई है। संभावित रोग: {name}। "
        if code == "ANTHRAX":
            advisory_msg += "चेतावनी: मृत पशु के शव को बिल्कुल न चीरें। पशु चिकित्सक टीम को तुरंत भेजा जा रहा है।"
        elif code == "FMD":
            advisory_msg += "पशु को तुरंत अलग बांधें। लाल दवा से पैर धोएं। सरकारी पशु चिकित्सक को सूचना भेज दी गई है।"
        else:
            advisory_msg += "पशु को छाया में रखें और नजदीकी पशु औषधालय से संपर्क करें।"
            
        return jsonify({
            "next_step": "COMPLETED",
            "report_id": report_id,
            "triage_code": code,
            "triage_name": name,
            "urgency": assessment["urgency"],
            "prompt_text": advisory_msg,
            "prompt_text_en": f"Report #{report_id} registered. Suspected: {name}. Veterinary team notified. " + assessment["biohazard_alert"]
        })

# ==========================================
# EXECUTIVE DASHBOARD ANALYTICS API
# ==========================================

@app.route("/api/stats/dashboard", methods=["GET"])
def dashboard_stats():
    conn = get_db_connection()
    cur = conn.cursor()
    
    total_animals = cur.execute("SELECT COUNT(*) FROM animals").fetchone()[0]
    total_sick = cur.execute("SELECT COUNT(*) FROM animals WHERE health_status IN ('SICK', 'QUARANTINED')").fetchone()[0]
    total_reports = cur.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    active_outbreaks = cur.execute("SELECT COUNT(*) FROM outbreaks WHERE containment_status = 'ACTIVE'").fetchone()[0]
    pending_lab = cur.execute("SELECT COUNT(*) FROM lab_referrals WHERE chain_of_custody_status != 'CONFIRMED'").fetchone()[0]
    total_vaccinations = cur.execute("SELECT COUNT(*) FROM vaccinations WHERE status = 'COMPLETED'").fetchone()[0]
    overdue_vaccinations = cur.execute("SELECT COUNT(*) FROM vaccinations WHERE status = 'OVERDUE'").fetchone()[0]
    
    # Reports by disease code
    cur.execute("""
    SELECT triage_code, triage_name, COUNT(*) as count, SUM(mortality_count) as mortality
    FROM reports
    WHERE triage_code IS NOT NULL
    GROUP BY triage_code
    ORDER BY count DESC
    """)
    disease_breakdown = [dict(r) for r in cur.fetchall()]
    
    # Recent reports
    cur.execute("SELECT * FROM reports ORDER BY id DESC LIMIT 5")
    recent_reports = [dict(r) for r in cur.fetchall()]
    for r in recent_reports:
        try:
            r["symptoms"] = json.loads(r["symptoms_json"])
        except Exception:
            r["symptoms"] = []
            
    conn.close()
    
    return jsonify({
        "metrics": {
            "total_registered_livestock": total_animals,
            "active_morbidity_count": total_sick,
            "total_surveillance_reports": total_reports,
            "active_outbreak_clusters": active_outbreaks,
            "pending_diagnostic_samples": pending_lab,
            "completed_vaccinations": total_vaccinations,
            "overdue_vaccinations": overdue_vaccinations,
            "herd_immunity_index": "81.4%"
        },
        "disease_breakdown": disease_breakdown,
        "recent_reports": recent_reports
    })

if __name__ == "__main__":
    print("Starting Pashu Suraksha Server on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
