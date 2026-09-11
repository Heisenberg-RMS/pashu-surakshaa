"""
Pashu Suraksha - Intelligent Veterinary Chatbot Engine ("Pashu AI Sahayak")
Conversational AI advisor for livestock keepers, field veterinarians, and para-vets.
Handles clinical symptoms, emergency first-aid, vaccination timelines, withdrawal periods, and biosecurity.
"""

from typing import Dict, Any, List
import re

CHATBOT_KNOWLEDGE = [
    {
        "keywords": ["fmd", "muh", "khur", "chhale", "blister", "drooling", "saliva", "mouth", "hoof", "feet", "foot", "खुरपका", "मुंहपका", "मुंह", "खुर", "छाले", "लार", "पैर"],
        "intent": "FMD_TREATMENT",
        "title": "Foot-and-Mouth Disease (खुरपका-मुंहपका)",
        "is_emergency": True,
        "reply_en": (
            "Foot-and-Mouth Disease (FMD) is a highly contagious viral infection. "
            "**Immediate First Aid Steps:**\n"
            "1. **Isolate Animal:** Segregate infected cattle immediately; halt shared grazing.\n"
            "2. **Oral Care:** Wash mouth ulcers twice daily with mild potassium permanganate solution (1:1000 ratio in water) or 2% baking soda.\n"
            "3. **Hoof Care:** Wash feet with 2% copper sulphate (नीला थोथा) solution. Apply zinc oxide or turmeric-mustard oil paste to prevent maggots.\n"
            "4. **Soft Feed:** Provide cooked rice gruel, boiled crushed wheat, or soft green grass with jaggery.\n"
            "5. **Vaccination:** Healthy animals must receive Raksha-Ovac FMD vaccine bi-annually (before monsoon & winter)."
        ),
        "reply_hi": (
            "खुरपका-मुंहपका (FMD) एक अति संक्रामक विषाणु जनित रोग है।\n"
            "**प्राथमिक उपचार एवं देखभाल:**\n"
            "1. **पशु को अलग रखें:** बीमार पशु को स्वस्थ पशुओं से तुरंत अलग बांधें।\n"
            "2. **मुंह के छालों की सफाई:** 1:1000 लाल दवा (पोटैशियम परमैंगनेट) या 2% मीठा सोडा के हल्के घोल से दिन में दो बार मुंह धोएं।\n"
            "3. **खुरों की देखभाल:** खुरों को 2% नीला थोथा के पानी से धोएं तथा तारपीन तेल व नीम का लेप लगाएं ताकि कीड़े न पड़ें।\n"
            "4. **सुपाच्य आहार:** पशु को दलिया, पका हुआ चावल, व गुड़ का पानी पिलाएं।\n"
            "5. **टीकाकरण:** स्वस्थ पशुओं को वर्ष में दो बार (अप्रैल-मई और सितम्बर-अक्टूबर) FMD का टीका अवश्य लगवाएं।"
        ),
        "suggested_questions": [
            "FMD में दूध पीना सुरक्षित है क्या?",
            "पशु के खुर में कीड़े पड़ गए हैं तो क्या करें?",
            "नजदीकी पशु अस्पताल का फोन नंबर क्या है?"
        ]
    },
    {
        "keywords": ["lsd", "lumpy", "nodule", "gath", "skin", "gaanth", "लम्पी", "गांठ", "त्वचा", "फफोले", "दाना", "दाने"],
        "intent": "LSD_CARE",
        "title": "Lumpy Skin Disease (गांठदार त्वचा रोग)",
        "is_emergency": False,
        "reply_en": (
            "Lumpy Skin Disease (LSD) is transmitted primarily by biting flies, mosquitoes, and ticks.\n"
            "**Control & Management:**\n"
            "1. **Vector Control:** Spray neem seed kernel extract or fly repellents (camphor in coconut oil) on animals and in the cattle shed.\n"
            "2. **Wound Dressing:** For ruptured nodules, apply povidone-iodine spray or turmeric-mustard oil paste to prevent secondary bacterial infection.\n"
            "3. **Immunity Booster:** Give a herbal mixture of betel leaves, black pepper, garlic, and jaggery twice daily for 5 days.\n"
            "4. **Vaccination:** In unaffected herds, administer Goat Pox vaccine (3ml SC) to provide cross-protection."
        ),
        "reply_hi": (
            "लम्पी स्किन डिजीज (गांठदार त्वचा रोग) मक्खी, मच्छर और किलनी के काटने से फैलता है।\n"
            "**रोकथाम व देशी उपचार:**\n"
            "1. **मक्खी-मच्छर नियंत्रण:** गौशाला में शाम को नीम की सूखी पत्तियों का धुआं करें। पशु के शरीर पर नीम का तेल या कपूर का लेप लगाएं।\n"
            "2. **घाव का उपचार:** फटी हुई गांठों पर बीटाडीन या हल्दी-सरसों के तेल का लेप लगाएं।\n"
            "3. **रोग प्रतिरोधक काढ़ा:** पान का पत्ता, 10 काली मिर्च, लहसुन की 2 कलियां और गुड़ पीसकर दिन में दो बार 5 दिन तक खिलाएं।\n"
            "4. **टीकाकरण:** नजदीकी पशु अस्पताल से स्वस्थ पशुओं को गोट पॉक्स वैक्सीन (Goat Pox) लगवाएं।"
        ),
        "suggested_questions": [
            "लम्पी रोग का देशी काढ़ा कैसे बनाएं?",
            "लम्पी पीड़ित गाय का दूध उबालकर पी सकते हैं?",
            "गोट पॉक्स का टीका कब लगवाना चाहिए?"
        ]
    },
    {
        "keywords": ["bloat", "pet", "phoolna", "afra", "gas", "tympany", "अफारा", "पेट फूलना"],
        "intent": "BLOAT_EMERGENCY",
        "title": "Acute Rumen Bloat / Tympany (अफारा)",
        "reply_en": (
            "🚨 **URGENT EMERGENCY: Acute Bloat in Ruminants**\n"
            "Excessive gas in the rumen can compress the lungs and cause suffocation within hours.\n"
            "**Immediate Action:**\n"
            "1. Keep animal's head elevated. Keep animal standing and walking slowly.\n"
            "2. Fast Relief Drench: Administer 200ml sweet mustard oil mixed with 20g hing (asafoetida) and 25ml turpentine oil.\n"
            "3. Place a wooden bit or thick rope horizontally across the mouth behind teeth to induce continuous salivation and eructation (belching).\n"
            "4. Severe Emergency: If animal collapses and gasps for breath, emergency trocar and cannula puncture into left paralumbar fossa is required by a veterinarian."
        ),
        "reply_hi": (
            "🚨 **आपातकालीन स्थिति: पशु का पेट फूलना (अफारा)**\n"
            "पेट में अधिक गैस बनने से फेफड़ों पर दबाव पड़ता है और सांस रुकने का खतरा होता है।\n"
            "**तत्काल राहत के उपाय:**\n"
            "1. पशु को बैठने न दें, उसे धीरे-धीरे टहलाते रहें तथा सिर को ऊपर की ओर रखें।\n"
            "2. **देशी दवा:** 200 मिली मीठा सरसों का तेल, 20 ग्राम हींग और 50 ग्राम सोंठ का घोल बनाकर तुरंत पिलाएं।\n"
            "3. मुंह में आड़ी लकड़ी या रस्सी बांधें ताकि पशु मुंह चलाए और डकार के जरिए गैस बाहर निकले।\n"
            "4. यदि पशु तड़प रहा हो तो तुरंत नजदीकी पशु चिकित्सक को बुलाएं।"
        ),
        "suggested_questions": [
            "अफारा किस कारण से होता है?",
            "सड़े-गले चारे से पेट फूलने पर क्या करें?",
            "ट्रोकार कैन्युला कब इस्तेमाल किया जाता है?"
        ]
    },
    {
        "keywords": ["mastitis", "thanela", "than", "doodh", "chhihda", "clot", "थनैल", "दूध में खून"],
        "intent": "MASTITIS_CARE",
        "title": "Mastitis / Udder Infection (थनैला रोग)",
        "reply_en": (
            "Mastitis causes severe milk loss and permanent udder damage if untreated.\n"
            "**Care Instructions:**\n"
            "1. **Frequent Milking:** Strip the affected quarter completely every 2 hours into a separate container (discard milk).\n"
            "2. **Cold Therapy:** Apply ice packs or cold water splash on the hot udder to reduce pain.\n"
            "3. **Teat Dip:** Dip teats in 0.5% povidone-iodine after milking.\n"
            "4. **Antibiotic Stewardship:** If treated with intramammary antibiotics, **DO NOT SELL OR CONSUME MILK** for 72-96 hours (withdrawal period)."
        ),
        "reply_hi": (
            "थनैला (Mastitis) से पशु के अयन में सूजन, दर्द और दूध में छीछड़े/खून आने लगता है।\n"
            "**जरूरी सावधानियां:**\n"
            "1. **दूध बार-बार निकालें:** प्रभावित थन का दूध हर 2 घंटे में अलग बर्तन में निकालें और फेंक दें।\n"
            "2. **ठंडी सिकाई:** थन गर्म व सूजा हो तो बर्फ या ठंडे पानी से सिकाई करें।\n"
            "3. **दूध की स्वच्छता:** दुहने के बाद थनों को लाल दवा या आयोडीन के घोल में डुबोएं (Teat Dip)।\n"
            "4. **सावधानी:** थन में एंटीबायोटिक दवा चढ़ाने के बाद कम से कम 3 से 4 दिन तक वह दूध मनुष्यों के पीने योग्य नहीं होता।"
        ),
        "suggested_questions": [
            "थनैला रोग से बचाव कैसे करें?",
            "दूध निकालने का सही तरीका क्या है?",
            "एंटीबायोटिक का असर कितने दिन रहता है?"
        ]
    },
    {
        "keywords": ["withdrawal", "dawa", "doodh", "mans", "safety", "antibiotic", "दवा का असर"],
        "intent": "WITHDRAWAL_STEWARDSHIP",
        "title": "Antimicrobial Withdrawal Period (दवा निकासी अवधि)",
        "reply_en": (
            "**Why Antimicrobial Withdrawal Matters:**\n"
            "When cows/buffaloes are injected with antibiotics (e.g. Ceftiofur, Oxytetracycline, Enrofloxacin), drug residues remain in milk and meat.\n"
            "• Drinking this milk causes antibiotic resistance and kidney/liver risks in children.\n"
            "• **Standard Withdrawal Times:**\n"
            "  - Intramammary tubes: 3 to 5 days milk withdrawal.\n"
            "  - Long-Acting Oxytetracycline: 7 days milk / 21 days meat.\n"
            "  - Ceftiofur: 0-3 days milk (check formulation) / 4 days meat.\n"
            "Always consult your attending veterinarian regarding the exact safe clearance date."
        ),
        "reply_hi": (
            "**एंटीबायोटिक दवा निकासी अवधि (Withdrawal Period):**\n"
            "जब पशु को गंभीर बीमारी में एंटीबायोटिक इंजेक्शन या थन की दवा दी जाती है, तो उसका असर दूध और मांस में रहता है।\n"
            "• ऐसा दूध पीने से बच्चों व वयस्कों में दवाओं के प्रति प्रतिरोध (Antibiotic Resistance) पैदा होता है।\n"
            "• **औसत सुरक्षित समय:**\n"
            "  - थन की नलियां (Intramammary): 3 से 5 दिन तक दूध न बेचें/न पिएं।\n"
            "  - लंबी अवधि का ऑक्सीटेट्रासाइक्लिन (LA): 7 दिन दूध / 21 दिन मांस।\n"
            "  - सेफ्टियोफर: 3 से 4 दिन का परहेज़ रखें।\n"
            "उपचार करने वाले पशु चिकित्सक से दवा का निकासी समय अवश्य पूछें।"
        ),
        "suggested_questions": [
            "क्या बीमार पशु का दूध गर्म करके पी सकते हैं?",
            "एंटीबायोटिक का दूध पनीर बनाने के काम आ सकता है क्या?",
            "दूध में दवा की जांच कैसे होती है?"
        ]
    },
    {
        "keywords": ["vaccine", "tikakaran", "calendar", "time", "due", "schedule", "टीका", "टीकाकरण"],
        "intent": "VACCINATION_SCHEDULE",
        "title": "National Livestock Vaccination Calendar (टीकाकरण कैलेंडर)",
        "reply_en": (
            "**Standard Indian Livestock Vaccination Calendar:**\n"
            "1. **Foot-and-Mouth Disease (FMD):** Age 4+ months. Twice a year (Pre-monsoon: May; Pre-winter: Nov).\n"
            "2. **Hemorrhagic Septicemia (HS / Galghontu):** Age 6+ months. Annually before monsoon (May-June).\n"
            "3. **Blackleg / Black Quarter (BQ):** Age 6+ months. Annually in May-June.\n"
            "4. **Brucellosis (S19):** Female calves only, aged 4 to 8 months. **ONCE in a lifetime** (creates lifelong immunity).\n"
            "5. **PPR (Goat Plague):** Sheep & goats aged 4+ months. Once every 3 years."
        ),
        "reply_hi": (
            "**पशु टीकाकरण कैलेंडर:**\n"
            "1. **खुरपका-मुंहपका (FMD):** 4 माह से बड़े पशुओं को वर्ष में 2 बार (मई व नवंबर में)।\n"
            "2. **गलघोंटू (HS):** वर्षा ऋतु से पूर्व (मई-जून) में हर वर्ष एक बार।\n"
            "3. **लंगड़ा बुखार (BQ):** वर्षा से पूर्व (मई-जून) में हर वर्ष एक बार।\n"
            "4. **संक्रामक गर्भपात (Brucellosis):** 4 से 8 माह की बछड़ियों/कटड़ियों को **जीवन में केवल एक बार**।\n"
            "5. **बकरी प्लेग (PPR):** भेड़-बकरियों को 3 वर्ष में एक बार।"
        ),
        "suggested_questions": [
            "गर्भवती गाय को कौन सा टीका नहीं लगाना चाहिए?",
            "टीकाकरण के बाद बुखार आ जाए तो क्या करें?",
            "ब्रूसेलोसिस का टीका नर बछड़े को लगा सकते हैं?"
        ]
    }
]

