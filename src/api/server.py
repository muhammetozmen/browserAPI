"""
FastAPI Server module for the browserAPI project.
Handles local HTTP endpoints, lifespan startup session checks,
periodic background cookie synchronization, and query routing.
"""

import asyncio
import sys
import json
import time
import uuid
import base64
import urllib.request
import tempfile
import os
import mimetypes
from typing import Optional, Union, List, Dict, Any, Tuple
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

from src.core.config import get_config
from src.core.cookies import get_cookies
from src.services.gemini_io import verify_session, send_prompt, get_gemini_client
from src.api.dashboard_html import DASHBOARD_HTML
from src.core.notifications import send_desktop_notification

def t(en: str, tr: str) -> str:
    """
    Translation helper function.
    """
    lang = get_config("gemini", "language")
    return tr if lang == "tr" else en

# Background task loop for cookie sync
async def cookie_sync_loop():
    """
    Periodically extracts cookies from the browser in the background
    based on the configured refresh interval.
    """
    while True:
        try:
            interval = get_config("meta", "cookie_update") or 600
            await asyncio.sleep(interval)
            
            print(" [>] " + t("Background Task: Synchronizing browser session cookies...", "Arka Plan Görevi: Tarayıcı oturum çerezleri eşitleniyor..."))
            cookies = get_cookies()
            if cookies:
                # Force-refresh client session with new cookies
                await get_gemini_client(force_refresh=True)
                print(" [+] " + t("Background Task: Cookies synchronized successfully.", "Arka Plan Görevi: Çerezler başarıyla eşitlendi."))
            else:
                print(" [-] " + t("Background Task: Cookie synchronization failed.", "Arka Plan Görevi: Çerez eşitlemesi başarısız oldu."))
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(" [-] " + t(f"Background Task Error: {e}", f"Arka Plan Görevi Hatası: {e}"))
            await asyncio.sleep(60)  # Wait a minute before retrying on error

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events handler managing server startup and shutdown hooks.
    """
    print("\n [>] " + t("Initializing local API session cookies...", "Yerel API oturum çerezleri başlatılıyor..."))
    cookies = get_cookies()
    if cookies:
        print(" [+] " + t("Session cookies initialized.", "Oturum çerezleri başlatıldı."))
        if await verify_session():
            print(" [+] " + t("Gemini session connection verified and healthy.", "Gemini oturum bağlantısı doğrulandı ve sağlıklı."))
        else:
            print(" \033[91m[-] " + t("Warning: Gemini session verification failed. Cookies might be expired.", "Uyarı: Gemini oturum doğrulaması başarısız oldu. Çerezlerin süresi dolmuş olabilir.") + "\033[0m")
            send_desktop_notification(
                "browserAPI Gateway",
                t("Warning: Session validation failed on startup. Please check cookies.", "Uyarı: Başlangıçta oturum doğrulaması başarısız oldu. Lütfen çerezleri kontrol edin.")
            )
    else:
        print(" \033[91m[-] " + t("Warning: No cookies extracted. Server queries may fail.", "Uyarı: Çerez ayıklanamadı. Sunucu sorguları başarısız olabilir.") + "\033[0m")
        send_desktop_notification(
            "browserAPI Gateway",
            t("Warning: No session cookies found. Please run the CLI Setup Wizard.", "Uyarı: Oturum çerezi bulunamadı. Lütfen CLI Kurulum Sihirbazını çalıştırın.")
        )
        
    # Start the periodic background sync task
    sync_task = asyncio.create_task(cookie_sync_loop())
    yield
    # Shutdown: Cancel background task
    sync_task.cancel()
    try:
        await sync_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="browserAPI Gateway",
    description="Local HTTP API proxy for Google Gemini Web Client",
    version="1.0",
    lifespan=lifespan
)

# Resolve project-local scratch directory for temporary multimodal files
SCRATCH_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "scratch"
)

def parse_multimodal_message(content: Union[str, List[Dict[str, Any]]]) -> Tuple[str, List[str]]:
    """
    Parses a message content (either a string or a list of content parts).
    Extracts the combined text prompt and a list of absolute paths to
    temporary image files stored in the scratch directory.
    """
    if isinstance(content, str):
        return content, []
        
    text_parts = []
    temp_filepaths = []
    
    # Ensure scratch directory exists
    if not os.path.exists(SCRATCH_DIR):
        os.makedirs(SCRATCH_DIR, exist_ok=True)
        
    for part in content:
        if not isinstance(part, dict):
            continue
        part_type = part.get("type")
        if part_type == "text":
            text = part.get("text", "")
            if text:
                text_parts.append(text)
        elif part_type == "image_url":
            image_url_obj = part.get("image_url")
            if isinstance(image_url_obj, dict):
                url = image_url_obj.get("url", "")
            else:
                url = str(image_url_obj) if image_url_obj else ""
                
            if not url:
                continue
                
            file_bytes = None
            ext = ".png"
            
            if url.startswith("data:"):
                try:
                    # Handle base64 data URLs: data:image/png;base64,...
                    header, encoded = url.split(",", 1)
                    mime_type = "image/png"
                    if ";" in header:
                        parts = header.split(";")
                        if parts[0].startswith("data:"):
                            mime_type = parts[0][5:]
                    
                    ext = mimetypes.guess_extension(mime_type) or ".png"
                    file_bytes = base64.b64decode(encoded)
                except Exception as e:
                    print(f" [-] Failed to decode base64 image URL: {e}")
            elif url.startswith("http://") or url.startswith("https://"):
                try:
                    # Fetch image bytes from HTTP URL
                    req = urllib.request.Request(
                        url,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                    )
                    with urllib.request.urlopen(req, timeout=10) as response:
                        file_bytes = response.read()
                        content_type = response.headers.get("content-type", "image/png")
                        ext = mimetypes.guess_extension(content_type) or ".png"
                except Exception as e:
                    print(f" [-] Failed to fetch image from URL {url}: {e}")
            
            if file_bytes:
                try:
                    # Save bytes to a project-local temporary file
                    fd, temp_path = tempfile.mkstemp(suffix=ext, dir=SCRATCH_DIR)
                    with os.fdopen(fd, "wb") as temp_file:
                        temp_file.write(file_bytes)
                    temp_filepaths.append(temp_path)
                except Exception as e:
                    print(f" [-] Failed to write temporary image file: {e}")
                    
    return "\n".join(text_parts), temp_filepaths

class QueryRequest(BaseModel):
    prompt: str
    model_type: str = "default"  # 'default' or 'strong'

class QueryResponse(BaseModel):
    status: str
    response: Optional[str] = None
    error: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: Union[str, List[Dict[str, Any]]]

class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

@app.get("/health")
async def health_check():
    """
    Returns server status and runs session health checks against Gemini.
    """
    is_healthy = await verify_session()
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "gemini_connection": "verified" if is_healthy else "disconnected",
        "default_browser": get_config("cookies", "default_browser")
    }

@app.post("/generate", response_model=QueryResponse)
async def generate(request: QueryRequest):
    """
    Exposes POST /generate endpoint to run prompts against Gemini.
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
        
    try:
        # Run query through the integration service with built-in retries
        response_text = await send_prompt(request.prompt, model_type=request.model_type)
        return QueryResponse(status="success", response=response_text)
    except Exception as e:
        # Return error with truncated context
        return QueryResponse(status="error", error=str(e))

