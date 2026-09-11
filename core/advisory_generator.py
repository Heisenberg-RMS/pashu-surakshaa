"""
Pashu Suraksha - Multilingual Advisory & Voice Broadcast Engine
Generates disease prevention, biosecurity, and emergency quarantine advisories
in multiple Indian languages (Hindi, English, Punjabi, Bengali, Marathi, Telugu, Tamil).
"""

from typing import Dict, Any, List

ADVISORY_TEMPLATES = {
    "FMD_OUTBREAK": {
        "en": {
            "title": "Foot-and-Mouth Disease (FMD) Outbreak Alert",
            "voice_script": "Attention livestock owners. Suspected Foot and Mouth Disease has been reported in your block. Isolate any animals showing drooling or blisters on mouth and feet. Do not allow your cattle to graze in common pastures. Apply potassium permanganate solution on lesions. Contact the veterinary officer immediately.",
            "text": "CRITICAL ALERT: Suspected FMD reported nearby. 1) Segregate sick cattle immediately. 2) Wash mouth and hoof sores with 1:1000 potassium permanganate solution. 3) Prohibit animal trade and common grazing. 4) Report new cases to toll-free 1962."
        },
        "hi": {
            "title": "खुरपका-मुंहपका (FMD) रोग चेतावनी एवं परामर्श",
            "voice_script": "पशुपालक भाइयों ध्यान दें। आपके ब्लॉक में खुरपका-मुंहपका बीमारी के लक्षण पाए गए हैं। यदि पशु के मुंह से लार टपक रही हो या खुरों व जीभ पर छाले हों, तो उसे तुरंत अन्य पशुओं से अलग बांधें। सामूहिक चराई बंद करें। छालों पर लाल दवा यानी पोटेशियम परमैंगनेट का घोल लगाएं। तुरंत पशु चिकित्सक से संपर्क करें।",
            "text": "अति महत्वपूर्ण सूचना: खुरपका-मुंहपका रोग का प्रकोप दर्ज किया गया है। 1) बीमार पशु को तुरंत अलग करें। 2) मुंह व खुर के छालों को पोटेशियम परमैंगनेट के हल्के घोल से धोएं। 3) पशु हाट या मेले में पशु न ले जाएं। 4) निःशुल्क हेल्पलाइन 1962 पर सूचना दें।"
        },
        "pa": {
            "title": "ਮੂੰਹ-ਖੁਰ (FMD) ਬਿਮਾਰੀ ਚੇਤਾਵਨੀ",
            "voice_script": "ਪਸ਼ੂ ਪਾਲਕ ਵੀਰੋ ਧਿਆਨ ਦਿਓ। ਤੁਹਾਡੇ ਇਲਾਕੇ ਵਿੱਚ ਮੂੰਹ-ਖੁਰ ਦੀ ਬਿਮਾਰੀ ਦੇ ਲੱਛਣ ਮਿਲੇ ਹਨ। ਜੇਕਰ ਪਸ਼ੂ ਦੇ ਮੂੰਹ ਵਿੱਚੋਂ ਝੱਗ ਵਗ ਰਹੀ ਹੈ ਜਾਂ ਪੈਰਾਂ 'ਤੇ ਛਾਲੇ ਹਨ, ਤਾਂ ਉਸ ਨੂੰ ਤੁਰੰਤ ਵੱਖਰਾ ਬੰਨ੍ਹੋ। ਸਾਂਝੀ ਚਰਾਈ ਰੋਕੋ ਅਤੇ ਲਾਲ ਦਵਾਈ ਨਾਲ ਛਾਲੇ ਸਾਫ਼ ਕਰੋ।",
            "text": "ਜ਼ਰੂਰੀ ਚੇਤਾਵਨੀ: ਮੂੰਹ-ਖੁਰ ਬਿਮਾਰੀ ਦੀ ਰਿਪੋਰਟ ਹੋਈ ਹੈ। 1) ਬਿਮਾਰ ਪਸ਼ੂ ਨੂੰ ਤੁਰੰਤ ਵੱਖ ਕਰੋ। 2) ਪੋਟਾਸ਼ੀਅਮ ਪਰਮੈਂਗਨੇਟ ਨਾਲ ਜ਼ਖ਼ਮ ਧੋਵੋ। 3) ਪਸ਼ੂ ਮੰਡੀਆਂ ਵਿੱਚ ਜਾਣਾ ਬੰਦ ਕਰੋ। 4) ਵੈਟਰਨਰੀ ਹਸਪਤਾਲ ਸੰਪਰਕ ਕਰੋ।"
        },
        "bn": {
            "title": "খুরারোগ (FMD) প্রাদুর্ভাব সতর্কতা",
            "voice_script": "পশুপালক ভাইয়েরা শুনুন। আপনার এলাকায় খুরারোগের লক্ষণ পাওয়া গেছে। যদি গবাদি পশুর মুখ দিয়ে লালা ঝরে বা খুরে ঘা হয়, তবে তাকে অবিলম্বে আলাদা রাখুন। সাধারণ চারণভূমিতে নিয়ে যাবেন না। অবিলম্বে নিকটস্থ পশু চিকিৎসকের সাথে যোগাযোগ করুন।",
            "text": "জরুরি সতর্কতা: খুরারোগ (FMD) দেখা দিয়েছে। ১) আক্রান্ত পশুকে দল থেকে আলাদা করুন। ২) লাল জল (পটাশিয়াম পারম্যাঙ্গানেট) দিয়ে মুখ ও খুরের ঘা পরিষ্কার করুন। ৩) পশুর মেলা বা হাটে নিয়ে যাবেন না।"
        },
        "mr": {
            "title": "लाळ्या खुरकूत (FMD) प्रादुर्भाव सतर्कता",
            "voice_script": "पशुपालक मित्रांनो लक्ष द्या. आपल्या भागात लाळ्या खुरकूत आजाराची लक्षणे आढळली आहेत. जनावरांच्या लाळ गळत असल्यास किंवा तोंडात-खुरांत फोड असल्यास त्यांना तात्काळ वेगळे बांधा. सामूहिक चरण्यास बंदी घाला. ताबडतोब पशुवैद्यकीय अधिकाऱ्यांशी संपर्क साधा.",
            "text": "अत्यंत तातडीचा इशारा: लाळ्या खुरकूतचा प्रादुर्भाव. १) बाधित जनावरांना तत्काळ विलग करा. २) पोटॅशियम परमँगनेटच्या पाण्याने जखमा धुवा. ३) जनावरांचे बाजार व वाहतूक तात्काळ थांबवा."
        },
        "te": {
            "title": "గాలికుంటు వ్యాధి (FMD) హెచ్చరిక",
            "voice_script": "రైతు సోదరులారా గమనించండి. మీ ప్రాంతంలో గాలికుంటు వ్యాధి వ్యాపించే ప్రమాదం ఉంది. నోటి నుండి లాలాజలం కారుతున్న, గిట్టల మధ్య పుండ్లు ఉన్న పశువులను వెంటనే మంద నుండి వేరు చేయండి. వెంటనే పశువైద్యుడిని సంప్రదించండి.",
            "text": "ముఖ్య హెచ్చరిక: గాలికుంటు వ్యాధి వ్యాప్తి. 1) వ్యాధి సోకిన పశువును వేరు చేయండి. 2) పుండ్లను పొటాషియం పర్మాంగనేట్ ద్రావణంతో శుభ్రం చేయండి. 3) సంతలకు పశువులను తరలించవద్దు."
        },
        "ta": {
            "title": "கோமாரி நோய் (FMD) எச்சரிக்கை",
            "voice_script": "விவசாய பெருமக்களே கவனம். உங்கள் பகுதியில் கோமாரி நோய் பரவி வருகிறது. வாயில் உமிழ்நீர் வடிதல் அல்லது கால்களில் கொப்பளங்கள் உள்ள மாடுகளை உடனடியாக தனியாக பிரிக்கவும். பொது மேய்ச்சலை தவிர்க்கவும். கால்நடை மருத்துவரை அணுகவும்.",
            "text": "அவசர எச்சரிக்கை: கோமாரி நோய் தடுப்பு. 1) பாதிக்கப்பட்ட மாடுகளை உடனே தனிமைப்படுத்தவும். 2) பொட்டாசியம் பெர்மாங்கனேட் கரைசலால் புண்களை கழுவவும். 3) கால்நடை சந்தைகளை தவிர்க்கவும்."
        }
    },
    "LSD_OUTBREAK": {
        "en": {
            "title": "Lumpy Skin Disease (LSD) Vector Advisory",
            "voice_script": "Urgent alert regarding Lumpy Skin Disease. Cattle with circular skin nodules and fever must be isolated. Spray neem oil or ectoparasiticide to repel biting midges, flies, and ticks. Ensure your healthy cattle receive goat pox preventive vaccine.",
            "text": "LSD ALERT: 1) Isolate nodular cattle under mosquito netting. 2) Spray neem seed kernel extract or fly repellents in sheds. 3) Healthy cattle in 5km radius should receive Goat Pox vaccination. 4) Clean shed with 1% formalin or 2% sodium hypochlorite."
        },
        "hi": {
            "title": "लम्पी स्किन डिजीज (गांठदार त्वचा रोग) परामर्श",
            "voice_script": "लम्पी त्वचा रोग से बचाव हेतु सूचना। जिन गायों के शरीर पर गोल गांठें या तेज बुखार हो, उन्हें तुरंत मच्छरदानी में अलग रखें। मक्खी, मच्छर और किलनी भगाने के लिए नीम के तेल या कपूर का छिड़काव करें। स्वस्थ पशुओं को गोट पॉक्स का टीका जरूर लगवाएं।",
            "text": "लम्पी रोग रोकथाम: 1) गांठ वाले पशु को अलग करें व मच्छरदानी लगाएं। 2) गौशाला में नीम की पत्ती का धुआं करें तथा कीटनाशक छिड़कें। 3) 5 किमी के दायरे में स्वस्थ पशुओं को गोट पॉक्स वैक्सीन लगवाएं। 4) गौशाला को स्वच्छ व सूखा रखें।"
        },
        "pa": {
            "title": "ਲੰਪੀ ਸਕਿਨ ਬਿਮਾਰੀ (LSD) ਬਚਾਅ ਸਲਾਹ",
            "voice_script": "ਲੰਪੀ ਚਮੜੀ ਰੋਗ ਬਾਰੇ ਜ਼ਰੂਰੀ ਜਾਣਕਾਰੀ। ਜਿਨ੍ਹਾਂ ਪਸ਼ੂਆਂ ਦੇ ਸਰੀਰ 'ਤੇ ਗੰਢਾਂ ਹਨ, ਉਨ੍ਹਾਂ ਨੂੰ ਵੱਖ ਕਰੋ। ਮੱਖੀਆਂ ਅਤੇ ਮੱਛਰਾਂ ਨੂੰ ਭਜਾਉਣ ਲਈ ਨਿੰਮ ਦੇ ਤੇਲ ਦਾ ਛਿੜਕਾਅ ਕਰੋ। ਤੰਦਰੁਸਤ ਪਸ਼ੂਆਂ ਨੂੰ ਬਚਾਅ ਦਾ ਟੀਕਾ ਜ਼ਰੂਰ ਲਗਵਾਓ।",
            "text": "ਲੰਪੀ ਸਕਿਨ ਰੋਕਥਾਮ: 1) ਗੰਢਾਂ ਵਾਲੇ ਪਸ਼ੂ ਨੂੰ ਵੱਖਰੇ ਸ਼ੈੱਡ ਵਿੱਚ ਰੱਖੋ। 2) ਮੱਛਰਾਂ-ਮੱਖੀਆਂ ਦੀ ਰੋਕਥਾਮ ਲਈ ਸਪਰੇਅ ਕਰੋ। 3) ਨੇੜਲੇ ਵੈਟਰਨਰੀ ਹਸਪਤਾਲ ਤੋਂ ਟੀਕਾਕਰਨ ਕਰਵਾਓ।"
        }
    },
    "ANTHRAX_BIOHAZARD": {
        "en": {
            "title": "CRITICAL BIOHAZARD: Suspected Anthrax Warning",
            "voice_script": "Extreme danger warning. Suspected Anthrax case detected. Do not touch or cut open the carcass. Dark blood oozing from mouth or rectum contains deadly spores that infect humans. Keep humans and dogs away. Veterinary team is en route for deep burial with lime.",
            "text": "DANGER - ZOONOTIC BIOHAZARD: 1) NEVER cut or flay the carcass. 2) Cover carcass with heavy tarpaulin to prevent birds/dogs access. 3) Disinfect surrounding soil with 10% caustic soda or formalin. 4) Anyone with cuts who touched animal must report to hospital."
        },
        "hi": {
            "title": "अत्यंत खतरनाक चेतावनी: संक्रामक गिलटी / विषहरि (एंथ्रेक्स) रोग",
            "voice_script": "सावधान! अत्यंत गंभीर चेतावनी। एंथ्रेक्स बीमारी का अंदेशा है। मृत पशु के शव को बिल्कुल न चीरें और न ही छुएं। नाक या गुदा से निकलने वाला काला खून मनुष्यों में भी जानलेवा संक्रमण फैला सकता है। शव को ढक कर रखें। पशुपालन विभाग की टीम 2 मीटर गहरे गड्ढे में चूना डालकर दफनाने आ रही है।",
            "text": "खतरे की चेतावनी (एंथ्रेक्स): 1) मृत पशु का चीर-फाड़ बिल्कुल न करें। 2) शव को तुरंत ढकें, कुत्तों व पक्षियों को दूर रखें। 3) जमीन पर 10% चूना या फॉर्मेलिन का छिड़काव करें। 4) संपर्क में आए लोग तुरंत प्राथमिक स्वास्थ्य केंद्र जाएं।"
        }
    },
    "PRE_MONSOON_VACCINATION": {
        "en": {
            "title": "Seasonal Pre-Monsoon Vaccination Drive (HS & BQ)",
            "voice_script": "Seasonal health advisory. Monsoon brings high risk of Galghontu (HS) and Langra Bukhar (Blackleg). Get your cattle and buffaloes vaccinated at the nearest dispensary before the rains begin. Deworm calves to ensure robust immunity.",
            "text": "PRE-MONSOON DRIVE: 1) Vaccinate all cattle and buffaloes against Hemorrhagic Septicemia (HS) and Blackleg (BQ). 2) Administer broad-spectrum anthelmintic for liver flukes and roundworms. 3) Store dry fodder in elevated moisture-free sheds."
        },
        "hi": {
            "title": "मानसून पूर्व टीकाकरण अभियान (गलघोंटू व लंगड़ा बुखार)",
            "voice_script": "पशुपालक भाइयों, वर्षा ऋतु शुरू होने से पहले गलघोंटू और लंगड़ा बुखार का टीका अवश्य लगवाएं। बारिश के मौसम में दलदली पानी से यह बीमारियां तेजी से फैलती हैं। अपने पशुओं को पेट के कीड़ों की दवा यानी कृमिनाशक भी दें। नजदीकी पशु औषधालय में यह टीका निःशुल्क उपलब्ध है।",
            "text": "वर्षा पूर्व टीकाकरण: 1) सभी गाय-भैंसों को गलघोंटू (HS) और लंगड़ा (BQ) का टीका लगवाएं। 2) पशुओं को पेट के कीड़ों की दवा (Albendazole/Fenbendazole) अवश्य दें। 3) भूसा व चारा सूखे स्थान पर रखें ताकि फफूंद न लगे।"
        }
    }
}

