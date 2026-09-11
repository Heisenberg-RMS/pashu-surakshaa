# पशु सुरक्षा (Pashu Suraksha)
### Unified Real-Time Animal Health Surveillance, Early Warning & Decision-Support System

**Pashu Suraksha** is a scalable, offline-resilient digital animal health intelligence platform designed for livestock farmers, para-veterinarians, veterinary officers, and state animal husbandry departments across village, block, and district levels.

---

## Key Capabilities & Features

### 1. Multi-Channel Reporting & Offline Resilience
- **Farmer & Field Worker PWA**: Touch-friendly symptom selector with anatomical visual aids and multi-species support (Cattle, Buffalo, Goat, Sheep, Pig, Poultry).
- **Zero-Connectivity Offline Queue**: Uses browser **IndexedDB** to store symptom and mortality reports when internet access is unavailable. Automatically reconciles and syncs with the central server upon reconnection.
- **Simulated Low-Bandwidth IVR Hotline (1962)**: Interactive DTMF dialpad simulator allowing farmers with basic 2G feature phones to report disease symptoms via keypad presses and listen to synthesized local language advisories.

### 2. Rule-Based & AI-Assisted Syndromic Triage Engine
- Real-time scoring and differential diagnosis for 10 high-impact livestock diseases:
  - **Foot-and-Mouth Disease (FMD)** (खुरपका और मुंहपका)
  - **Lumpy Skin Disease (LSD)** (गांठदार त्वचा रोग)
  - **Peste des Petits Ruminants (PPR)** (बकरी-भेड़ की प्लेग)
  - **Anthrax** (गिलटी रोग / विषहरि) — *Critical Zoonotic Biohazard Alert*
  - **Hemorrhagic Septicemia (HS)** (गलघोंटू रोग)
  - **Blackleg / Black Quarter (BQ)** (लंगड़ा बुखार / चरचरी)
  - **Brucellosis** (संक्रामक गर्भपात) — *Zoonotic Alert*
  - **Avian Influenza (H5N1)** (बर्ड फ्लू)
  - **African Swine Fever (ASF)** (अफ्रीकी स्वाइन फीवर)
  - **Rabies** (रेबीज / अलर्क रोग) — *Fatal Zoonosis*
- Instant differential diagnosis ranking with match confidence percentage, urgency classification, and specimen collection instructions.

### 3. Geospatial Outbreak Mapping & Dynamic Containment Rings
- Interactive **Leaflet.js GIS Map** displaying active outbreak clusters, village epicenters, veterinary dispensaries, and diagnostic laboratories.
- Automated containment buffer calculations following WOAH/DAHD protocols:
  - **3 km Infected Zone Ring**: Red shaded zone enforcing strict ban on animal transport, milk/meat trade, and livestock fairs.
  - **10 km Surveillance / Buffer Zone Ring**: Yellow dashed ring mandating ring vaccination and active syndromic search.

### 4. Environmental & Meteorological Vector Risk Modeling
- Correlates live meteorological parameters (temperature, relative humidity, 24-hour rainfall, wind velocity) with pathogen transmission dynamics:
  - **Culicoides Midge & Tick Breeding Suitability**: Identifies vector-borne outbreak risks (LSD, Theileriosis, Bluetongue).
  - **FMD Airborne Plume Dispersion Potential**: Computes downwind airborne spread radius under current atmospheric conditions.
  - **HS Waterlogging Stress**: Flags high-risk low-lying grazing pastures prone to *Pasteurella multocida* flare-ups during monsoon stress.

### 5. Animal & Herd Electronic Health Records (EHR)
- Unique Animal Identification (12-digit ear tag / INAPH format) and RFID tag tracking.
- **Digital Pashu Swasthya Card** (Animal Health Passport).
- Lifetime vaccination history with automated due date tracking and overdue alerts.
- **Antimicrobial Stewardship & Withdrawal Tracker**: Warns farmers and officers when treated animals are under drug withdrawal periods, preventing antibiotic residues in milk and meat.

