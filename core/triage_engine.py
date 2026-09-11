"""
Pashu Suraksha - Syndromic Triage & Differential Diagnosis Engine
Evaluates clinical symptoms, mortality patterns, species vulnerability, and epidemiological risk
to flag suspected outbreaks, rank differential diagnoses, and trigger containment protocols.
"""

from typing import List, Dict, Any

DISEASE_KNOWLEDGE_BASE = {
    "FMD": {
        "name": "Foot-and-Mouth Disease (खुरपका और मुंहपका)",
        "code": "FMD",
        "species": ["Cattle", "Buffalo", "Sheep", "Goat", "Pig"],
        "zoonotic": False,
        "urgency": "CRITICAL",
        "incubation_days": "2-14 days",
        "hallmark_symptoms": {
            "oral_vesicles": 30,         # Blisters on tongue, gums, dental pad
            "hoof_lesions": 25,          # Blisters/erosions between hooves, coronet
            "excessive_salivation": 20,   # Drooling, ropey frothy saliva
            "lameness": 15,              # Stiff gait, reluctance to move
            "high_fever": 10             # Acute high fever (>104°F)
        },
        "secondary_symptoms": {
            "teat_lesions": 10,
            "drop_in_milk": 15,
            "loss_of_appetite": 5,
            "shivering": 5
        },
        "biohazard_alert": "HIGHLY CONTAGIOUS AIRBORNE SPREAD: Quarantine herd immediately. Restrict all animal and vehicle movement within a 10 km zone. Disinfect with 4% sodium carbonate or 2% citric acid.",
        "sample_required": "Vesicular fluid, oral epithelial tissue in phosphate buffered glycerin, heparinized blood",
        "ring_radius_km": 10,
        "containment_action": "Notify District Animal Husbandry Officer. Impose 3km infected zone ban on milk/meat movement. Initiate emergency ring vaccination."
    },
    "LSD": {
        "name": "Lumpy Skin Disease (गांठदार त्वचा रोग)",
        "code": "LSD",
        "species": ["Cattle", "Buffalo"],
        "zoonotic": False,
        "urgency": "HIGH",
        "incubation_days": "4-14 days",
        "hallmark_symptoms": {
            "skin_nodules": 35,          # Firm round cutaneous nodules 2-5cm across body
            "high_fever": 20,            # Fever 104-106°F
            "enlarged_lymph_nodes": 20,  # Prescapular and precrural lymphadenopathy
            "limb_edema": 15             # Swelling in legs, brisket, dewlap
        },
        "secondary_symptoms": {
            "ocular_nasal_discharge": 10,
            "drop_in_milk": 10,
            "emaciation": 5,
            "loss_of_appetite": 5
        },
        "biohazard_alert": "VECTOR-BORNE TRANSMISSION (Biting flies, Culicoides midges, ticks). Isolate affected cattle under mosquito nets. Apply topical ectoparasiticides.",
        "sample_required": "Skin nodule biopsies/scabs, EDTA blood, nasal swabs in viral transport medium",
        "ring_radius_km": 5,
        "containment_action": "Segregate infected cattle. Administer Goat Pox vaccine (heterologous protection) to healthy animals in 5km buffer."
    },
    "PPR": {
        "name": "Peste des Petits Ruminants (बकरी और भेड़ की प्लेग)",
        "code": "PPR",
        "species": ["Goat", "Sheep"],
        "zoonotic": False,
        "urgency": "CRITICAL",
        "incubation_days": "3-6 days",
        "hallmark_symptoms": {
            "erosive_stomatitis": 30,    # Necrotic sores in mouth, foul breath
            "severe_diarrhea": 25,       # Foul-smelling watery profuse diarrhea
            "mucopurulent_discharge": 20,# Thick crusting eye and nasal discharge
            "high_fever": 15,            # Sudden fever >104°F
            "pneumonia_dyspnea": 15      # Rapid labored breathing, coughing
        },
        "secondary_symptoms": {
            "loss_of_appetite": 5,
            "hypothermia_pre_death": 10,
            "dehydration": 10
        },
        "biohazard_alert": "VERY HIGH MORTALITY IN SMALL RUMINANTS (Up to 80%). Contagious through close contact, shared grazing, and water troughs.",
        "sample_required": "Ocular/nasal swabs, EDTA blood, mesenteric lymph nodes or spleen tissue post-mortem",
        "ring_radius_km": 5,
        "containment_action": "Strict quarantine of goat/sheep flocks. Halt village livestock haats/fairs. Deploy homologous PPR live attenuated vaccine."
    },
    "ANTHRAX": {
        "name": "Anthrax (गिलटी रोग / विषहरि)",
        "code": "ANTHRAX",
        "species": ["Cattle", "Buffalo", "Sheep", "Goat", "Pig", "Equine"],
        "zoonotic": True,
        "urgency": "CRITICAL",
        "incubation_days": "1-7 days",
        "hallmark_symptoms": {
            "sudden_unexplained_death": 40, # Peracute sudden death without prior signs
            "unclotted_dark_blood": 30,     # Oozing tarry uncoagulated blood from mouth, nose, anus
            "incomplete_rigor_mortis": 20,  # Carcass fails to stiffen
            "rapid_bloat": 15               # Rapid post-mortem tympany
        },
        "secondary_symptoms": {
            "high_fever": 10,
            "subcutaneous_edema": 15,
            "respiratory_distress": 10
        },
        "biohazard_alert": "EXTREME DANGER - ZOONOTIC & SPORE-FORMING BACTERIUM! DO NOT OPEN OR CUT THE CARCASS. Opening exposes vegetative cells to oxygen, creating spores that persist in soil for decades. Wear PPE; bury carcass >2m deep covered with quicklime or incinerate.",
        "sample_required": "Peripheral ear-vein blood smear on glass slide (do NOT collect blood vacutainers by opening vein). Fixed slide for Gram/McFadyean staining.",
        "ring_radius_km": 10,
        "containment_action": "Alert Human Public Health authorities immediately. Quarantine farm. Ring vaccinate susceptible livestock with Anthrax spore vaccine."
    },
    "HS": {
        "name": "Hemorrhagic Septicemia (गलघोंटू रोग)",
        "code": "HS",
        "species": ["Cattle", "Buffalo"],
        "zoonotic": False,
        "urgency": "HIGH",
        "incubation_days": "1-3 days",
        "hallmark_symptoms": {
            "throat_swelling": 35,          # Hot, painful swelling in submandibular/throat region
            "stertorous_breathing": 25,     # Harsh snoring, difficult suffocating respiration
            "high_fever": 20,               # Hyperthermia (106-107°F)
            "tongue_protrusion": 15         # Swollen cyanotic tongue protruding
        },
        "secondary_symptoms": {
            "salivation": 10,
            "nasal_discharge": 10,
            "sudden_collapse": 15
        },
        "biohazard_alert": "Acute, rapid fatal disease predominantly in buffaloes during monsoon/post-monsoon stress. Mortality reaches 90% if untreated in first 12 hours.",
        "sample_required": "Heart blood swabs from carcass, bone marrow, or blood smear for Pasteurella multocida bipolar staining",
        "ring_radius_km": 3,
        "containment_action": "Immediate parenteral antibiotic therapy (Oxytetracycline / Ceftiofur) for in-contact animals. Mass pre-monsoon HS alum precipitated vaccination."
    },
    "BLACKLEG": {
        "name": "Blackleg / Black Quarter (लंगड़ा बुखार / चरचरी)",
        "code": "BLACKLEG",
        "species": ["Cattle", "Buffalo", "Sheep"],
        "zoonotic": False,
        "urgency": "HIGH",
        "incubation_days": "1-3 days",
        "hallmark_symptoms": {
            "crepitant_swelling": 35,       # Crackling / gaseous swelling on thigh, shoulder, neck
            "severe_lameness": 25,          # Inability to bear weight on affected limb
            "high_fever": 20,               # Fever 105°F followed by subnormal temperature
            "cold_painless_muscle": 15      # Swelling turns dry, dark, cold and painless
        },
        "secondary_symptoms": {
            "depression": 10,
            "rapid_breathing": 10,
            "tremors": 5
        },
        "biohazard_alert": "Endogenous soil-borne Clostridial infection in young calves (6-24 months). Spores in soil enter via ingestion or muscle trauma.",
        "sample_required": "Affected muscle tissue smear or aspirate under anaerobic conditions, fluorescent antibody test (FAT)",
        "ring_radius_km": 3,
        "containment_action": "Prophylactic penicillin treatment for in-contact young stock. Annual BQ polyvalent vaccination."
    },
    "BRUCELLOSIS": {
        "name": "Brucellosis (संक्रामक गर्भपात)",
        "code": "BRUCELLOSIS",
        "species": ["Cattle", "Buffalo", "Sheep", "Goat", "Pig"],
        "zoonotic": True,
        "urgency": "MEDIUM",
        "incubation_days": "2-4 weeks",
        "hallmark_symptoms": {
            "late_term_abortion": 40,       # Abortion in 6th-8th month of gestation
            "retained_placenta": 25,        # Retained fetal membranes, metritis
            "orchitis_epididymitis": 20,    # Swollen testicles in breeding bulls
            "hygroma": 15                   # Chronic joint swelling (carpal hygroma)
        },
        "secondary_symptoms": {
            "drop_in_milk": 15,
            "infertility": 15,
            "vaginal_discharge": 10
        },
        "biohazard_alert": "MAJOR ZOONOSIS (Undulant fever in humans, Malta fever). Transmitted through raw unpasteurized milk, aborted fetus, placenta, and uterine discharge. Handlers must wear gloves and face shields.",
        "sample_required": "Serum for Rose Bengal Plate Test (RBPT), milk ring test (MRT), fetal stomach contents, cotyledon smear",
        "ring_radius_km": 2,
        "containment_action": "Screen herd with RBPT/ELISA. Segregate reactors. Vaccinate female calves aged 4-8 months with Brucella abortus S19 vaccine once in lifetime."
    },
    "AVIAN_FLU": {
        "name": "Avian Influenza / Bird Flu (बर्ड फ्लू)",
        "code": "AVIAN_FLU",
        "species": ["Poultry", "Duck", "Turkey"],
        "zoonotic": True,
        "urgency": "CRITICAL",
        "incubation_days": "1-5 days",
        "hallmark_symptoms": {
            "sudden_mass_mortality": 40,    # Sudden catastrophic death of birds within hours
            "cyanosis_comb_wattles": 25,    # Comb, wattles, and legs turn dark purple/blue
            "facial_head_edema": 20,        # Severe swelling of head, eyelids, neck
            "greenish_diarrhea": 15         # Profuse watery diarrhea
        },
        "secondary_symptoms": {
            "respiratory_distress": 10,
            "total_egg_drop": 15,
            "torticolis_paralysis": 10
        },
        "biohazard_alert": "POTENTIAL PANDEMIC THREAT (H5N1 / H5N6 / H9N2). Highly infectious to domestic poultry and transmissible to humans with high case fatality. Prohibit bird and poultry manure transport.",
        "sample_required": "Tracheal/cloacal swabs in viral transport medium with antibiotics, packaged in triple container cold chain on dry ice to NIHSAD Bhopal",
        "ring_radius_km": 10,
        "containment_action": "Notify State Animal Husbandry Department and District Collector. 1 km Culling Zone protocol; 10 km Surveillance Zone. Prohibit all poultry trade."
    },
    "ASF": {
        "name": "African Swine Fever (अफ्रीकी स्वाइन फीवर)",
        "code": "ASF",
        "species": ["Pig"],
        "zoonotic": False,
        "urgency": "CRITICAL",
        "incubation_days": "4-19 days",
        "hallmark_symptoms": {
            "high_fever": 25,               # Severe fever (105-108°F)
            "cutaneous_hemorrhages": 30,    # Bluish-red skin patches on ears, snout, abdomen, legs
            "sudden_high_mortality": 30,    # Mortality approaching 100% in swine
            "bloody_diarrhea": 15           # Hemorrhagic gastroenteritis, vomiting
        },
        "secondary_symptoms": {
            "huddling_weakness": 10,
            "respiratory_distress": 10,
            "abortion": 10
        },
        "biohazard_alert": "VIRAL HEMORRHAGIC DISEASE OF SWINE. Extremely resilient virus surviving in cured meats and swill feed for months. No approved vaccine available.",
        "sample_required": "EDTA blood, spleen, tonsils, lymph nodes sent in leak-proof cold container to ICAR-NIHSAD",
        "ring_radius_km": 10,
        "containment_action": "Strict ban on movement of pigs, pork products, and feed. 1 km infected zone culling and bio-secure carcass burial. Disinfect with sodium hypochlorite."
    },
    "RABIES": {
        "name": "Rabies (रेबीज / अलर्क रोग)",
        "code": "RABIES",
        "species": ["Dog", "Cattle", "Buffalo", "Sheep", "Goat", "Equine"],
        "zoonotic": True,
        "urgency": "CRITICAL",
        "incubation_days": "2 weeks to 6 months",
        "hallmark_symptoms": {
            "abnormal_behavior_aggression": 35, # Biting objects, frantic bellowing, restlessness
            "excessive_salivation": 25,         # Profuse frothing at mouth, choking sounds
            "pharyngeal_paralysis": 20,         # Inability to swallow, jaw dropped
            "progressive_hind_paralysis": 20    # Incoordination, knuckling, recumbency
        },
        "secondary_symptoms": {
            "tenesmus": 10,
            "hyperesthesia": 10,
            "altered_vocalization": 15
        },
        "biohazard_alert": "100% FATAL ZOONOSIS. Neurotropic Lyssavirus transmitted via bite or saliva contact with broken skin or mucous membranes.",
        "sample_required": "Full brain (hippocampus and cerebellum) in 50% buffered glycerol-saline to approved rabies diagnostic lab. Wear rabies-grade PPE.",
        "ring_radius_km": 2,
        "containment_action": "Isolate suspect animal in secure escape-proof pen. Anyone bitten or exposed must undergo immediate wound washing with soap for 15 min and Post-Exposure Prophylaxis (PEP)."
    }
}