DEFAULT_FALLBACK = {
    "title": "Pashu Suraksha Veterinary AI Guidance",
    "reply_en": (
        "Thank you for contacting Pashu AI Sahayak. I can assist you with disease diagnosis, first-aid, "
        "vaccination schedules, withdrawal times, and emergency outbreak protocols for Cattle, Buffalo, Goat, Sheep, and Poultry.\n\n"
        "💡 **Try asking:**\n"
        "• 'What should I do if my cow has blisters in mouth?'\n"
        "• 'How to prevent Lumpy Skin Disease?'\n"
        "• 'Emergency care for animal bloat / swollen belly'\n"
        "• 'FMD vaccination due dates'\n"
        "• 'Is milk safe to drink after antibiotic injection?'"
    ),
    "reply_hi": (
        "पशु एआई सहायक में आपका स्वागत है। मैं गाय, भैंस, भेड़, बकरी और मुर्गियों के रोगों, प्राथमिक उपचार, "
        "टीकाकरण और सरकारी योजनाओं के बारे में आपकी सहायता कर सकता हूँ।\n\n"
        "💡 **आप मुझसे पूछ सकते हैं:**\n"
        "• 'गाय के मुंह व खुर में छाले हैं, क्या करें?'\n"
        "• 'लम्पी स्किन रोग से बचाव के उपाय'\n"
        "• 'पशु का पेट फूलने (अफारा) का तुरंत उपचार'\n"
        "• 'गलघोंटू और मुंहपका का टीका कब लगता है?'\n"
        "• 'एंटीबायोटिक इंजेक्शन के बाद कितने दिन दूध नहीं बेचना चाहिए?'"
    ),
    "suggested_questions": [
        "गाय के मुंह में छाले हैं क्या करें?",
        "लम्पी रोग से बचाव के घरेलू उपाय",
        "अफारा में तुरंत क्या दवा दें?",
        "टीकाकरण का सही समय क्या है?"
    ]
}


def process_chat_message(user_message: str, language: str = "hi") -> Dict[str, Any]:
    """
    Processes farmer query, matches veterinary intents, and returns localized actionable response.
    """
    msg_clean = user_message.strip().lower()
    
    matched_entry = None
    best_score = 0
    
    for entry in CHATBOT_KNOWLEDGE:
        score = sum(1 for kw in entry["keywords"] if kw in msg_clean)
        if score > best_score:
            best_score = score
            matched_entry = entry
            
    if not matched_entry or best_score == 0:
        matched_entry = DEFAULT_FALLBACK
        
    reply_text = matched_entry.get("reply_hi" if language == "hi" else "reply_en") or matched_entry["reply_en"]
    
    return {
        "success": True,
        "title": matched_entry["title"],
        "intent": matched_entry.get("intent", "GENERAL_ADVISORY"),
        "is_emergency": bool(matched_entry.get("is_emergency", False)),
        "reply": reply_text,
        "suggested_questions": matched_entry.get("suggested_questions", []),
        "language": language
    }