### 6. Laboratory Referral & Chain-of-Custody Tracking
- Digital sample requisition generation with unique barcode tracking (`LAB-YYYYMMDD-XXXX`).
- Step-by-step chain-of-custody progress tracker:
  `Sample Collected` ➔ `In Cold-Chain Transit` ➔ `Received at Reference Lab` ➔ `PCR / ELISA in Progress` ➔ `Result Certified`.
- Direct escalation to State Disease Diagnostic Laboratories (SDDL) and ICAR-NIHSAD.

### 7. Multilingual Voice Advisories & Targeted SMS Broadcasts
- Pre-compiled and dynamic biosecurity advisories in **7 Indian languages**:
  - हिन्दी (Hindi)
  - English (Indian)
  - ਪੰਜਾਬੀ (Punjabi)
  - বাংলা (Bengali)
  - मराठी (Marathi)
  - తెలుగు (Telugu)
  - தமிழ் (Tamil)
- Integrated in-browser **Web Speech API** Text-to-Speech (TTS) voice player for non-literate livestock owners.
- Simulated geo-targeted emergency SMS broadcast dispatching alerts to all registered farmers within a quarantine perimeter.

### 8. AI Computer Vision Lesion Diagnostics
- **Smart Camera Lens & Image Upload**: Capture or upload photos of cattle, buffalo, sheep, goats, or poultry showing suspected symptoms.
- **Hallmark Lesion Recognition**:
  - **LSD Nodules**: Skin nodules, circumscribed firm lumps across neck, dewlap, and back.
  - **FMD Vesicles**: Ruptured vesicles, tongue erosions, dental pad ulcers, and interdigital cleft wounds with ropy salivation.
  - **Acute Mastitis**: Swollen, painful, asymmetric udders with curdled/bloody milk discharge.
  - **Tick Infestations**: Ectoparasite clusters (*Hyalomma/Rhipicephalus*) carrying tick-borne blood protozoa.
  - **Suspected Anthrax Carcass**: Tar-like non-clotted orificial hemorrhage and lack of rigor mortis (*Critical Biohazard*).
  - **HS Throat Edema**: Acute inflammatory neck and brisket swelling with respiratory stridor.
- **Automated Clinical Workflow**: Returns confidence scores (60-98%), pathognomonic lesion markers, immediate home care / wound dressing instructions, required laboratory specimen types, and one-tap transfer to outbreak reports.

### 9. Conversational Veterinary AI Chatbot ("Pashu AI Sahayak")
- **24/7 Bilingual Conversational Advisor**: Accessible in **Hindi** and **English**.
- **Comprehensive Livestock Knowledge Base**: Handles queries on disease symptoms, immediate first-aid, safe herbal formulations, biosecurity, antibiotic withdrawal periods (milk/meat safety), and national vaccination timelines.
- **Emergency Life-Threat Detection**: Automatically flags urgent life-threatening crises (acute rumen bloat/afara, peracute deaths) with bold first-response instructions.
- **Speech Audio Playback**: Read-aloud button on every message powered by Web Speech API for low-literacy farmers.
- **Contextual Suggestions**: Dynamic quick-reply chips allowing one-tap follow-ups without manual typing.

### 10. App-Friendly & Mobile Web Responsive Design
- **Mobile Bottom Navigation Bar**: Fixed bottom bar on viewports `< 850px` for seamless single-thumb switching between Dashboard, Camera AI Lens, Triage Form, GIS Containment Map, and Chatbot.
- **Direct Camera Integration**: Native HTML5 `<input type="file" capture="environment">` directly launches the rear camera on Android and iOS devices.
- **Touch Targets & Slide-up Drawers**: 48px+ minimum touch targets, collapsible cards, sliding chatbot bottom sheet, and responsive data tables designed for field smartphones.

