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

"""Weather forecast tool for training recommendation agent."""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from pathlib import Path
import requests
from google.adk.tools import ToolContext

# Try to load .env file if not already loaded
try:
    from dotenv import load_dotenv
    # Try to find .env file in project root (two levels up from this file)
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
except ImportError:
    pass  # dotenv not available, rely on system environment variables

logger = logging.getLogger(__name__)


def get_weather_forecast(
    latitude: float,
    longitude: float,
    days: int = 7,
    tool_context: ToolContext = None,
) -> Dict[str, Any]:
    """Get weather forecast for the next N days.

    This tool fetches weather forecast data using Google Weather API (Google Maps Platform).
    If Google Maps API key is not available, returns mock data for development.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        days: Number of days to forecast (default: 7, max: 7)
        tool_context: ADK tool context

    Returns:
        dict: A dictionary containing:
            - status: "success" or "error"
            - forecast: List of daily weather forecasts
            - error_message: Error details if status is "error"
    """
    days = min(max(days, 1), 7)  # Clamp between 1 and 7

    # 降级链：Google Weather API → OpenWeatherMap API → 模拟数据
    
    # Step 1: 尝试 Google Weather API
    google_api_key = None
    if tool_context:
        google_api_key = tool_context.state.get("maps_api_key", "")
    if not google_api_key:
        google_api_key = os.environ.get("GOOGLE_MAPS_API_KEY") or os.environ.get("MAPS_API_KEY", "")
    
    if google_api_key:
        try:
            logger.info(f"🌐 Attempting Google Weather API...")
            result = _get_weather_from_google(latitude, longitude, days, google_api_key)
            logger.info(f"✅ Google Weather API succeeded")
            return result
        except requests.exceptions.HTTPError as e:
            # 检查是否是位置不支持的错误
            if "Location not supported" in str(e) or "not supported for this location" in str(e).lower():
                logger.warning(f"⚠️  Location ({latitude}, {longitude}) not supported by Google Weather API")
            else:
                logger.warning(f"⚠️  Google Weather API failed: {e}")
            logger.info(f"🔄 Falling back to OpenWeatherMap API...")
        except Exception as e:
            logger.warning(f"⚠️  Google Weather API error: {e}")
            logger.info(f"🔄 Falling back to OpenWeatherMap API...")
    else:
        logger.info(f"ℹ️  Google Maps API key not found, skipping Google Weather API")
        logger.info(f"🔄 Trying OpenWeatherMap API...")
    
    # Step 2: 尝试 OpenWeatherMap API
    openweather_key = os.environ.get("OPENWEATHER_API_KEY") or os.environ.get("WEATHER_API_KEY")
    
    if openweather_key:
        try:
            logger.info(f"🌐 Attempting OpenWeatherMap API...")
            result = _get_weather_from_openweathermap(latitude, longitude, days, openweather_key)
            logger.info(f"✅ OpenWeatherMap API succeeded")
            return result
        except requests.exceptions.HTTPError as e:
            logger.warning(f"⚠️  OpenWeatherMap API HTTP error: {e}")
        except Exception as e:
            logger.warning(f"⚠️  OpenWeatherMap API error: {e}")
    else:
        logger.info(f"ℹ️  OpenWeatherMap API key not found")
    
    # Step 3: 最终降级到模拟数据
    logger.info(f"📊 All weather APIs failed or unavailable, using mock weather data")
    return _get_mock_weather_forecast(latitude, longitude, days)


