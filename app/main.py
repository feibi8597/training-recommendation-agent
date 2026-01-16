#!/usr/bin/env python3
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

"""FastAPI backend for training recommendation agent with automatic welcome message."""

import logging
import os
import sys
import uuid
from pathlib import Path

# 配置日志（需要在加载 .env 之前）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加项目根目录到 Python 路径，以便能够导入 training_recommend 模块
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 在导入 agent 之前，先加载 .env 文件
from dotenv import load_dotenv

# 加载项目根目录下的 .env 文件
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"✅ 已加载环境变量文件: {env_path}")
    # 显示已加载的环境变量（不显示敏感信息）
    if "GOOGLE_GENAI_USE_VERTEXAI" in os.environ:
        logger.info(f"   GOOGLE_GENAI_USE_VERTEXAI={os.environ.get('GOOGLE_GENAI_USE_VERTEXAI')}")
    if "GOOGLE_API_KEY" in os.environ:
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        logger.info(f"   GOOGLE_API_KEY={'*' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else '***'}")
else:
    logger.warning(f"⚠️  未找到 .env 文件: {env_path}，将使用默认值或系统环境变量")

# 在导入 agent 之前，设置默认环境变量（仅当未在 .env 中设置时）
# 如果未设置 GOOGLE_GENAI_USE_VERTEXAI，默认使用 AI Studio 模式（不需要凭证）
if "GOOGLE_GENAI_USE_VERTEXAI" not in os.environ:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "0"  # 0 = AI Studio, 1 = Vertex AI
    logger.info("ℹ️  使用默认值: GOOGLE_GENAI_USE_VERTEXAI=0 (AI Studio 模式)")

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from google.adk.runners import InMemoryRunner
from google.genai import types
from training_recommend import agent
import googlemaps

app = FastAPI(title="Training Recommendation Agent")

# Mount static files
# static 目录在项目根目录下，和 app 目录同级
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Initialize runner
APP_NAME = os.getenv("APP_NAME", "training_recommend_app")
runner = InMemoryRunner(app_name=APP_NAME, agent=agent.root_agent)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page."""
    html_file = static_dir / "index.html"
    if html_file.exists():
        return html_file.read_text(encoding="utf-8")
    return "<h1>Training Recommendation Agent</h1><p>Please create index.html</p>"


@app.post("/api/create_session")
async def create_session():
    """
    创建会话并自动发送欢迎消息
    
    这是实现自动欢迎消息的核心：在会话创建时，自动发送 "WELCOME" 消息给 Agent，
    Agent 检测到这个消息后会立即回复欢迎信息。
    """
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=user_id
    )

    if not session:
        raise HTTPException(status_code=500, detail="Failed to create session")

    # 自动发送欢迎消息（相当于 Dialogflow CX 的 EventInput）
    welcome_message = types.Content(
        parts=[types.Part.from_text(text="WELCOME")], role="user"
    )

    # 流式返回欢迎消息的回复
    async def generate_welcome():
        async for event in runner.run_async(
            user_id=user_id, session_id=session.id, new_message=welcome_message
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        yield f"data: {part.text}\n\n"
            if event.is_final_response():
                yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_welcome(),
        media_type="text/event-stream",
        headers={
            "X-User-Id": user_id,
            "X-Session-Id": session.id,
        },
    )


@app.get("/api/geocode")
async def geocode(lat: float, lng: float):
    """
    将经纬度转换为详细地址信息
    
    Args:
        lat: 纬度
        lng: 经度
    
    Returns:
        JSON 包含城市、完整地址和详细地址组件
    """
    maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY") or os.environ.get("MAPS_API_KEY")
    
    if not maps_api_key:
        logger.warning("⚠️  Google Maps API key not found")
        raise HTTPException(
            status_code=500,
            detail="Google Maps API key not configured"
        )
    
    try:
        gmaps = googlemaps.Client(key=maps_api_key)
        
        # 反向地理编码：将经纬度转换为地址
        # 指定语言为中文，确保返回中文地址
        reverse_geocode_result = gmaps.reverse_geocode((lat, lng), language='zh-CN')
        
        if not reverse_geocode_result:
            raise HTTPException(
                status_code=404,
                detail="No address found for the given coordinates"
            )
        
        # 解析地址信息
        result = reverse_geocode_result[0]
        formatted_address = result.get("formatted_address", "")
        
        # 提取地址组件
        address_components = {}
        for component in result.get("address_components", []):
            types_list = component.get("types", [])
            long_name = component.get("long_name", "")
            
            if "locality" in types_list:  # 城市
                address_components["city"] = long_name
            elif "administrative_area_level_1" in types_list:  # 省/州
                address_components["province"] = long_name
            elif "administrative_area_level_2" in types_list:  # 区/县
                address_components["district"] = long_name
            elif "country" in types_list:  # 国家
                address_components["country"] = long_name
            elif "street_address" in types_list or "route" in types_list:  # 街道
                address_components["street"] = long_name
        
        # 确定城市名称（优先使用 locality，否则使用 administrative_area_level_1）
        city = (
            address_components.get("city") or 
            address_components.get("district") or 
            address_components.get("province") or 
            "未知城市"
        )
        
        return JSONResponse({
            "city": city,
            "formatted_address": formatted_address,
            "address": address_components,
            "latitude": lat,
            "longitude": lng
        })
        
    except Exception as e:
        logger.error(f"❌ Geocoding error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Geocoding failed: {str(e)}"
        )


@app.post("/api/send_message")
async def send_message(request: Request):
    """Send a message to the agent."""
    # Get form data
    form_data = await request.form()
    user_id = form_data.get("user_id")
    session_id = form_data.get("session_id")
    message = form_data.get("message")

    if not user_id or not session_id or not message:
        raise HTTPException(status_code=400, detail="Missing required parameters")

    content = types.Content(parts=[types.Part.from_text(text=message)], role="user")

    async def generate_response():
        try:
            async for event in runner.run_async(
                user_id=user_id, session_id=session_id, new_message=content
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            yield f"data: {part.text}\n\n"
                if event.is_final_response():
                    yield "data: [DONE]\n\n"
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg and "PERMISSION_DENIED" in error_msg:
                yield f"data: ⚠️ API Key 配置错误：\n\n"
                yield f"data: 错误信息：{error_msg}\n\n"
                yield f"data: \n\n"
                yield f"data: 请检查：\n\n"
                yield f"data: 1. 访问 https://console.cloud.google.com/apis/credentials 检查 API Key 状态\n\n"
                yield f"data: 2. 访问 https://aistudio.google.com/apikey 创建新的 API Key\n\n"
                yield f"data: 3. 确保在 .env 文件中正确配置了 GOOGLE_API_KEY\n\n"
                yield f"data: 4. 确保启用了 Generative Language API\n\n"
            else:
                yield f"data: 抱歉，处理消息时出现错误：{error_msg}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_response(), media_type="text/event-stream"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