def assess_symptoms(
    species: str,
    symptoms: List[str],
    has_fever: bool = False,
    mortality_count: int = 0,
    affected_count: int = 1,
    additional_notes: str = ""
) -> Dict[str, Any]:
    """
    Evaluates observed symptoms against the disease knowledge base and returns a scored differential diagnosis.
    """
    candidate_scores = []
    
    # Normalize inputs
    norm_species = species.strip().capitalize()
    symptoms_set = set(s.strip().lower() for s in symptoms)
    
    for code, info in DISEASE_KNOWLEDGE_BASE.items():
        # Species match check
        species_matched = any(
            norm_species.lower() in s.lower() or s.lower() in norm_species.lower() 
            for s in info["species"]
        )
        if not species_matched:
            continue
            
        score = 0
        max_possible_hallmark = sum(info["hallmark_symptoms"].values())
        matched_hallmarks = []
        matched_secondaries = []
        
        # Check hallmarks
        for symptom_key, weight in info["hallmark_symptoms"].items():
            if symptom_key == "high_fever" and has_fever:
                score += weight
                matched_hallmarks.append("High Fever")
            elif symptom_key in symptoms_set:
                score += weight
                matched_hallmarks.append(symptom_key.replace("_", " ").title())
                
        # Check secondary symptoms
        for symptom_key, weight in info["secondary_symptoms"].items():
            if symptom_key in symptoms_set:
                score += weight
                matched_secondaries.append(symptom_key.replace("_", " ").title())
                
        # Bonus weighting for mortality indicators
        if mortality_count > 0:
            if code in ["ANTHRAX", "AVIAN_FLU", "ASF", "HS", "PPR"]:
                score += 15
                if "sudden_unexplained_death" in symptoms_set or "sudden_mass_mortality" in symptoms_set:
                    score += 20

        # Compute confidence percentage (capped at 98% for syndromic screen without PCR)
        confidence = min(round((score / max(max_possible_hallmark, 50)) * 100), 98)
        
        if score > 15:
            candidate_scores.append({
                "code": code,
                "name": info["name"],
                "confidence": confidence,
                "raw_score": score,
                "zoonotic": info["zoonotic"],
                "urgency": info["urgency"],
                "incubation_days": info["incubation_days"],
                "matched_hallmarks": matched_hallmarks,
                "matched_secondaries": matched_secondaries,
                "biohazard_alert": info["biohazard_alert"],
                "sample_required": info["sample_required"],
                "ring_radius_km": info["ring_radius_km"],
                "containment_action": info["containment_action"]
            })
            
    # Sort candidates by confidence descending
    candidate_scores.sort(key=lambda x: x["confidence"], reverse=True)
    
    if not candidate_scores:
        # Fallback / General non-specific syndromic condition
        return {
            "status": "NON_SPECIFIC",
            "top_diagnosis": {
                "code": "GENERAL_MALADY",
                "name": "General Non-Specific Illness / Routine Morbidity",
                "confidence": 35,
                "urgency": "LOW",
                "zoonotic": False,
                "biohazard_alert": "No immediate critical epidemic hallmark detected. Maintain clean hygiene, provide clean drinking water, and monitor animal vitals for 24-48 hours.",
                "sample_required": "Routine complete blood count (CBC) or fecal sample if diarrhea persists",
                "ring_radius_km": 0,
                "containment_action": "Consult nearest Veterinary Dispensary for supportive treatment (antipyretics, electrolytes)."
            },
            "differential_diagnoses": [],
            "urgency": "LOW",
            "is_zoonotic": False,
            "trigger_containment_ring": False,
            "containment_ring_radius_km": 0
        }
        
    top = candidate_scores[0]
    
    # Urgency determination
    overall_urgency = top["urgency"]
    if top["zoonotic"] or mortality_count >= 2 or top["confidence"] >= 70:
        if overall_urgency != "CRITICAL":
            overall_urgency = "HIGH"
            
    trigger_ring = top["confidence"] >= 60 and top["urgency"] in ["CRITICAL", "HIGH"]
    
    return {
        "status": "SUSPECTED_OUTBREAK" if trigger_ring else "CLINICAL_ALERT",
        "top_diagnosis": top,
        "differential_diagnoses": candidate_scores[1:4],
        "urgency": overall_urgency,
        "is_zoonotic": top["zoonotic"],
        "trigger_containment_ring": trigger_ring,
        "containment_ring_radius_km": top["ring_radius_km"] if trigger_ring else 0,
        "biohazard_alert": top["biohazard_alert"],
        "recommended_sample": top["sample_required"],
        "recommended_containment": top["containment_action"]
    }
