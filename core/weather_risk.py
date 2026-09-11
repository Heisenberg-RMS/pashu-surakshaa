"""
Pashu Suraksha - Environmental & Vector Risk Scoring Engine
Correlates meteorological parameters (temperature, humidity, monsoon precipitation, wind vectors)
with pathogen transmission dynamics and insect vector suitability (Culicoides, ticks, flies).
"""

from typing import Dict, Any, List

def calculate_environmental_risk(
    temperature_c: float,
    humidity_percent: float,
    rainfall_mm: float,
    wind_speed_kmh: float,
    district_name: str = "Regional"
) -> Dict[str, Any]:
    """
    Computes disease-specific transmission risk indices based on microclimate variables.
    """
    # 1. Vector Suitability Index (Culicoides midges, ticks, Stomoxys flies)
    # Optimum: 25-34°C, humidity > 65%, moderate moisture
    vector_score = 0
    if 24.0 <= temperature_c <= 34.0:
        vector_score += 45
    elif 20.0 <= temperature_c <= 38.0:
        vector_score += 25
    else:
        vector_score += 10
        
    if humidity_percent >= 75.0:
        vector_score += 40
    elif humidity_percent >= 60.0:
        vector_score += 25
    else:
        vector_score += 10
        
    if rainfall_mm > 5.0:
        vector_score += 15
    vector_index = min(vector_score, 100)
    
    # 2. FMD Airborne Transmission Index
    # Aphthovirus survives longer and disperses downwind in high humidity (>60%) and cooler/mild temps (15-27°C)
    fmd_score = 0
    if 12.0 <= temperature_c <= 27.0:
        fmd_score += 40
    elif temperature_c <= 32.0:
        fmd_score += 20
        
    if humidity_percent >= 65.0:
        fmd_score += 40
    elif humidity_percent >= 50.0:
        fmd_score += 20
        
    if 8.0 <= wind_speed_kmh <= 28.0:
        fmd_score += 20
    fmd_risk_index = min(fmd_score, 100)
    
    # 3. Hemorrhagic Septicemia (HS) Waterlogging Stress Risk
    # High in torrential rain, sudden cold stress, high humidity
    hs_score = 20
    if rainfall_mm >= 25.0:
        hs_score += 50
    elif rainfall_mm >= 10.0:
        hs_score += 30
        
    if humidity_percent >= 80.0:
        hs_score += 30
    hs_risk_index = min(hs_score, 100)
    
    # 4. Anthrax Soil Spore Exposure Risk
    # High risk when prolonged dry period is followed by abrupt torrential rain
    anthrax_score = 15
    if rainfall_mm >= 35.0 and temperature_c >= 30.0:
        anthrax_score += 55
    elif rainfall_mm >= 15.0:
        anthrax_score += 30
    anthrax_risk_index = min(anthrax_score, 100)
    
    def get_level(score: int) -> str:
        if score >= 75:
            return "CRITICAL"
        elif score >= 50:
            return "HIGH"
        elif score >= 30:
            return "MODERATE"
        return "LOW"
        
    return {
        "district": district_name,
        "meteorological_conditions": {
            "temperature_c": temperature_c,
            "relative_humidity_percent": humidity_percent,
            "precipitation_24h_mm": rainfall_mm,
            "wind_speed_kmh": wind_speed_kmh
        },
        "indices": {
            "vector_breeding_suitability": {
                "score": vector_index,
                "level": get_level(vector_index),
                "primary_vectors": "Culicoides midges, Hyalomma ticks, Stomoxys calcitrans",
                "linked_diseases": ["Lumpy Skin Disease", "Theileriosis", "Bluetongue"]
            },
            "fmd_airborne_dispersion": {
                "score": fmd_risk_index,
                "level": get_level(fmd_risk_index),
                "dispersion_radius_potential": "Up to 15 km downwind under current humidity",
                "linked_diseases": ["Foot-and-Mouth Disease"]
            },
            "waterlogging_stress_hs": {
                "score": hs_risk_index,
                "level": get_level(hs_risk_index),
                "vulnerable_species": "Buffaloes and crossbred cattle",
                "linked_diseases": ["Hemorrhagic Septicemia (गलघोंटू)"]
            },
            "spore_washout_anthrax": {
                "score": anthrax_risk_index,
                "level": get_level(anthrax_risk_index),
                "warning": "Low-lying alkaline grazing pastures prone to spore exposure",
                "linked_diseases": ["Anthrax (विषहरि)"]
            }
        },
        "overall_biosecurity_threat_level": get_level(max(vector_index, fmd_risk_index, hs_risk_index))
    }

def get_regional_weather_profiles() -> List[Dict[str, Any]]:
    """Returns sample real-time simulated regional microclimate profiles across key livestock belts."""
    regions = [
        {"district": "Hisar", "block": "Hansi", "state": "Haryana", "temp": 31.5, "humidity": 78, "rain": 14.2, "wind": 16.5},
        {"district": "Anand", "block": "Petlad", "state": "Gujarat", "temp": 29.8, "humidity": 82, "rain": 22.0, "wind": 14.0},
        {"district": "Bareilly", "block": "Faridpur", "state": "Uttar Pradesh", "temp": 28.4, "humidity": 85, "rain": 38.5, "wind": 11.2},
        {"district": "Ludhiana", "block": "Jagraon", "state": "Punjab", "temp": 33.0, "humidity": 65, "rain": 2.0, "wind": 18.0},
        {"district": "Salem", "block": "Omalur", "state": "Tamil Nadu", "temp": 32.2, "humidity": 71, "rain": 8.5, "wind": 12.5},
        {"district": "Bikaner", "block": "Nokha", "state": "Rajasthan", "temp": 37.5, "humidity": 42, "rain": 0.0, "wind": 22.0}
    ]
    
    results = []
    for r in regions:
        risk_profile = calculate_environmental_risk(
            temperature_c=r["temp"],
            humidity_percent=r["humidity"],
            rainfall_mm=r["rain"],
            wind_speed_kmh=r["wind"],
            district_name=r["district"]
        )
        risk_profile["block"] = r["block"]
        risk_profile["state"] = r["state"]
        results.append(risk_profile)
    return results
