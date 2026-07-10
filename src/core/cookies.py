"""
Cookie resolution and extraction module for the browserAPI project.
Handles resolving standard browser cookie database paths, expanding wildcards,
and presenting manual locating instructions if the path cannot be resolved.
"""

import os
import sys
import glob
import json
import sqlite3
import shutil
import tempfile
import hashlib
from pathlib import Path
from typing import Optional, Dict
from Crypto.Cipher import AES

def t(en: str, tr: str) -> str:
    """
    Translation helper function that retrieves configured language.
    """
    try:
        from src.core.config import get_config
        lang = get_config("gemini", "language")
    except Exception:
        lang = "en"
    return tr if lang == "tr" else en

def get_os_name() -> str:
    """
    Detects the current host operating system and maps it to a standard key.
    
    Returns:
        str: 'windows', 'linux', or 'darwin'.
    """
    plat = sys.platform
    if plat.startswith("win"):
        return "windows"
    elif plat.startswith("darwin"):
        return "darwin"
    else:
        # Fallback to linux for other unix-like systems
        return "linux"

def get_path(browser_name: str) -> Optional[Path]:
    """
    Dynamically resolves the absolute path to the browser's cookie database file.
    Uses browser.json path definitions, expands user paths, and handles wildcards.
    
    Args:
        browser_name (str): The browser identifier (e.g. 'chrome', 'firefox').
        
    Returns:
        Optional[Path]: Validated Path object, or None if not found.
    """
    # browser.json sits in the project root (two levels up from src/core/cookies.py)
    json_path = Path(__file__).parent.parent.parent / "browser.json"
    if not json_path.exists():
        print(" [-] " + t("Error: browser.json mapping file is missing.", "Hata: browser.json eşleme dosyası eksik."))
        return None
        
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            browser_mappings = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(" [-] " + t(f"Error: Failed to read browser.json: {e}", f"Hata: browser.json okunamadı: {e}"))
        return None
        
    browser_data = browser_mappings.get(browser_name.lower())
    if not browser_data:
        return None
        
    os_name = get_os_name()
    candidates = browser_data.get(os_name, [])
    
    for candidate in candidates:
        # Expand user directory (e.g. ~/)
        expanded = os.path.expanduser(candidate)
        
        # Handle wildcards (e.g. Firefox profile directories)
        if "*" in expanded:
            matched_paths = glob.glob(expanded)
            if matched_paths:
                # Return the first matching path that exists
                for match in matched_paths:
                    p = Path(match)
                    if p.exists() and p.is_file():
                        # Exclude write-layers of overlayfs (PSD)
                        if "-rw" in p.parent.name or "-rw" in p.name:
                            continue
                        return p
        else:
            p = Path(expanded)
            if p.exists() and p.is_file():
                # Exclude write-layers of overlayfs (PSD)
                if "-rw" in p.parent.name or "-rw" in p.name:
                    continue
                return p
                
    return None

