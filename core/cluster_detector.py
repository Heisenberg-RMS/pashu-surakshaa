"""
Pashu Suraksha - Spatio-Temporal Cluster & Outbreak Detection Engine
Detects spatial clustering of syndromic reports within sliding time windows,
computes outbreak centroids, and generates containment buffer rings (3km infected zone, 10km surveillance zone).
"""

import math
from typing import List, Dict, Any
from datetime import datetime, timedelta

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two geographic coordinates in kilometers."""
    R = 6371.0 # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def detect_outbreak_clusters(
    reports: List[Dict[str, Any]],
    distance_threshold_km: float = 8.0,
    days_window: int = 7,
    min_cluster_cases: int = 3
) -> List[Dict[str, Any]]:
    """
    Groups recent disease reports by disease code and geographical proximity.
    Triggers an Outbreak Cluster when case count exceeds threshold, or immediately for Anthrax/ASF/Avian Flu.
    """
    if not reports:
        return []
        
    now = datetime.now()
    cutoff_date = now - timedelta(days=days_window)
    
    # Filter recent reports
    recent_reports = []
    for r in reports:
        created_str = r.get("created_at") or r.get("timestamp") or ""
        try:
            r_date = datetime.fromisoformat(created_str.replace("Z", "+00:00").split("+")[0])
        except Exception:
            r_date = now
            
        if r_date >= cutoff_date:
            recent_reports.append(r)
            
    # Group by disease code
    disease_groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in recent_reports:
        code = r.get("disease_code") or r.get("suspected_disease", "UNKNOWN")
        if code not in disease_groups:
            disease_groups[code] = []
        disease_groups[code].append(r)
        
    detected_clusters = []
    cluster_id_counter = 1
    
    for code, group in disease_groups.items():
        if not group:
            continue
            
        # Single-case immediate outbreak triggers for catastrophic or high-containment pathogens
        is_zero_tolerance = code in ["ANTHRAX", "AVIAN_FLU", "ASF"]
        threshold = 1 if is_zero_tolerance else min_cluster_cases
        
        visited = set()
        for i, rep_i in enumerate(group):
            if i in visited:
                continue
                
            cluster_members = [rep_i]
            visited.add(i)
            lat_i = float(rep_i.get("latitude", 0.0))
            lon_i = float(rep_i.get("longitude", 0.0))
            
            for j, rep_j in enumerate(group):
                if j in visited:
                    continue
                lat_j = float(rep_j.get("latitude", 0.0))
                lon_j = float(rep_j.get("longitude", 0.0))
                
                dist = haversine_distance_km(lat_i, lon_i, lat_j, lon_j)
                if dist <= distance_threshold_km:
                    cluster_members.append(rep_j)
                    visited.add(j)
                    
            if len(cluster_members) >= threshold:
                # Calculate centroid
                centroid_lat = sum(float(m.get("latitude", 0.0)) for m in cluster_members) / len(cluster_members)
                centroid_lon = sum(float(m.get("longitude", 0.0)) for m in cluster_members) / len(cluster_members)
                
                total_affected = sum(int(m.get("affected_count", 1)) for m in cluster_members)
                total_mortality = sum(int(m.get("mortality_count", 0)) for m in cluster_members)
                
                villages = list(set(m.get("village", "Unknown") for m in cluster_members if m.get("village")))
                district = cluster_members[0].get("district", "Central District")
                block = cluster_members[0].get("block", "Central Block")
                
                # Determine containment zones
                infected_zone_radius_km = 3.0
                surveillance_zone_radius_km = 10.0
                if code in ["ANTHRAX", "AVIAN_FLU"]:
                    infected_zone_radius_km = 3.0
                    surveillance_zone_radius_km = 10.0
                elif code == "LSD":
                    surveillance_zone_radius_km = 8.0
                    
                detected_clusters.append({
                    "cluster_id": f"CLUST-{datetime.now().year}-{cluster_id_counter:03d}",
                    "disease_code": code,
                    "disease_name": cluster_members[0].get("disease_name", code),
                    "case_count": len(cluster_members),
                    "total_affected_animals": total_affected,
                    "total_mortality": total_mortality,
                    "centroid_latitude": round(centroid_lat, 5),
                    "centroid_longitude": round(centroid_lon, 5),
                    "district": district,
                    "block": block,
                    "villages_affected": villages,
                    "status": "ACTIVE_OUTBREAK",
                    "severity": "CRITICAL" if (is_zero_tolerance or total_mortality > 0 or len(cluster_members) >= 5) else "HIGH",
                    "containment": {
                        "infected_zone_radius_km": infected_zone_radius_km,
                        "surveillance_zone_radius_km": surveillance_zone_radius_km,
                        "movement_ban_active": True,
                        "ring_vaccination_mandated": True,
                        "target_species": cluster_members[0].get("species", "Livestock")
                    },
                    "first_reported": min(m.get("created_at", "") for m in cluster_members),
                    "latest_reported": max(m.get("created_at", "") for m in cluster_members)
                })
                cluster_id_counter += 1
                
    return detected_clusters