### 11. Multi-Role Authentication & Login Options
- **Quick 1-Click Persona Switch**: Instant demo login as any key stakeholder:
  - 👨‍🌾 **Farmer / Livestock Owner**: Ramcharan Yadav (`farmer` / `farm123`)
  - 🩺 **Field Para-Vet / Pashu Sakhi**: Ramesh Kumar (`paravet` / `vet123`)
  - 🏛️ **District Veterinary Officer (DVO)**: Dr. Sunil Bishnoi (`dvo_hisar` / `dvo123`)
  - 📊 **State Directorate**: Dr. A. K. Sharma (`director_ah` / `state123`)
- **Official Credentials Login**: Username and password authentication with encrypted sessions.
- **Rural Mobile OTP Login**: Designed for livestock owners without passwords — enter 10-digit mobile number to receive simulated OTP (`1962`) and log in immediately.
- **Dynamic Context Synchronization**: Pre-populates reporter details, filters animal EHR records, and tailors UI workflows based on authenticated identity.

### 12. Role-Based Decision Support
- **Livestock Owner (पशुपालक)**: Track individual herd health cards, check withdrawal periods, listen to voice advisories.
- **Field Para-Vet / Pashu Sakhi**: Log village visits, offline report synchronization, rapid field triage.
- **District Veterinary Officer (DVO)**: Review outbreak clusters, activate containment rings, authorize diagnostic sample referrals.
- **State Animal Husbandry Directorate**: Real-time epidemiological curves, syndromic breakdown, and emergency vaccine stockpile tracking.

---

## Directory Structure

```
pashu-suraksha/
├── app.py                      # Flask REST API & Web Application
├── requirements.txt            # Python dependencies
├── README.md                   # System documentation
├── database/
│   ├── db.py                   # SQLite schemas, connection pool & seed generator
│   └── pashu_suraksha.db       # Database file
├── core/
│   ├── triage_engine.py        # Rule-based & AI syndromic triage engine
│   ├── vision_engine.py        # Computer vision pathology & lesion diagnostic engine
│   ├── chatbot_engine.py       # Conversational AI veterinary advisor ("Pashu AI Sahayak")
│   ├── cluster_detector.py     # Spatio-temporal cluster & outbreak detection
│   ├── weather_risk.py         # Environmental & vector risk index calculation
│   └── advisory_generator.py   # Multilingual text & voice advisory engine
├── static/
│   ├── css/style.css           # Responsive mobile-first stylesheet & bottom nav
│   ├── js/
│   │   ├── app.js              # Central UI controller, charts, auth & state
│   │   ├── vision_ui.js        # Camera lens, upload dropzone & lesion scanner UI
│   │   ├── chatbot_ui.js       # Conversational chatbot drawer & speech playback
│   │   ├── map_ui.js           # Leaflet.js GIS map & containment rings
│   │   ├── triage_ui.js        # Symptom picker & real-time differential diagnosis
│   │   ├── ehr_ui.js           # Animal health cards & vaccination logs
│   │   ├── lab_ui.js           # Chain-of-custody laboratory referral tracker
│   │   ├── ivr_ui.js           # Telephone keypad & hotline simulator
│   │   ├── voice_advisory.js   # Web Speech API TTS audio player
│   │   └── offline_sync.js     # IndexedDB offline storage & auto-sync
│   ├── icon.png                # PWA App Icon
│   ├── manifest.json           # PWA Web App Manifest
│   └── sw.js                   # Service worker for offline asset caching
├── templates/
│   └── index.html              # Unified Single-Page Application interface
└── tests/
    └── test_api.py             # Automated unit & integration tests
```

---

## Running the Application

### 1. Launch the Server
Execute the following command in PowerShell:
```powershell
& "C:\Users\admin\AppData\Local\Python\pythoncore-3.14-64\python.exe" app.py
```

### 2. Access in Browser
Open your browser and navigate to:
```
http://localhost:5000
```

### 3. Run Automated Tests
```powershell
& "C:\Users\admin\AppData\Local\Python\pythoncore-3.14-64\python.exe" tests/test_api.py
```