async def handle_chat_completion(request: ChatCompletionRequest, forced_model_type: Optional[str] = None):
    """
    Core logic to handle chat completion requests and map them to the proper model.
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty.")
        
    # Extract the last user message content
    last_user_msg = next((msg.content for msg in reversed(request.messages) if msg.role == "user"), None)
    if not last_user_msg:
        raise HTTPException(status_code=400, detail="No user message found in the messages history.")
        
    # Parse multimodal input (extract text prompt and temporary files)
    prompt_text, temp_files = parse_multimodal_message(last_user_msg)
    
    if not prompt_text.strip() and not temp_files:
        raise HTTPException(status_code=400, detail="User message prompt content cannot be empty.")
        
    # Map the requested model ID to the configuration keys
    if forced_model_type:
        model_type = forced_model_type
    else:
        model_type = "default"
        if "pro" in request.model.lower():
            model_type = "strong"
        elif "lite" in request.model.lower():
            model_type = "weak"
            
    # Track whether ownership of temp_files has been transferred to streaming generator
    temp_files_transferred = False
    
    try:
        # Support OpenAI-compatible streaming
        if request.stream:
            temp_files_transferred = True
            return StreamingResponse(
                stream_response_generator(prompt_text, model_type, request.model, files=temp_files),
                media_type="text/event-stream"
            )
            
        response_text = await send_prompt(prompt_text, model_type=model_type, files=temp_files)
        
        chat_id = f"chatcmpl-{uuid.uuid4()}"
        
        return {
            "id": chat_id,
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary files if they were not transferred to the streaming generator
        if not temp_files_transferred and temp_files:
            for file_path in temp_files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as cleanup_err:
                    print(f" [-] Failed to delete temporary file {file_path}: {cleanup_err}")

@app.get("/v1/models")
def list_models():
    """
    OpenAI-compatible models listing.
    """
    return {
        "object": "list",
        "data": [
            {"id": "gemini-2.0-flash-lite", "object": "model", "owned_by": "google"},
            {"id": "gemini-2.0-flash", "object": "model", "owned_by": "google"},
            {"id": "gemini-1.5-pro", "object": "model", "owned_by": "google"}
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    OpenAI-compatible chat completions endpoint.
    """
    return await handle_chat_completion(request)