def get_multilingual_advisory(alert_type: str, language: str = "hi") -> Dict[str, Any]:
    """Retrieves localized text and spoken script for farmer broadcast."""
    type_data = ADVISORY_TEMPLATES.get(alert_type, ADVISORY_TEMPLATES["FMD_OUTBREAK"])
    lang_data = type_data.get(language) or type_data.get("en") or list(type_data.values())[0]
    return {
        "alert_type": alert_type,
        "language": language,
        "title": lang_data["title"],
        "voice_script": lang_data["voice_script"],
        "text": lang_data["text"]
    }

def get_all_supported_languages() -> List[Dict[str, str]]:
    """Returns list of supported Indian languages with BCP 47 speech tags."""
    return [
        {"code": "hi", "name": "हिन्दी (Hindi)", "speech_voice": "hi-IN"},
        {"code": "en", "name": "English (Indian)", "speech_voice": "en-IN"},
        {"code": "pa", "name": "ਪੰਜਾਬੀ (Punjabi)", "speech_voice": "pa-IN"},
        {"code": "bn", "name": "বাংলা (Bengali)", "speech_voice": "bn-IN"},
        {"code": "mr", "name": "मराठी (Marathi)", "speech_voice": "mr-IN"},
        {"code": "te", "name": "తెలుగు (Telugu)", "speech_voice": "te-IN"},
        {"code": "ta", "name": "தமிழ் (Tamil)", "speech_voice": "ta-IN"}
    ]