def get_browser_guide(browser_name: str, os_name: str) -> str:
    """
    Returns step-by-step guidance on how to find the cookie file manually.
    
    Args:
        browser_name (str): Browser identifier.
        os_name (str): Operating system key.
        
    Returns:
        str: Descriptive guide text.
    """
    browser = browser_name.lower()
    
    guides: Dict[str, Dict[str, str]] = {
        "chrome": {
            "linux": t("Look in '~/.config/google-chrome/'. Typically located at '~/.config/google-chrome/Default/Cookies'.",
                       "'~/.config/google-chrome/' dizinine bakın. Genellikle '~/.config/google-chrome/Default/Cookies' konumundadır."),
            "windows": t("Press Win+R, type '%localappdata%\\Google\\Chrome\\User Data', and check 'Default\\Network\\Cookies'.",
                         "Win+R tuşlarına basın, '%localappdata%\\Google\\Chrome\\User Data' yazın ve 'Default\\Network\\Cookies' dosyasını kontrol edin."),
            "darwin": t("Look in '~/Library/Application Support/Google/Chrome/Default/Cookies'.",
                        "'~/Library/Application Support/Google/Chrome/Default/Cookies' dizinine bakın.")
        },
        "firefox": {
            "linux": t("Look in '~/.mozilla/firefox/'. Find your active profile folder (e.g. 'xxxxx.default-release') and locate 'cookies.sqlite'.",
                       "'~/.mozilla/firefox/' dizinine bakın. Aktif profil klasörünüzü bulun (örn. 'xxxxx.default-release') ve 'cookies.sqlite' dosyasını bulun."),
            "windows": t("Press Win+R, type '%appdata%\\Mozilla\\Firefox\\Profiles', open your active profile folder, and locate 'cookies.sqlite'.",
                         "Win+R tuşlarına basın, '%appdata%\\Mozilla\\Firefox\\Profiles' yazın, aktif profil klasörünüzü açın ve 'cookies.sqlite' dosyasını bulun."),
            "darwin": t("Look in '~/Library/Application Support/Firefox/Profiles/'. Find your active profile folder and locate 'cookies.sqlite'.",
                        "'~/Library/Application Support/Firefox/Profiles/' dizinine bakın. Aktif profil klasörünüzü bulun ve 'cookies.sqlite' dosyasını bulun.")
        },
        "edge": {
            "linux": t("Look in '~/.config/microsoft-edge/' and locate 'Default/Cookies'.",
                       "'~/.config/microsoft-edge/' dizinine bakın ve 'Default/Cookies' dosyasını bulun."),
            "windows": t("Press Win+R, type '%localappdata%\\Microsoft\\Edge\\User Data', and check 'Default\\Network\\Cookies'.",
                         "Win+R tuşlarına basın, '%localappdata%\\Microsoft\\Edge\\User Data' yazın ve 'Default\\Network\\Cookies' dosyasını kontrol edin."),
            "darwin": t("Look in '~/Library/Application Support/Microsoft Edge/Default/Cookies'.",
                        "'~/Library/Application Support/Microsoft Edge/Default/Cookies' dizinine bakın.")
        },
        "brave": {
            "linux": t("Look in '~/.config/BraveSoftware/Brave-Browser/Default/Cookies'.",
                       "'~/.config/BraveSoftware/Brave-Browser/Default/Cookies' konumuna bakın."),
            "windows": t("Press Win+R, type '%localappdata%\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Network\\Cookies'.",
                         "Win+R tuşlarına basın, '%localappdata%\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Network\\Cookies' yazın."),
            "darwin": t("Look in '~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Cookies'.",
                        "'~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Cookies' konumuna bakın.")
        },
        "opera": {
            "linux": t("Look in '~/.config/opera/Cookies'.",
                       "'~/.config/opera/Cookies' konumuna bakın."),
            "windows": t("Press Win+R, type '%appdata%\\Opera Software\\Opera Stable\\Cookies'.",
                         "Win+R tuşlarına basın, '%appdata%\\Opera Software\\Opera Stable\\Cookies' yazın."),
            "darwin": t("Look in '~/Library/Application Support/com.operasoftware.Opera/Cookies'.",
                        "'~/Library/Application Support/com.operasoftware.Opera/Cookies' konumuna bakın.")
        },
        "safari": {
            "linux": t("Safari is not supported on Linux.",
                       "Safari Linux üzerinde desteklenmiyor."),
            "windows": t("Safari is not supported on Windows.",
                         "Safari Windows üzerinde desteklenmiyor."),
            "darwin": t("Look in '~/Library/Cookies/Cookies.binarycookies'.",
                        "'~/Library/Cookies/Cookies.binarycookies' konumuna bakın.")
        }
    }
    
    return guides.get(browser, {}).get(
        os_name, 
        t(f"Please locate the standard cookies database file for {browser_name} on your system.",
          f"Lütfen sisteminizde {browser_name} için standart çerez veri tabanı dosyasını bulun.")
    )

def decrypt_linux_cookie(encrypted_val: bytes, key: bytes) -> str:
    """
    Decrypts a Chromium cookie value on Linux.
    Uses AES-128-CBC with a 16-space character IV, stripping PKCS#7 padding
    and handling the 32-byte hash prefix present in modern browsers.
    """
    if not encrypted_val:
        return ""
        
    # Strip the v10/v11 signature prefix if present
    if encrypted_val.startswith(b"v10") or encrypted_val.startswith(b"v11"):
        ciphertext = encrypted_val[3:]
    else:
        ciphertext = encrypted_val
        
    try:
        # Chromium uses a static IV of 16 spaces on Linux
        iv = b" " * 16
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        
        # Remove PKCS#7 padding
        padding_len = decrypted[-1]
        if 1 <= padding_len <= 16:
            plaintext = decrypted[:-padding_len]
        else:
            plaintext = decrypted
            
        # Try decoding with and without the 32-byte hash prefix
        try:
            return plaintext.decode("utf-8")
        except UnicodeDecodeError:
            # Modern Chromium prepends a 32-byte hash signature to decrypted values
            if len(plaintext) > 32:
                return plaintext[32:].decode("utf-8")
            raise
    except Exception:
        return ""

def get_keyring_password(browser_name: str) -> str:
    """
    Retrieves the encryption password from GNOME Keyring.
    Falls back to 'peanuts' if the keyring is unavailable or locked.
    """
    app_names = {
        "chrome": "chrome",
        "chromium": "chromium",
        "brave": "brave",
        "vivaldi": "vivaldi",
        "opera": "opera",
        "edge": "microsoft-edge"
    }
    app_name = app_names.get(browser_name.lower(), "chrome")
    password = "peanuts"  # Fallback default password
    
    try:
        import secretstorage
        connection = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(connection)
        
        # Search for safe storage credentials associated with the browser application name
        search_attrs = {"application": app_name}
        items = list(collection.search_items(search_attrs))
        
        # Fallback to manual label matching if application tag is missing
        if not items:
            for item in collection.get_all_items():
                label = item.get_label().lower()
                if "safe storage" in label and app_name in label:
                    items.append(item)
                    break
                    
        if items:
            password = items[0].get_secret().decode("utf-8")
    except Exception:
        # Fail silently and use fallback peanuts (common in headless/locked sandboxes)
        pass
        
    return password

