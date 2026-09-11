"""
Pashu Suraksha - Database Engine & Models (SQLite)
Manages schemas, persistent storage, queries, and rich baseline seed data
for farmers, animals, health reports, vaccinations, treatments, lab referrals, and outbreaks.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "pashu_suraksha.db")

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables and seeds baseline operational data."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Farmers table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS farmers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        village TEXT NOT NULL,
        block TEXT NOT NULL,
        district TEXT NOT NULL,
        state TEXT NOT NULL,
        pin_code TEXT,
        livestock_count INTEGER DEFAULT 0,
        language_preference TEXT DEFAULT 'hi',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Animals table (EHR)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS animals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tag_number TEXT NOT NULL UNIQUE,
        species TEXT NOT NULL,
        breed TEXT,
        sex TEXT,
        age_months INTEGER,
        owner_id INTEGER,
        owner_name TEXT,
        owner_phone TEXT,
        village TEXT,
        block TEXT,
        district TEXT,
        health_status TEXT DEFAULT 'HEALTHY',
        rfid_uid TEXT,
        registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (owner_id) REFERENCES farmers (id)
    )
    """)
    
    # Disease & Mortality Reports
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_uid TEXT NOT NULL UNIQUE,
        reporter_type TEXT NOT NULL,
        reporter_name TEXT NOT NULL,
        reporter_phone TEXT NOT NULL,
        animal_tag TEXT,
        species TEXT NOT NULL,
        village TEXT NOT NULL,
        block TEXT NOT NULL,
        district TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        symptoms_json TEXT NOT NULL,
        has_fever INTEGER DEFAULT 0,
        affected_count INTEGER DEFAULT 1,
        mortality_count INTEGER DEFAULT 0,
        additional_notes TEXT,
        photo_url TEXT,
        triage_code TEXT,
        triage_name TEXT,
        confidence INTEGER,
        urgency TEXT,
        is_zoonotic INTEGER DEFAULT 0,
        containment_triggered INTEGER DEFAULT 0,
        status TEXT DEFAULT 'PENDING_REVIEW',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Vaccinations
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vaccinations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal_tag TEXT NOT NULL,
        vaccine_name TEXT NOT NULL,
        disease_targeted TEXT NOT NULL,
        dose_number INTEGER DEFAULT 1,
        batch_number TEXT,
        manufacturer TEXT,
        administered_date TEXT NOT NULL,
        next_due_date TEXT NOT NULL,
        administered_by TEXT,
        status TEXT DEFAULT 'COMPLETED',
        FOREIGN KEY (animal_tag) REFERENCES animals (tag_number)
    )
    """)
    
    # Treatments & Drug Stewardship (Antibiotic withdrawal period)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS treatments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal_tag TEXT NOT NULL,
        diagnosis TEXT NOT NULL,
        drug_administered TEXT NOT NULL,
        dosage TEXT,
        treatment_date TEXT NOT NULL,
        withdrawal_period_days INTEGER DEFAULT 0,
        withdrawal_end_date TEXT,
        vet_name TEXT,
        notes TEXT,
        FOREIGN KEY (animal_tag) REFERENCES animals (tag_number)
    )
    """)
    
    # Laboratory Referral & Chain of Custody
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lab_referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sample_barcode TEXT NOT NULL UNIQUE,
        report_id INTEGER,
        animal_tag TEXT,
        sample_type TEXT NOT NULL,
        suspect_disease TEXT NOT NULL,
        target_lab TEXT NOT NULL,
        collection_date TEXT NOT NULL,
        chain_of_custody_status TEXT DEFAULT 'SAMPLE_COLLECTED',
        result_certified TEXT DEFAULT 'PENDING',
        result_notes TEXT,
        tested_at TEXT,
        FOREIGN KEY (report_id) REFERENCES reports (id)
    )
    """)
    
    # Active Outbreaks & Containment Zones
    cur.execute("""
    CREATE TABLE IF NOT EXISTS outbreaks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cluster_id TEXT NOT NULL UNIQUE,
        disease_code TEXT NOT NULL,
        disease_name TEXT NOT NULL,
        district TEXT NOT NULL,
        block TEXT NOT NULL,
        village TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        infected_radius_km REAL DEFAULT 3.0,
        surveillance_radius_km REAL DEFAULT 10.0,
        active_cases INTEGER DEFAULT 1,
        mortality INTEGER DEFAULT 0,
        containment_status TEXT DEFAULT 'ACTIVE',
        alert_level TEXT DEFAULT 'CRITICAL',
        declared_date TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Advisories Log
    cur.execute("""
    CREATE TABLE IF NOT EXISTS advisories_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_type TEXT NOT NULL,
        title TEXT NOT NULL,
        message_hi TEXT,
        message_en TEXT,
        target_district TEXT NOT NULL,
        target_block TEXT,
        target_radius_km REAL DEFAULT 10.0,
        farmers_notified_count INTEGER DEFAULT 0,
        channel TEXT DEFAULT 'ALL',
        broadcast_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Users table (Authentication & Roles)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT NOT NULL,
        designation TEXT,
        village TEXT,
        block TEXT,
        district TEXT,
        state TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    
    # Check if seed data exists
    cur.execute("SELECT COUNT(*) FROM farmers")
    if cur.fetchone()[0] == 0:
        seed_baseline_data(conn)
    else:
        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            seed_baseline_data(conn)
        
    conn.close()

def seed_baseline_data(conn: sqlite3.Connection):
    """Populates realistic initial data across Indian farming clusters."""
    cur = conn.cursor()
    
    # 0. Users (Authentication & Roles)
    users_data = [
        ("farmer", "9876543210", "farm123", "FARMER", "Ramcharan Yadav", "Dairy Livestock Keeper", "Dhani Mohabbatpur", "Hansi", "Hisar", "Haryana"),
        ("paravet", "9812903421", "vet123", "PARA_VET", "Ramesh Kumar", "Pashu Sakhi / Para-Veterinary Worker", "Bhatla", "Hansi", "Hisar", "Haryana"),
        ("dvo_hisar", "9899123456", "dvo123", "DVO", "Dr. Sunil Bishnoi", "District Veterinary Officer (DVO)", "Hisar Polyclinic", "Hisar", "Hisar", "Haryana"),
        ("director_ah", "9811002233", "state123", "DIRECTOR", "Dr. A. K. Sharma", "Director General of Animal Husbandry", "State Secretariat", "Central", "State Directorate", "Haryana")
    ]
    cur.executemany("""
    INSERT OR IGNORE INTO users (username, phone, password, role, full_name, designation, village, block, district, state)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, users_data)
    
    # 1. Farmers
    farmers_data = [
        ("Ramcharan Yadav", "9876543210", "Dhani Mohabbatpur", "Hansi", "Hisar", "Haryana", "125033", 6, "hi"),
        ("Sukhwinder Singh", "9812345678", "Mullanpur", "Jagraon", "Ludhiana", "Punjab", "141101", 12, "pa"),
        ("Dharmesh Patel", "9823456789", "Boriavi", "Petlad", "Anand", "Gujarat", "388450", 8, "hi"),
        ("Shyam Sundar Sharma", "9834567890", "Kewani", "Faridpur", "Bareilly", "Uttar Pradesh", "243503", 5, "hi"),
        ("Perumal Krishnan", "9845678901", "Kadayampatti", "Omalur", "Salem", "Tamil Nadu", "636351", 9, "ta"),
        ("Baburao Deshmukh", "9856789012", "Chakur", "Chakur", "Latur", "Maharashtra", "413513", 14, "mr")
    ]
    cur.executemany("""
    INSERT OR IGNORE INTO farmers (name, phone, village, block, district, state, pin_code, livestock_count, language_preference)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, farmers_data)
    
    # 2. Animals (EHR)
    animals_data = [
        ("100982347101", "Cattle", "Murrah Cross", "Female", 36, 1, "Ramcharan Yadav", "9876543210", "Dhani Mohabbatpur", "Hansi", "Hisar", "SICK", "RFID-882101"),
        ("100982347102", "Buffalo", "Murrah", "Female", 48, 1, "Ramcharan Yadav", "9876543210", "Dhani Mohabbatpur", "Hansi", "Hisar", "HEALTHY", "RFID-882102"),
        ("100982347103", "Cattle", "Sahiwal", "Female", 28, 1, "Ramcharan Yadav", "9876543210", "Dhani Mohabbatpur", "Hansi", "Hisar", "HEALTHY", "RFID-882103"),
        ("100982347201", "Cattle", "HF Cross", "Female", 42, 2, "Sukhwinder Singh", "9812345678", "Mullanpur", "Jagraon", "Ludhiana", "HEALTHY", "RFID-771201"),
        ("100982347202", "Cattle", "HF Cross", "Female", 30, 2, "Sukhwinder Singh", "9812345678", "Mullanpur", "Jagraon", "Ludhiana", "SICK", "RFID-771202"),
        ("100982347301", "Cattle", "Gir", "Female", 50, 3, "Dharmesh Patel", "9823456789", "Boriavi", "Petlad", "Anand", "QUARANTINED", "RFID-663301"),
        ("100982347302", "Cattle", "Gir", "Male", 24, 3, "Dharmesh Patel", "9823456789", "Boriavi", "Petlad", "Anand", "HEALTHY", "RFID-663302"),
        ("100982347401", "Buffalo", "Bhadawari", "Female", 38, 4, "Shyam Sundar Sharma", "9834567890", "Kewani", "Faridpur", "Bareilly", "SICK", "RFID-554401"),
        ("100982347501", "Goat", "Salem Black", "Female", 18, 5, "Perumal Krishnan", "9845678901", "Kadayampatti", "Omalur", "Salem", "HEALTHY", "RFID-441101"),
        ("100982347502", "Goat", "Salem Black", "Male", 22, 5, "Perumal Krishnan", "9845678901", "Kadayampatti", "Omalur", "Salem", "HEALTHY", "RFID-441102")
    ]
    cur.executemany("""
    INSERT OR IGNORE INTO animals (tag_number, species, breed, sex, age_months, owner_id, owner_name, owner_phone, village, block, district, health_status, rfid_uid)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, animals_data)
    
    # 3. Vaccinations
    today = datetime.now()
    six_months_ago = (today - timedelta(days=180)).strftime("%Y-%m-%d")
    next_fmd_due = (today + timedelta(days=15)).strftime("%Y-%m-%d")
    overdue_date = (today - timedelta(days=20)).strftime("%Y-%m-%d")
    
    vaccines_data = [
        ("100982347101", "Raksha-Ovac FMD", "Foot-and-Mouth Disease", 2, "BT-9021", "Indian Immunologicals", six_months_ago, next_fmd_due, "Dr. Sunil Bishnoi", "COMPLETED"),
        ("100982347102", "Raksha-Ovac FMD", "Foot-and-Mouth Disease", 3, "BT-9021", "Indian Immunologicals", six_months_ago, next_fmd_due, "Dr. Sunil Bishnoi", "COMPLETED"),
        ("100982347101", "Galghontu HS Vaccine", "Hemorrhagic Septicemia", 1, "HS-332", "IVRI Bareilly", six_months_ago, overdue_date, "Dr. Sunil Bishnoi", "OVERDUE"),
        ("100982347301", "Goat Pox Vaccine (Heterologous LSD)", "Lumpy Skin Disease", 1, "LSD-710", "Hester Biosciences", six_months_ago, next_fmd_due, "Dr. K. J. Thakkar", "COMPLETED"),
        ("100982347501", "PPR Live Vaccine", "Peste des Petits Ruminants", 1, "PPR-412", "Bio-Med", (today - timedelta(days=300)).strftime("%Y-%m-%d"), (today + timedelta(days=65)).strftime("%Y-%m-%d"), "Dr. M. Soundararajan", "COMPLETED")
    ]
    cur.executemany("""
    INSERT INTO vaccinations (animal_tag, vaccine_name, disease_targeted, dose_number, batch_number, manufacturer, administered_date, next_due_date, administered_by, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, vaccines_data)
    
    # 4. Treatments with Antimicrobial Withdrawal Stewardship
    treatments_data = [
        ("100982347101", "Severe Pododermatitis & Vesicles", "Ceftiofur Sodium 1g IM & Meloxicam", "1 vial daily x 3 days", (today - timedelta(days=2)).strftime("%Y-%m-%d"), 7, (today + timedelta(days=5)).strftime("%Y-%m-%d"), "Dr. Sunil Bishnoi", "WITHDRAWAL RESTRICTION: Milk & meat unfit for human consumption until withdrawal date!"),
        ("100982347401", "Acute Submandibular Edema (Suspected HS)", "Oxytetracycline LA 200mg/ml", "20 ml deep IM", (today - timedelta(days=1)).strftime("%Y-%m-%d"), 21, (today + timedelta(days=20)).strftime("%Y-%m-%d"), "Dr. V. K. Saxena", "High dose long-acting tetracycline. Strict 21-day slaughter withdrawal.")
    ]
    cur.executemany("""
    INSERT INTO treatments (animal_tag, diagnosis, drug_administered, dosage, treatment_date, withdrawal_period_days, withdrawal_end_date, vet_name, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, treatments_data)
    
    # 5. Seed Reports (spanning recent days to demonstrate clustering & triage)
    rep1_time = (today - timedelta(days=1, hours=4)).isoformat()
    rep2_time = (today - timedelta(days=1, hours=1)).isoformat()
    rep3_time = (today - timedelta(hours=6)).isoformat()
    rep4_time = (today - timedelta(hours=2)).isoformat()
    rep5_time = (today - timedelta(days=2)).isoformat()
    
    reports_data = [
        # Cluster 1: FMD in Hisar district (3 nearby cases)
        ("REP-2026-001", "FARMER", "Ramcharan Yadav", "9876543210", "100982347101", "Cattle", "Dhani Mohabbatpur", "Hansi", "Hisar", 29.1023, 76.0125,
         json.dumps(["oral_vesicles", "hoof_lesions", "excessive_salivation", "lameness", "drop_in_milk"]), 1, 3, 0,
         "Animal is drooling thick frothy saliva and unable to stand due to foot sores.", None,
         "FMD", "Foot-and-Mouth Disease (खुरपका और मुंहपका)", 92, "CRITICAL", 0, 1, "VERIFIED", rep1_time),
         
        ("REP-2026-002", "PARA_VET", "Ramesh Kumar (Pashu Sakhi)", "9812903421", None, "Cattle", "Bhatla", "Hansi", "Hisar", 29.1350, 76.0420,
         json.dumps(["oral_vesicles", "excessive_salivation", "lameness"]), 1, 4, 0,
         "Found 4 heifers in village herd with severe vesicular stomatitis and smacking of lips.", None,
         "FMD", "Foot-and-Mouth Disease (खुरपका और मुंहपका)", 88, "CRITICAL", 0, 1, "INVESTIGATED", rep2_time),
         
        ("REP-2026-003", "VET_OFFICER", "Dr. Sunil Bishnoi", "9899123456", None, "Buffalo", "Kheri Gagan", "Hansi", "Hisar", 29.0880, 75.9910,
         json.dumps(["hoof_lesions", "oral_vesicles", "lameness"]), 1, 2, 0,
         "Clinical examination confirmed ruptured erosions on interdigital cleft and dental pad.", None,
         "FMD", "Foot-and-Mouth Disease (खुरपका और मुंहपका)", 85, "CRITICAL", 0, 1, "VERIFIED", rep3_time),
         
        # Cluster 2: LSD in Anand, Gujarat
        ("REP-2026-004", "FARMER", "Dharmesh Patel", "9823456789", "100982347301", "Cattle", "Boriavi", "Petlad", "Anand", 22.5280, 72.9350,
         json.dumps(["skin_nodules", "enlarged_lymph_nodes", "limb_edema"]), 1, 2, 0,
         "Cow has round hard lumps all over neck and back. Swollen front legs.", None,
         "LSD", "Lumpy Skin Disease (गांठदार त्वचा रोग)", 90, "HIGH", 0, 1, "INVESTIGATED", rep4_time),
         
        # Cluster 3: Hemorrhagic Septicemia in Bareilly, UP
        ("REP-2026-005", "PARA_VET", "Satish Chandra", "9834112233", "100982347401", "Buffalo", "Kewani", "Faridpur", "Bareilly", 28.2140, 79.5420,
         json.dumps(["throat_swelling", "stertorous_breathing", "sudden_collapse"]), 1, 1, 1,
         "Buffalo died within 8 hours of sudden swelling in neck and heavy snoring breath.", None,
         "HS", "Hemorrhagic Septicemia (गलघोंटू रोग)", 88, "HIGH", 0, 1, "VERIFIED", rep5_time)
    ]
    cur.executemany("""
    INSERT OR IGNORE INTO reports (
        report_uid, reporter_type, reporter_name, reporter_phone, animal_tag, species,
        village, block, district, latitude, longitude, symptoms_json, has_fever,
        affected_count, mortality_count, additional_notes, photo_url,
        triage_code, triage_name, confidence, urgency, is_zoonotic, containment_triggered,
        status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, reports_data)
    
    # 6. Outbreaks & Quarantine Zones
    outbreaks_data = [
        ("CLUST-2026-001", "FMD", "Foot-and-Mouth Disease (खुरपका और मुंहपका)", "Hisar", "Hansi", "Dhani Mohabbatpur / Bhatla",
         29.1084, 76.0152, 3.0, 10.0, 9, 0, "ACTIVE", "CRITICAL", (today - timedelta(days=1)).strftime("%Y-%m-%d")),
         
        ("CLUST-2026-002", "LSD", "Lumpy Skin Disease (गांठदार त्वचा रोग)", "Anand", "Petlad", "Boriavi",
         22.5280, 72.9350, 3.0, 8.0, 4, 0, "ACTIVE", "HIGH", (today - timedelta(days=3)).strftime("%Y-%m-%d"))
    ]
    cur.executemany("""
    INSERT OR IGNORE INTO outbreaks (
        cluster_id, disease_code, disease_name, district, block, village,
        latitude, longitude, infected_radius_km, surveillance_radius_km,
        active_cases, mortality, containment_status, alert_level, declared_date
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, outbreaks_data)
    
    # 7. Laboratory Referrals
    samples_data = [
        ("LAB-2026-0091", 1, "100982347101", "Vesicular Fluid & Tongue Epithelium", "Foot-and-Mouth Disease",
         "ICAR-Directorate of FMD / Central Lab Mukteshwar", (today - timedelta(days=1)).strftime("%Y-%m-%d"),
         "TESTING_IN_PROGRESS", "PENDING", "Multiplex RT-PCR and Antigen ELISA underway. Serotype O suspected.", None),
         
        ("LAB-2026-0092", 4, "100982347301", "Skin Nodule Punch Biopsy", "Lumpy Skin Disease",
         "State Disease Diagnostic Lab (SDDL) Gandhinagar", (today - timedelta(days=2)).strftime("%Y-%m-%d"),
         "CONFIRMED", "POSITIVE", "Capripoxvirus specific PCR confirmed positive. CT value: 21.4.", (today - timedelta(hours=4)).strftime("%Y-%m-%d")),
         
        ("LAB-2026-0093", 5, "100982347401", "Heart Blood Swab & Bone Marrow", "Hemorrhagic Septicemia",
         "IVRI Bareilly Diagnostic Laboratory", (today - timedelta(days=2)).strftime("%Y-%m-%d"),
         "CONFIRMED", "POSITIVE", "Pasteurella multocida bipolar coccobacilli confirmed on Gram & Leishman stain.", (today - timedelta(days=1)).strftime("%Y-%m-%d"))
    ]
    cur.executemany("""
    INSERT OR IGNORE INTO lab_referrals (
        sample_barcode, report_id, animal_tag, sample_type, suspect_disease,
        target_lab, collection_date, chain_of_custody_status, result_certified, result_notes, tested_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, samples_data)
    
    # 8. Advisories Log
    advisories_data = [
        ("FMD_OUTBREAK", "Foot-and-Mouth Disease Emergency Containment Alert",
         "पशुपालक भाइयों: हांसी ब्लॉक में खुरपका-मुंहपका का प्रकोप। बीमार पशु को तुरंत अलग करें व 1:1000 लाल दवा के घोल से पैर और मुंह धोएं।",
         "URGENT: FMD Outbreak confirmed in Hansi block. Quarantine affected cattle immediately. Movement ban in 10 km ring.",
         "Hisar", "Hansi", 10.0, 412, "ALL", rep1_time),
        ("LSD_OUTBREAK", "Lumpy Skin Disease Vector Alert",
         "आणंद जिले में लम्पी रोग के लक्षण पाए गए हैं। मक्खी-मच्छर भगाने हेतु गौशाला में नीम का धुआं करें। स्वस्थ पशुओं को गोट पॉक्स वैक्सीन लगवाएं।",
         "LSD Alert in Petlad block: Isolate nodular cattle. Spray vector repellents in barns. Contact local veterinary hospital.",
         "Anand", "Petlad", 8.0, 280, "ALL", rep4_time)
    ]
    cur.executemany("""
    INSERT INTO advisories_log (
        alert_type, title, message_hi, message_en, target_district, target_block,
        target_radius_km, farmers_notified_count, channel, broadcast_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, advisories_data)
    
    conn.commit()

# Query helper functions
def get_all_reports(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reports ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        try:
            r["symptoms"] = json.loads(r["symptoms_json"])
        except Exception:
            r["symptoms"] = []
    conn.close()
    return rows

def get_all_animals() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM animals ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_animal_by_tag(tag_number: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM animals WHERE tag_number = ?", (tag_number,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    animal = dict(row)
    
    # Vaccinations
    cur.execute("SELECT * FROM vaccinations WHERE animal_tag = ? ORDER BY administered_date DESC", (tag_number,))
    animal["vaccinations"] = [dict(r) for r in cur.fetchall()]
    
    # Treatments
    cur.execute("SELECT * FROM treatments WHERE animal_tag = ? ORDER BY treatment_date DESC", (tag_number,))
    animal["treatments"] = [dict(r) for r in cur.fetchall()]
    
    # Reports
    cur.execute("SELECT * FROM reports WHERE animal_tag = ? ORDER BY id DESC", (tag_number,))
    animal["reports"] = [dict(r) for r in cur.fetchall()]
    
    conn.close()
    return animal

def get_all_outbreaks() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM outbreaks WHERE containment_status = 'ACTIVE' ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_all_lab_referrals() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT lr.*, r.reporter_name, r.village, r.district, r.species
    FROM lab_referrals lr
    LEFT JOIN reports r ON lr.report_id = r.id
    ORDER BY lr.id DESC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_all_advisories() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM advisories_log ORDER BY id DESC LIMIT 20")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def insert_report(data: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cur = conn.cursor()
    
    report_uid = f"REP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    symptoms_json = json.dumps(data.get("symptoms", []))
    
    cur.execute("""
    INSERT INTO reports (
        report_uid, reporter_type, reporter_name, reporter_phone, animal_tag, species,
        village, block, district, latitude, longitude, symptoms_json, has_fever,
        affected_count, mortality_count, additional_notes, photo_url,
        triage_code, triage_name, confidence, urgency, is_zoonotic, containment_triggered,
        status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        report_uid,
        data.get("reporter_type", "FARMER"),
        data.get("reporter_name", "Anonymous Reporter"),
        data.get("reporter_phone", ""),
        data.get("animal_tag"),
        data.get("species", "Cattle"),
        data.get("village", "Unknown"),
        data.get("block", "Unknown"),
        data.get("district", "Unknown"),
        float(data.get("latitude", 28.6139)),
        float(data.get("longitude", 77.2090)),
        symptoms_json,
        1 if data.get("has_fever") else 0,
        int(data.get("affected_count", 1)),
        int(data.get("mortality_count", 0)),
        data.get("additional_notes", ""),
        data.get("photo_url"),
        data.get("triage_code"),
        data.get("triage_name"),
        int(data.get("confidence", 0)),
        data.get("urgency", "LOW"),
        1 if data.get("is_zoonotic") else 0,
        1 if data.get("containment_triggered") else 0,
        data.get("status", "PENDING_REVIEW")
    ))
    
    report_id = cur.lastrowid
    
    # Update animal status if animal tag provided
    if data.get("animal_tag"):
        new_status = "SICK" if data.get("mortality_count", 0) == 0 else "DECEASED"
        cur.execute("UPDATE animals SET health_status = ? WHERE tag_number = ?", (new_status, data.get("animal_tag")))
        
    conn.commit()
    conn.close()
    return report_id

def insert_lab_referral(data: Dict[str, Any]) -> str:
    conn = get_db_connection()
    cur = conn.cursor()
    barcode = f"LAB-{datetime.now().strftime('%Y%m%d')}-{cur.execute('SELECT COUNT(*) FROM lab_referrals').fetchone()[0] + 1:04d}"
    
    cur.execute("""
    INSERT INTO lab_referrals (
        sample_barcode, report_id, animal_tag, sample_type, suspect_disease,
        target_lab, collection_date, chain_of_custody_status, result_certified, result_notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        barcode,
        data.get("report_id"),
        data.get("animal_tag"),
        data.get("sample_type", "Blood / Swab"),
        data.get("suspect_disease", "FMD"),
        data.get("target_lab", "District Veterinary Lab"),
        datetime.now().strftime("%Y-%m-%d"),
        "SAMPLE_COLLECTED",
        "PENDING",
        data.get("notes", "Specimen collected in cold transport buffer")
    ))
    conn.commit()
    conn.close()
    return barcode

def update_lab_referral_status(barcode: str, status: str, result_certified: str, notes: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    UPDATE lab_referrals
    SET chain_of_custody_status = ?, result_certified = ?, result_notes = ?, tested_at = ?
    WHERE sample_barcode = ?
    """, (status, result_certified, notes, datetime.now().strftime("%Y-%m-%d %H:%M"), barcode))
    conn.commit()
    conn.close()

def insert_vaccination(data: Dict[str, Any]):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO vaccinations (
        animal_tag, vaccine_name, disease_targeted, dose_number, batch_number,
        manufacturer, administered_date, next_due_date, administered_by, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("animal_tag"),
        data.get("vaccine_name"),
        data.get("disease_targeted"),
        int(data.get("dose_number", 1)),
        data.get("batch_number", "VAC-" + datetime.now().strftime("%m%d")),
        data.get("manufacturer", "Government Veterinary Supply"),
        data.get("administered_date", datetime.now().strftime("%Y-%m-%d")),
        data.get("next_due_date"),
        data.get("administered_by", "Field Para-Vet"),
        "COMPLETED"
    ))
    conn.commit()
    conn.close()

def log_advisory(data: Dict[str, Any]):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO advisories_log (
        alert_type, title, message_hi, message_en, target_district, target_block,
        target_radius_km, farmers_notified_count, channel
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("alert_type"),
        data.get("title"),
        data.get("message_hi"),
        data.get("message_en"),
        data.get("target_district", "All"),
        data.get("target_block", "All"),
        float(data.get("target_radius_km", 10.0)),
        int(data.get("farmers_notified_count", 150)),
        data.get("channel", "ALL")
    ))
    conn.commit()
    conn.close()

# User Authentication Helpers
def authenticate_user(identifier: str, password: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT * FROM users 
    WHERE (username = ? OR phone = ?) AND password = ?
    """, (identifier, identifier, password))
    row = cur.fetchone()
    conn.close()
    if row:
        user = dict(row)
        del user["password"]
        return user
    return None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        user = dict(row)
        del user["password"]
        return user
    return None

def get_user_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    row = cur.fetchone()
    conn.close()
    if row:
        user = dict(row)
        del user["password"]
        return user
    return None

def get_demo_users() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, phone, role, full_name, designation, district, state FROM users")
    users = [dict(r) for r in cur.fetchall()]
    conn.close()
    return users

