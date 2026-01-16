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

"""Gear recommendation tool for training recommendation agent."""

from typing import Dict, Any
from google.adk.tools import ToolContext


# Gear recommendation map based on sport type
GEAR_MAP = {
    "长跑": {
        "shoes": ["跑步鞋", "运动鞋"],
        "clothing": ["速干T恤", "运动短裤", "运动袜"],
        "accessories": ["运动手表", "水壶", "毛巾"],
    },
    "跑步": {
        "shoes": ["跑步鞋", "运动鞋"],
        "clothing": ["速干T恤", "运动短裤", "运动袜"],
        "accessories": ["运动手表", "水壶", "毛巾"],
    },
    "running": {
        "shoes": ["跑步鞋", "运动鞋"],
        "clothing": ["速干T恤", "运动短裤", "运动袜"],
        "accessories": ["运动手表", "水壶", "毛巾"],
    },
    "游泳": {
        "shoes": [],
        "clothing": ["泳衣", "泳帽", "泳镜", "浴巾"],
        "accessories": ["防水袋", "拖鞋", "洗护用品"],
    },
    "swimming": {
        "shoes": [],
        "clothing": ["泳衣", "泳帽", "泳镜", "浴巾"],
        "accessories": ["防水袋", "拖鞋", "洗护用品"],
    },
    "力量训练": {
        "shoes": ["训练鞋"],
        "clothing": ["运动背心", "运动长裤", "运动手套"],
        "accessories": ["水壶", "毛巾", "护腕"],
    },
    "健身": {
        "shoes": ["训练鞋"],
        "clothing": ["运动背心", "运动长裤", "运动手套"],
        "accessories": ["水壶", "毛巾", "护腕"],
    },
    "gym": {
        "shoes": ["训练鞋"],
        "clothing": ["运动背心", "运动长裤", "运动手套"],
        "accessories": ["水壶", "毛巾", "护腕"],
    },
    "瑜伽": {
        "shoes": [],
        "clothing": ["瑜伽服", "瑜伽裤", "运动内衣"],
        "accessories": ["瑜伽垫", "瑜伽砖", "瑜伽带"],
    },
    "yoga": {
        "shoes": [],
        "clothing": ["瑜伽服", "瑜伽裤", "运动内衣"],
        "accessories": ["瑜伽垫", "瑜伽砖", "瑜伽带"],
    },
    "骑行": {
        "shoes": ["骑行鞋"],
        "clothing": ["骑行服", "骑行裤", "头盔"],
        "accessories": ["水壶", "手套", "护目镜"],
    },
    "自行车": {
        "shoes": ["骑行鞋"],
        "clothing": ["骑行服", "骑行裤", "头盔"],
        "accessories": ["水壶", "手套", "护目镜"],
    },
    "cycling": {
        "shoes": ["骑行鞋"],
        "clothing": ["骑行服", "骑行裤", "头盔"],
        "accessories": ["水壶", "手套", "护目镜"],
    },
    "篮球": {
        "shoes": ["篮球鞋"],
        "clothing": ["运动背心", "运动短裤"],
        "accessories": ["护膝", "护腕", "水壶"],
    },
    "羽毛球": {
        "shoes": ["羽毛球鞋"],
        "clothing": ["运动T恤", "运动短裤"],
        "accessories": ["羽毛球拍", "羽毛球", "护腕"],
    },
    "爬山": {
        "shoes": ["登山鞋"],
        "clothing": ["速干衣", "冲锋衣", "运动长裤"],
        "accessories": ["登山杖", "背包", "水壶"],
    },
}


def get_recommended_gear(
    sport_type: str, tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Get recommended gear for a specific sport type.

    This tool returns recommended gear (shoes, clothing, accessories)
    based on the sport type using a predefined map.

    Args:
        sport_type: Type of sport (e.g., "长跑", "游泳", "力量训练", "瑜伽", "骑行")
        tool_context: ADK tool context

    Returns:
        dict: A dictionary containing:
            - status: "success"
            - sport_type: The sport type
            - recommended_gear: Dictionary with shoes, clothing, and accessories
    """
    sport_type_lower = sport_type.lower()

    # Try to find exact match first
    gear = GEAR_MAP.get(sport_type) or GEAR_MAP.get(sport_type_lower)

    # If not found, try to match by keyword
    if not gear:
        for key, value in GEAR_MAP.items():
            if key.lower() in sport_type_lower or sport_type_lower in key.lower():
                gear = value
                break

    # Default gear if not found
    if not gear:
        gear = {
            "shoes": ["运动鞋"],
            "clothing": ["运动服", "运动裤"],
            "accessories": ["水壶", "毛巾"],
        }

    return {
        "status": "success",
        "sport_type": sport_type,
        "recommended_gear": gear,
    }