def extract_firefox_cookies(db_path: Path) -> dict:
    """
    Extracts plaintext cookies from Firefox (moz_cookies).
    """
    cookies = {}
    try:
        # Copy to a temporary location to prevent database locks
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_db = Path(temp_dir) / "cookies.sqlite"
            shutil.copy2(db_path, temp_db)
            
            conn = sqlite3.connect(str(temp_db))
            cursor = conn.cursor()
            
            # Query for active Secure-1PSID tokens matching Google host keys
            cursor.execute(
                "SELECT name, value FROM moz_cookies "
                "WHERE host LIKE '%google.com' AND name IN ('__Secure-1PSID', '__Secure-1PSIDTS')"
            )
            for name, value in cursor.fetchall():
                if value:
                    cookies[name] = value
                    
            conn.close()
    except Exception as e:
        print(f" \033[91m[-] " + t(f"Error reading Firefox cookies: {e}", f"Firefox çerezleri okunurken hata oluştu: {e}") + "\033[0m")
        
    return cookies

def extract_chromium_cookies(db_path: Path, browser_name: str) -> dict:
    """
    Extracts and decrypts cookies from Chromium-based browsers.
    """
    cookies = {}
    try:
        # Retrieve key material
        password = get_keyring_password(browser_name)
        # Derive 16-byte AES key using PBKDF2 (1 iteration, HMAC-SHA1, salt='saltysalt')
        key = hashlib.pbkdf2_hmac("sha1", password.encode("utf-8"), b"saltysalt", 1, 16)
        
        # Copy to a temporary location to prevent database locks
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_db = Path(temp_dir) / "Cookies"
            shutil.copy2(db_path, temp_db)
            
            conn = sqlite3.connect(str(temp_db))
            cursor = conn.cursor()
            
            # Query for both plaintext and encrypted cookie values
            cursor.execute(
                "SELECT name, value, encrypted_value FROM cookies "
                "WHERE host_key LIKE '%google.com' AND name IN ('__Secure-1PSID', '__Secure-1PSIDTS')"
            )
            for name, plaintext_val, encrypted_val in cursor.fetchall():
                decrypted_val = ""
                if encrypted_val:
                    decrypted_val = decrypt_linux_cookie(encrypted_val, key)
                    
                val = decrypted_val if decrypted_val else plaintext_val
                if val:
                    cookies[name] = val
                    
            conn.close()
    except Exception as e:
        print(f" \033[91m[-] " + t(f"Error reading Chromium cookies: {e}", f"Chromium çerezleri okunurken hata oluştu: {e}") + "\033[0m")
        
    return cookies

def get_cookies() -> dict:
    """
    Orchestrates the cookie extraction process for the targeted browser.
    Extracts __Secure-1PSID and __Secure-1PSIDTS session values.
    
    Returns:
        dict: Extracted cookie names and values.
    """
    from src.core.config import get_config, set_config
    
    browser_name = get_config("cookies", "default_browser")
    browser_path = get_config("cookies", "browser_path")
    
    if not browser_name or not browser_path:
        print(" \033[91m[-] " + t("Error: Default browser or cookie path is not configured.", "Hata: Varsayılan tarayıcı veya çerez yolu yapılandırılmamış.") + "\033[0m")
        return {}
        
    db_path = Path(browser_path)
    if not db_path.exists():
        print(f" \033[91m[-] " + t(f"Error: Configured cookie database path does not exist: {db_path}", f"Hata: Yapılandırılan çerez veri tabanı yolu mevcut değil: {db_path}") + "\033[0m")
        return {}
        
    browser_lower = browser_name.lower()
    
    # Determine extraction strategy
    if browser_lower in ("firefox", "librewolf", "waterfox"):
        cookies = extract_firefox_cookies(db_path)
    else:
        cookies = extract_chromium_cookies(db_path, browser_name)
        
    if cookies:
        # Securely update the config with extracted token credentials
        for token_name in ("__Secure-1PSID", "__Secure-1PSIDTS"):
            if token_name in cookies:
                set_config("cookies", token_name, cookies[token_name])
        return cookies
    else:
        print(" \033[91m[-] " + t("Error: Failed to locate __Secure-1PSID or __Secure-1PSIDTS cookies in the database.", "Hata: Veri tabanında __Secure-1PSID veya __Secure-1PSIDTS çerezleri bulunamadı.") + "\033[0m")
        print("     " + t("Please ensure you are logged into Google Gemini in the selected browser.", "Lütfen seçilen tarayıcıda Google Gemini'ye giriş yaptığınızdan emin olun."))
        return {}