def _get_weather_from_google(
    latitude: float, longitude: float, days: int, api_key: str
) -> Dict[str, Any]:
    """Get weather forecast from Google Weather API (Google Maps Platform)."""
    # Google Weather API endpoint for daily forecast
    base_url = "https://weather.googleapis.com/v1"
    
    forecast_list = []
    today = datetime.now().date()
    
    try:
        # Get daily forecast (up to 10 days)
        forecast_url = f"{base_url}/forecast/days:lookup"
        params = {
            "key": api_key,
            "location.latitude": latitude,
            "location.longitude": longitude,
            "days": days,
        }
        
        logger.debug(f"Requesting weather forecast: {forecast_url} with params: location=({latitude}, {longitude}), days={days}")
        response = requests.get(forecast_url, params=params, timeout=10)
        
        if response.status_code == 404:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get("error", {}).get("message", response.text)
            
            # Check if it's a location not supported error
            if "not supported for this location" in error_msg.lower() or "try a different location" in error_msg.lower():
                logger.warning(f"⚠️  Weather API does not support this location ({latitude}, {longitude})")
                raise requests.exceptions.HTTPError(f"Location not supported: {error_msg}")
            else:
                logger.error(f"❌ Weather API 404 error. This usually means:")
                logger.error(f"   1. Weather API is not enabled in your Google Cloud project")
                logger.error(f"   2. API key doesn't have permission to access Weather API")
                logger.error(f"   3. Check: https://console.cloud.google.com/google/maps-apis")
                raise requests.exceptions.HTTPError(f"Weather API not available (404): {error_msg}")
        
        response.raise_for_status()
        data = response.json()
        logger.debug(f"Weather API response received successfully")
        
        # Process Google Weather API response
        daily_forecast_data = data.get("dailyForecast", {})
        daily_forecasts = daily_forecast_data.get("days", [])
        
        if not daily_forecasts:
            daily_forecasts = data.get("forecast", {}).get("daily", [])
        
        logger.debug(f"Received {len(daily_forecasts)} days of forecast data")
        
        # Process each day
        for i in range(days):
            forecast_date = today + timedelta(days=i)
            
            if i < len(daily_forecasts):
                day_data = daily_forecasts[i]
                
                temp_data = day_data.get("temperature", {}) or day_data.get("temp", {})
                high_temp = temp_data.get("high", temp_data.get("max", 22))
                low_temp = temp_data.get("low", temp_data.get("min", 15))
                
                condition_data = day_data.get("condition", day_data.get("weather", {}))
                if isinstance(condition_data, str):
                    condition = condition_data
                else:
                    condition = condition_data.get("text", condition_data.get("main", "多云"))
                
                condition_cn = _map_condition_to_chinese(condition)
                
                humidity = day_data.get("humidity", day_data.get("relativeHumidity", 60))
                wind_speed = day_data.get("windSpeed", day_data.get("wind", {}).get("speed", 10))
                if wind_speed > 50:
                    wind_speed = wind_speed * 3.6
                
                precipitation_prob = day_data.get("precipitationProbability", 
                                                  day_data.get("pop", 20))
                
                suitable_outdoor = (
                    "雨" not in condition_cn and 
                    "雪" not in condition_cn and
                    precipitation_prob < 50
                )
                
            else:
                high_temp = 22
                low_temp = 15
                condition_cn = "多云"
                humidity = 60
                wind_speed = 10
                precipitation_prob = 20
                suitable_outdoor = True
            
            forecast_list.append(
                {
                    "date": forecast_date.strftime("%Y-%m-%d"),
                    "day_of_week": _get_day_of_week_cn(forecast_date.weekday()),
                    "condition": condition_cn,
                    "condition_icon": _get_weather_icon(condition_cn),
                    "temperature": {"high": round(high_temp), "low": round(low_temp)},
                    "humidity": round(humidity),
                    "wind_speed": round(wind_speed),
                    "precipitation_probability": round(precipitation_prob),
                    "suitable_for_outdoor": suitable_outdoor,
                }
            )
        
        return {"status": "success", "forecast": forecast_list}
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Google Weather API request failed: {e}")
        raise
    except KeyError as e:
        logger.warning(f"⚠️  Unexpected API response structure: {e}, using fallback")
        raise