# --- Default Model Endpoint ---
@app.get("/v1/default/models")
def list_default_models():
    """
    OpenAI models listing showing only the default model.
    """
    return {
        "object": "list",
        "data": [
            {"id": "gemini-2.0-flash", "object": "model", "owned_by": "google"}
        ]
    }

@app.post("/v1/default/chat/completions")
async def default_chat_completions(request: ChatCompletionRequest):
    """
    OpenAI chat completions forcing the default model.
    """
    return await handle_chat_completion(request, forced_model_type="default")

# --- Strong Model Endpoint ---
@app.get("/v1/strong/models")
def list_strong_models():
    """
    OpenAI models listing showing only the strong model.
    """
    return {
        "object": "list",
        "data": [
            {"id": "gemini-1.5-pro", "object": "model", "owned_by": "google"}
        ]
    }

@app.post("/v1/strong/chat/completions")
async def strong_chat_completions(request: ChatCompletionRequest):
    """
    OpenAI chat completions forcing the strong model.
    """
    return await handle_chat_completion(request, forced_model_type="strong")

# --- Weak Model Endpoint ---
@app.get("/v1/weak/models")
def list_weak_models():
    """
    OpenAI models listing showing only the weak model.
    """
    return {
        "object": "list",
        "data": [
            {"id": "gemini-2.0-flash-lite", "object": "model", "owned_by": "google"}
        ]
    }

@app.post("/v1/weak/chat/completions")
async def weak_chat_completions(request: ChatCompletionRequest):
    """
    OpenAI chat completions forcing the weak model.
    """
    return await handle_chat_completion(request, forced_model_type="weak")

# --- Streaming Generator Helper ---
async def stream_response_generator(prompt: str, model_type: str, model_name: str, files: Optional[list] = None):
    """
    Simulates SSE streaming chunks compatible with standard OpenAI client protocols.
    """
    try:
        response_text = await send_prompt(prompt, model_type=model_type, files=files)
        chat_id = f"chatcmpl-{uuid.uuid4()}"
        created_time = int(time.time())
        
        # Tokenize by space to yield natural-looking word flow
        words = response_text.split(" ")
        for idx, word in enumerate(words):
            content = word + " " if idx < len(words) - 1 else word
            chunk = {
                "id": chat_id,
                "object": "chat.completion.chunk",
                "created": created_time,
                "model": model_name,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": content},
                        "finish_reason": None
                    }
                ]
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            await asyncio.sleep(0.015)
            
        final_chunk = {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": created_time,
            "model": model_name,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }
            ]
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        err_chunk = {
            "error": {
                "message": str(e),
                "type": "server_error",
                "code": 500
            }
        }
        yield f"data: {json.dumps(err_chunk)}\n\n"
        yield "data: [DONE]\n\n"
    finally:
        # Clean up temporary files used for multimodal input
        if files:
            for file_path in files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as cleanup_err:
                    print(f" [-] Failed to delete temporary file {file_path}: {cleanup_err}")

# --- Web Control Dashboard Endpoints ---
@app.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard():
    """
    Renders the browserAPI Control Panel dashboard.
    """
    return HTMLResponse(content=DASHBOARD_HTML)

@app.get("/api/status")
def get_api_status():
    """
    Exposes current configurations to the dashboard.
    """
    return {
        "default_browser": get_config("cookies", "default_browser"),
        "host": get_config("server", "host"),
        "port": get_config("server", "port"),
        "default_model": get_config("gemini", "default_model"),
        "strong_model": get_config("gemini", "strong_model"),
        "weak_model": get_config("gemini", "weak_model"),
        "cookie_update": get_config("meta", "cookie_update")
    }

@app.post("/api/sync")
async def trigger_api_sync():
    """
    Enables manual browser cookie extraction trigger from the dashboard.
    """
    try:
        cookies = get_cookies()
        if cookies:
            await get_gemini_client(force_refresh=True)
            is_healthy = await verify_session()
            return {"status": "success", "session_healthy": is_healthy}
        return {"status": "error", "message": "Failed to extract cookies"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def start_server():
    """
    Loads host and port from config and starts the Uvicorn web server.
    """
    host = get_config("server", "host") or "127.0.0.1"
    port = get_config("server", "port") or 4747
    
    print(f" [>] " + t(f"Starting Local API Gateway on http://{host}:{port} ...", f"Yerel API Geçidi http://{host}:{port} adresinde başlatılıyor..."))
    uvicorn.run(app, host=host, port=port, log_level="info")
