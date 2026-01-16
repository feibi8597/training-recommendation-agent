# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Venue search tool for training recommendation agent."""

import os
import logging
import math
from typing import Dict, Any, List
from pathlib import Path
import googlemaps
from google.adk.tools import ToolContext

# Try to load .env file if not already loaded
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
except ImportError:
    pass

logger = logging.getLogger(__name__)


def search_nearby_venues(
    latitude: float,
    longitude: float,
    sport_type: str,
    radius: int = 2000,
    max_results: int = 5,
    tool_context: ToolContext = None,
) -> Dict[str, Any]:
    """Search for nearby venues suitable for a specific sport type.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        sport_type: Type of sport (e.g., "长跑", "游泳", "力量训练", "瑜伽", "骑行")
        radius: Search radius in meters (default: 2000)
        max_results: Maximum number of results to return (default: 5)
        tool_context: ADK tool context

    Returns:
        dict: A dictionary containing:
            - status: "success" or "error"
            - venues: List of venue information
            - error_message: Error details if status is "error"
    """
    maps_api_key = None
    if tool_context:
        maps_api_key = tool_context.state.get("maps_api_key", "")
    if not maps_api_key:
        maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY") or os.environ.get("MAPS_API_KEY", "")
    
    if not maps_api_key:
        logger.warning("⚠️  Google Maps API key not found")
        return {
            "status": "error",
            "venues": [],
            "error_message": "Google Maps API key not configured"
        }
    
    try:
        gmaps = googlemaps.Client(key=maps_api_key)
        
        # Map sport type to Google Places API types
        place_types = _map_sport_to_place_types(sport_type)
        
        all_venues = []
        seen_place_ids = set()
        
        # Search for each place type
        for place_type in place_types:
            try:
                places_result = gmaps.places_nearby(
                    location=(latitude, longitude),
                    radius=radius,
                    type=place_type,
                    language='zh-CN'
                )
                
                for place in places_result.get("results", []):
                    place_id = place.get("place_id")
                    if place_id and place_id not in seen_place_ids:
                        seen_place_ids.add(place_id)
                        
                        # Calculate distance
                        place_lat = place["geometry"]["location"]["lat"]
                        place_lng = place["geometry"]["location"]["lng"]
                        distance = _calculate_distance(
                            latitude, longitude, place_lat, place_lng
                        )
                        
                        venue_info = {
                            "name": place.get("name", "未知地点"),
                            "address": place.get("vicinity", place.get("formatted_address", "")),
                            "distance": _format_distance(distance),
                            "distance_meters": round(distance),
                            "rating": place.get("rating", 0),
                            "place_id": place_id,
                            "types": place.get("types", []),
                            "location": {
                                "latitude": place_lat,
                                "longitude": place_lng
                            }
                        }
                        
                        all_venues.append(venue_info)
                        
            except Exception as e:
                logger.warning(f"⚠️  Error searching for {place_type}: {e}")
                continue
        
        # Sort by distance and rating
        all_venues.sort(key=lambda x: (x["distance_meters"], -x["rating"]))
        
        # Limit results
        venues = all_venues[:max_results]
        
        return {
            "status": "success",
            "venues": venues,
            "sport_type": sport_type,
            "location": {"latitude": latitude, "longitude": longitude}
        }
        
    except Exception as e:
        logger.error(f"❌ Venue search error: {e}")
        return {
            "status": "error",
            "venues": [],
            "error_message": str(e)
        }


def _map_sport_to_place_types(sport_type: str) -> List[str]:
    """Map sport type to Google Places API types."""
    sport_lower = sport_type.lower()
    
    # Mapping of sport types to Google Places API types
    sport_mapping = {
        "长跑": ["park", "route"],
        "跑步": ["park", "route"],
        "running": ["park", "route"],
        "游泳": ["swimming_pool", "gym"],
        "swimming": ["swimming_pool", "gym"],
        "力量训练": ["gym", "health"],
        "健身": ["gym", "health"],
        "gym": ["gym", "health"],
        "瑜伽": ["gym", "yoga"],
        "yoga": ["gym", "yoga"],
        "骑行": ["park", "route", "bicycle_store"],
        "自行车": ["park", "route", "bicycle_store"],
        "cycling": ["park", "route", "bicycle_store"],
        "篮球": ["basketball_court", "gym"],
        "羽毛球": ["gym", "sports_complex"],
        "爬山": ["park", "natural_feature"],
    }
    
    # Try exact match first
    if sport_type in sport_mapping:
        return sport_mapping[sport_type]
    
    # Try case-insensitive match
    for key, value in sport_mapping.items():
        if key.lower() in sport_lower or sport_lower in key.lower():
            return value
    
    # Default: return gym and park
    return ["gym", "park"]


def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula.
    
    Returns distance in meters.
    """
    R = 6371000  # Earth radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def _format_distance(distance_meters: float) -> str:
    """Format distance in a human-readable format."""
    if distance_meters < 1000:
        return f"{int(distance_meters)}米"
    else:
        return f"{distance_meters / 1000:.1f}公里"