def _get_weather_from_openweathermap(
    latitude: float, longitude: float, days: int, api_key: str
) -> Dict[str, Any]:
    """Get weather forecast from OpenWeatherMap API."""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
        "units": "metric",
        "lang": "zh_cn",
        "cnt": days * 8,
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    forecast_list = []
    today = datetime.now().date()
    
    daily_forecasts = {}
    for item in data.get("list", []):
        dt = datetime.fromtimestamp(item["dt"])
        date_key = dt.date()
        
        if date_key not in daily_forecasts:
            daily_forecasts[date_key] = {
                "temps": [],
                "conditions": [],
                "humidity": [],
                "wind_speed": [],
                "precipitation": [],
            }
        
        daily_forecasts[date_key]["temps"].append(item["main"]["temp"])
        daily_forecasts[date_key]["conditions"].append(item["weather"][0]["main"])
        daily_forecasts[date_key]["humidity"].append(item["main"]["humidity"])
        daily_forecasts[date_key]["wind_speed"].append(
            item.get("wind", {}).get("speed", 0) * 3.6
        )
        rain = item.get("rain", {}).get("3h", 0) if "rain" in item else 0
        snow = item.get("snow", {}).get("3h", 0) if "snow" in item else 0
        daily_forecasts[date_key]["precipitation"].append(rain + snow)
    
    for i in range(days):
        forecast_date = today + timedelta(days=i)
        date_key = forecast_date
        
        if date_key in daily_forecasts:
            day_data = daily_forecasts[date_key]
            high_temp = max(day_data["temps"])
            low_temp = min(day_data["temps"])
            avg_humidity = sum(day_data["humidity"]) / len(day_data["humidity"])
            avg_wind = sum(day_data["wind_speed"]) / len(day_data["wind_speed"])
            total_precip = sum(day_data["precipitation"])
            
            condition_counts = {}
            for cond in day_data["conditions"]:
                condition_counts[cond] = condition_counts.get(cond, 0) + 1
            main_condition = max(condition_counts, key=condition_counts.get)
            
            condition_cn = _map_condition_to_chinese(main_condition)
            precip_prob = min(round(total_precip * 20), 100) if total_precip > 0 else 20
            suitable_outdoor = main_condition in ["Clear", "Clouds"] and total_precip < 1
            
        else:
            high_temp = 22
            low_temp = 15
            avg_humidity = 60
            avg_wind = 10
            condition_cn = "多云"
            precip_prob = 20
            suitable_outdoor = True
        
        forecast_list.append(
            {
                "date": forecast_date.strftime("%Y-%m-%d"),
                "day_of_week": _get_day_of_week_cn(forecast_date.weekday()),
                "condition": condition_cn,
                "condition_icon": _get_weather_icon(condition_cn),
                "temperature": {"high": round(high_temp), "low": round(low_temp)},
                "humidity": round(avg_humidity),
                "wind_speed": round(avg_wind),
                "precipitation_probability": precip_prob,
                "suitable_for_outdoor": suitable_outdoor,
            }
        )
    
    return {"status": "success", "forecast": forecast_list}


def _get_mock_weather_forecast(
    latitude: float, longitude: float, days: int
) -> Dict[str, Any]:
    """Generate mock weather forecast data for development."""
    today = datetime.now().date()
    forecast_list = []

    conditions = ["晴天", "多云", "晴天", "小雨", "多云", "晴天", "多云"]
    base_temp = 20

    for i in range(days):
        forecast_date = today + timedelta(days=i)
        condition = conditions[i % len(conditions)]
        temp_variation = (i % 3) * 2 - 2

        forecast_list.append(
            {
                "date": forecast_date.strftime("%Y-%m-%d"),
                "day_of_week": _get_day_of_week_cn(forecast_date.weekday()),
                "condition": condition,
                "condition_icon": _get_weather_icon(condition),
                "temperature": {
                    "high": base_temp + temp_variation + 5,
                    "low": base_temp + temp_variation,
                },
                "humidity": 60 + (i % 3) * 5,
                "wind_speed": 8 + (i % 3) * 2,
                "precipitation_probability": 20 if "雨" not in condition else 70,
                "suitable_for_outdoor": "雨" not in condition,
            }
        )

    return {"status": "success", "forecast": forecast_list}


def _map_condition_to_chinese(condition: str) -> str:
    """Map English weather condition to Chinese."""
    condition_lower = condition.lower()
    
    openweather_map = {
        "clear": "晴天",
        "clouds": "多云",
        "rain": "雨天",
        "drizzle": "小雨",
        "thunderstorm": "雷雨",
        "snow": "雪天",
        "mist": "雾",
        "fog": "雾",
        "haze": "雾",
    }
    
    general_map = {
        "clear": "晴天",
        "sunny": "晴天",
        "partly cloudy": "多云",
        "cloudy": "多云",
        "overcast": "阴天",
        "rain": "雨天",
        "rainy": "雨天",
        "drizzle": "小雨",
        "showers": "阵雨",
        "thunderstorm": "雷雨",
        "snow": "雪天",
        "snowy": "雪天",
        "mist": "雾",
        "fog": "雾",
        "foggy": "雾",
    }
    
    if condition_lower in openweather_map:
        return openweather_map[condition_lower]
    
    if condition_lower in general_map:
        return general_map[condition_lower]
    
    for key, value in {**openweather_map, **general_map}.items():
        if key in condition_lower or condition_lower in key:
            return value
    
    return "多云"


def _get_day_of_week_cn(weekday: int) -> str:
    """Get Chinese day of week."""
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return days[weekday]


def _get_weather_icon(condition: str) -> str:
    """Get weather icon emoji."""
    icon_map = {
        "晴天": "☀️",
        "多云": "⛅",
        "雨天": "🌧️",
        "小雨": "🌦️",
        "雷雨": "⛈️",
        "雪天": "❄️",
        "雾": "🌫️",
    }
    return icon_map.get(condition, "🌤️")
