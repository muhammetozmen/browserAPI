"""
Gemini integration service module for the browserAPI project.
Handles authenticating, sending prompt queries, retries with backoff,
and error context truncation using the gemini-webapi library.
"""

import sys
import asyncio
import re
from typing import Optional
from gemini_webapi import GeminiClient
from src.core.config import get_config
from src.core.cookies import get_cookies
from src.core.notifications import send_desktop_notification

def t(en: str, tr: str) -> str:
    """
    Translation helper function.
    """
    lang = get_config("gemini", "language")
    return tr if lang == "tr" else en

# Global cached client instance
_client: Optional[GeminiClient] = None

async def get_gemini_client(force_refresh: bool = False) -> GeminiClient:
    """
    Retrieves the cached GeminiClient instance, initializing it if necessary.
    
    Args:
        force_refresh (bool): If True, re-initializes the client from scratch.
        
    Returns:
        GeminiClient: Authenticated client instance.
    """
    global _client
    if _client is not None and not force_refresh:
        return _client
        
    psid = get_config("cookies", "__Secure-1PSID")
    psidts = get_config("cookies", "__Secure-1PSIDTS")
    
    if not psid:
        raise ValueError("__Secure-1PSID session cookie is not configured.")
        
    # Lazy initialization with modern asynchronous setup
    _client = GeminiClient(secure_1psid=psid, secure_1psidts=psidts)
    await _client.init()
    
    # Configure default conversation language if set
    lang = get_config("gemini", "language")
    if lang:
        _client.language = lang
    
    return _client

def truncate_error(error_msg: str, max_length: int = 500) -> str:
    """
    Truncates the error message/context to the specified max_length.
    """
    if len(error_msg) <= max_length:
        return error_msg
    return error_msg[:max_length - 3] + "..."

def clean_response_text(text: str) -> str:
    """
    Cleans generated response text by stripping out inline markdown images
    and raw googleusercontent media/search links.
    """
    if not text:
        return ""
    # Strip markdown image tags: ![alt](url)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Strip raw googleusercontent content/image links
    text = re.sub(r'https?://googleusercontent\.com/lmd[xX]_[^\s\)]+', '', text)
    # Normalize double/triple newlines left from stripping
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

async def send_prompt(prompt: str, model_type: str = "default", files: Optional[list] = None, max_retries: int = 3, backoff_factor: float = 1.5, temporary: bool = True) -> str:
    """
    Sends a query prompt to the Gemini client with a robust retry system.
    
    Args:
        prompt (str): The text prompt to generate content for.
        model_type (str): Either 'default', 'strong', or 'weak' (mapped to config settings).
        files (list): Optional list of file paths or byte streams to attach.
        max_retries (int): Maximum number of retry attempts (default: 3).
        backoff_factor (float): Multiplier for exponential backoff delay.
        temporary (bool): If True, runs the query in a temporary chat thread.
        
    Returns:
        str: Generated text response from Gemini.
        
    Raises:
        RuntimeError: If all retries fail, containing the truncated error context.
    """
    last_error = ""
    delay = 1.0
    
    for attempt in range(1, max_retries + 1):
        try:
            client = await get_gemini_client()
            
            # Map model type to actual models in the future if required; 
            # gemini-webapi defaults to gemini-2.5-flash which is perfect.
            response = await client.generate_content(prompt, files=files, temporary=temporary)
            if response and response.text:
                return clean_response_text(response.text)
                
            raise ValueError("Received an empty response payload from Gemini.")
                
        except Exception as e:
            exc_type, exc_value, _ = sys.exc_info()
            err_details = f"[{exc_type.__name__}] {exc_value}"
            last_error = truncate_error(err_details, max_length=500)
            
            # Print retry warning in red
            print(" [-] " + t(f"Attempt {attempt}/{max_retries} failed: {last_error}", f"{attempt}/{max_retries} denemesi başarısız oldu: {last_error}"))
            
            if attempt < max_retries:
                await asyncio.sleep(delay)
                delay *= backoff_factor
                # Re-extract cookies immediately on failure and reload client
                try:
                    print(" [>] " + t("Attempting immediate session cookie refresh from browser database...", "Tarayıcı veri tabanından hemen oturum çerezlerini yenileme deneniyor..."))
                    get_cookies()
                    await get_gemini_client(force_refresh=True)
                except Exception as refresh_err:
                    print(" [-] " + t(f"Immediate cookie refresh failed: {refresh_err}", f"Anlık çerez yenileme başarısız oldu: {refresh_err}"))
            else:
                # Trigger native desktop notification on final failure
                send_desktop_notification(
                    "browserAPI Gateway",
                    t("Session cookies expired or disconnected. Please open gemini.google.com to authenticate.",
                      "Oturum çerezlerinin süresi doldu veya bağlantı kesildi. Lütfen kimlik doğrulaması yapmak için gemini.google.com adresini açın.")
                )
                break
                
    raise RuntimeError(t(f"Failed to query Gemini after {max_retries} attempts. Last error context: {last_error}",
                         f"{max_retries} denemeden sonra Gemini sorgulanamadı. Son hata bağlamı: {last_error}"))

async def verify_session() -> bool:
    """
    Diagnostic health check function.
    Sends a standard non-temporary prompt to verify the signed-in session.
    
    Returns:
        bool: True if authentication is valid, False otherwise.
    """
    try:
        response_text = await send_prompt(
            "If you can read this, this means your session is working perfectly! Just say `Yes` to me gemini",
            max_retries=2,
            temporary=False
        )
        return bool(response_text)
    except Exception as e:
        truncated_err = truncate_error(str(e), max_length=300)
        print(f" \033[91m[-] " + t(f"Session verification failed: {truncated_err}", f"Oturum doğrulaması başarısız oldu: {truncated_err}") + "\033[0m")
        return False
