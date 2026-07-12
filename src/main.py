"""
Main entry point for the browserAPI CLI application.
Handles the command-line interface, lifecycle, and initialization workflow.
"""

import os
import sys
import socket
from pathlib import Path

def validate_server_settings(host: str, port: int) -> tuple[bool, str]:
    """
    Validates host address and checks if the port is unoccupied.
    
    Returns:
        (bool, str): (True, "") if valid and available, (False, error_message) otherwise.
    """
    # Verify port range
    if not (1 <= port <= 65535):
        return False, t("Port must be an integer between 1 and 65535.", "Bağlantı noktası 1 ile 65535 arasında bir tam sayı olmalıdır.")
        
    try:
        # Check if the host address is bindable and port is unoccupied
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            return True, ""
    except socket.gaierror:
        return False, t(f"Host address '{host}' is invalid or cannot be resolved.", f"Sunucu adresi '{host}' geçersiz veya çözümlenemiyor.")
    except OSError:
        return False, t(f"Host '{host}' on port {port} is already in use or restricted.", f"Bağlantı noktasındaki '{host}' sunucusu {port} zaten kullanımda veya kısıtlanmış.")
    except Exception as e:
        return False, t(f"Failed to bind to {host}:{port} - {e}", f"{host}:{port} adresine bağlanılamadı - {e}")

# Ensure the project root is in sys.path to enable absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import (
    get_config,
    set_config,
    test_config,
    reset_config,
    get_config_path
)
from src.core.cookies import get_path, get_browser_guide, get_os_name, get_cookies
from src.api.server import start_server

def t(en: str, tr: str) -> str:
    """
    Translation helper function.
    Returns the Turkish text if the configured language is Turkish,
    otherwise returns the English text.
    """
    lang = get_config("gemini", "language")
    return tr if lang == "tr" else en

def clear_terminal() -> None:
    """
    Clears the terminal screen using OS-specific commands.
    """
    os.system("cls" if os.name == "nt" else "clear")

def display_banner() -> None:
    """
    Displays the application ASCII banner and subtitle information.
    Strictly adheres to the no-emoji rule.
    """
    # Use bold standard Cyan (\033[1;36m) which maps to the user's terminal theme and makes the art bold
    theme_color = "\033[1;36m"
    reset = "\033[0m"
    
    border = f"\033[90m==========================================================={reset}"
    banner_lines = [
        "______                                  ___  ______ _____ ",
        "| ___ \\                                / _ \\ | ___ \\_   _|",
        "| |_/ /_ __ _____      _____  ___ _ __/ /_\\ \\| |_/ / | |  ",
        "| ___ \\ '__/ _ \\ \\ /\\ / / __|/ _ \\ '__|  _  ||  __/  | |  ",
        "| |_/ / | | (_) \\ V  V /\\__ \\  __/ |  | | | || |    _| |_ ",
        "\\____/|_|  \\___/ \\_/\\_/ |___/\\___|_|  \\_| |_/\\_|    \\___/ "
    ]
    
    # Author name is formatted as an OSC 8 terminal hyperlink pointing to the GitHub profile
    author_link = f"\033]8;;https://github.com/muhammetozmen\033\\Muhammet OZMEN\033]8;;\033\\"
    
    print(border)
    for line in banner_lines:
        print(f"{theme_color}{line}{reset}")
    print(f"\033[90mversion:1.1                             by {author_link}{reset}")
    print(border)
    
    # Print bold subtitle and gray/thin warning helper text using standard ANSI escape codes
    print(" " + t("\033[1mTurn your web client into FREE API\033[0m", "\033[1mWeb istemcinizi ÜCRETSİZ API'ye dönüştürün\033[0m"))
    print(" " + t("\033[90mFor education purpose only, please buy gemini API from here: https://aistudio.google.com/api-keys\033[0m\n", "\033[90mYalnızca eğitim amaçlıdır, lütfen gemini API'sini buradan satın alın: https://aistudio.google.com/api-keys\033[0m\n"))

def show_legal_disclaimer() -> bool:
    """
    Displays the mandatory Legal Disclaimer and User Consent screen.
    Prompts the user to accept the terms to proceed with initialization.
    
    Returns:
        bool: True if the user accepted the terms, False otherwise.
    """
    clear_terminal()
    display_banner()
    
    # Red disclaimer header to draw user attention
    print("\033[91m" + "-" * 80 + "\033[0m")
    print(" \033[91m[!] " + t("LEGAL DISCLAIMER AND USER CONSENT", "YASAL UYARI VE KULLANICI ONAYI") + "\033[0m")
    print("\033[91m" + "-" * 80 + "\033[0m")
    print(" " + t("This software is designed for educational, research, and personal testing", "Bu yazılım yalnızca eğitim, araştırma ve kişisel test"))
    print(" " + t("purposes only. It extracts session cookies from your local browser to", "amaçları için tasarlanmıştır. Google Gemini ile resmi olmayan"))
    print(" " + t("interact with Google Gemini unofficially.", "şekilde etkileşim kurmak için tarayıcınızdan oturum çerezlerini ayıklar."))
    print()
    print(" " + t("By proceeding, you acknowledge and agree that:", "Devam ederek şunları kabul etmiş ve onaylamış olursunuz:"))
    print(" " + t("1. You are using this tool at your own risk and discretion.", "1. Bu aracı tamamen kendi sorumluluğunuzda ve isteğinizle kullanıyorsunuz."))
    print(" " + t("2. This tool is not affiliated with, authorized, or endorsed by Google.", "2. Bu araç Google ile ilişkili değildir, yetkilendirilmemiştir veya onaylanmamıştır."))
    print(" " + t("3. Using unofficial APIs may violate Google's Terms of Service and could", "3. Resmi olmayan API'lerin kullanılması Google'ın Hizmet Şartlarını ihlal edebilir ve"))
    print(" " + t("   result in the suspension or termination of your Google account.", "   Google hesabınızın askıya alınmasına veya kapatılmasına neden olabilir."))
    print(" " + t("4. The developers assume no liability for any account bans, data loss,", "4. Geliştiriciler, kullanımından doğabilecek hesap engellemeleri, veri kaybı,"))
    print(" " + t("   security vulnerabilities, or other damages arising from its use.", "   güvenlik açıkları veya diğer zararlar için hiçbir sorumluluk kabul etmez."))
    print()
    print(" " + t("Do you explicitly accept these terms and consent to proceed?", "Bu şartları açıkça kabul ediyor ve devam etmeyi onaylıyor musunuz?"))
    print("-" * 80)
    
    try:
        user_input = input(" [?] " + t("Do you accept? (y/n): ", "Kabul ediyor musunuz? (e/h): ")).strip().lower()
        return user_input in ("y", "yes", "e", "evet")
    except (KeyboardInterrupt, EOFError):
        # Handle user interruption gracefully
        print("\n \033[91m[-] " + t("Input interrupted.", "Giriş kesintiye uğradı.") + "\033[0m")
        return False

def select_menu(title: str, options: list[str], default_idx: int = 0) -> int:
    """
    Displays an interactive CLI menu with arrow-key navigation on Linux.
    Falls back to simple numeric input if not on Linux or if input is not a TTY.
    Allows backing out of the menu by pressing 'b' or 'B' (returns -1).
    """
    # Check if standard input is a TTY and if we are on a Unix/Linux system
    is_unix_tty = False
    if sys.platform != "win32":
        try:
            is_unix_tty = sys.stdin.isatty()
        except Exception:
            pass

    if not is_unix_tty:
        # Fallback to simple numeric input (e.g. for piped testing)
        print("-" * 80)
        print(f" {title}")
        print("-" * 80)
        for idx, opt in enumerate(options):
            suffix = t(" (Default)", " (Varsayılan)") if idx == default_idx else ""
            print(f"  {idx + 1}. {opt}{suffix}")
        print("-" * 80)
        while True:
            try:
                choice = input(" [?] " + t(f"Select an option (1-{len(options)} or 'b' to go back): ", f"Bir seçenek seçin (1-{len(options)} veya geri dönmek için 'b'): ")).strip()
                if choice.lower() in ("b", "back"):
                    return -1
                if not choice:
                    # If user just presses ENTER, use the suggested default
                    return default_idx
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(options):
                    return choice_idx
                print(" \033[91m[-]" + t(" Invalid choice. Please try again.", " Geçersiz seçim. Lütfen tekrar deneyin.") + "\033[0m")
            except ValueError:
                print(" \033[91m[-]" + t(" Please enter a valid number.", " Lütfen geçerli bir sayı girin.") + "\033[0m")
            except (KeyboardInterrupt, EOFError):
                print("\n \033[91m[-]" + t(" Menu selection cancelled.", " Menü seçimi iptal edildi.") + "\033[0m")
                sys.exit(1)

    # Unix interactive arrow key selector
    import tty
    import termios

    def get_key() -> str:
        """Reads a single keypress, handling ANSI escape sequences for arrows."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch1 = sys.stdin.read(1)
            if ch1 == "\x1b":  # Start of escape sequence
                ch2 = sys.stdin.read(1)
                if ch2 == "[":
                    ch3 = sys.stdin.read(1)
                    return f"\x1b[{ch3}"
                return "\x1b"
            return ch1
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    # Set initial cursor to default suggestion
    selected_idx = default_idx if 0 <= default_idx < len(options) else 0
    
    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        while True:
            clear_terminal()
            display_banner()
            
            print("-" * 80)
            print(f" {title}")
            print("-" * 80)
            for idx, opt in enumerate(options):
                suffix = t(" (Default)", " (Varsayılan)") if idx == default_idx else ""
                if idx == selected_idx:
                    print(f" \033[1;36m[>]\033[0m \033[1m{opt}{suffix}\033[0m")
                else:
                    print(f"  [ ] {opt}{suffix}")
            print("-" * 80)
            print(" " + t("Use UP/DOWN arrow keys to navigate, ENTER to select, or 'b' to go back.", "Yön tuşlarını kullanarak gezinin, seçmek için ENTER'a veya geri dönmek için 'b'ye basın."))
            print("-" * 80)
            sys.stdout.flush()

            key = get_key()
            if key == "\x1b[A":  # Up arrow
                selected_idx = (selected_idx - 1) % len(options)
            elif key == "\x1b[B":  # Down arrow
                selected_idx = (selected_idx + 1) % len(options)
            elif key in ("\r", "\n"):  # Enter
                break
            elif key in ("b", "B"):  # Go back
                selected_idx = -1
                break
            elif key in ("\x03", "q", "Q"):  # Ctrl+C or 'q'
                raise KeyboardInterrupt
    finally:
        # Show cursor again
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    return selected_idx

def run_setup_wizard() -> None:
    """
    Runs the first-time initialization wizard to configure the settings.
    Allows navigating backward between steps using 'b' or 'back'.
    """
    step = 1
    
    browser_options = [
        "Google Chrome",
        "Mozilla Firefox",
        "Microsoft Edge",
        "Apple Safari",
        "Opera",
        "Brave",
        "Chromium",
        "Vivaldi",
        "LibreWolf",
        "Waterfox"
    ]
    browser_keys = [
        "chrome",
        "firefox",
        "edge",
        "safari",
        "opera",
        "brave",
        "chromium",
        "vivaldi",
        "librewolf",
        "waterfox"
    ]
    
    selected_browser = None
    choice_idx = 0
    
    while True:
        if step == 1:
            clear_terminal()
            print(" [>] " + t("Launching First-Time Initialization Setup Wizard...", "İlk Kurulum Sihirbazı Başlatılıyor..."))
            print()
            
            # Step 1: Select Default Browser
            choice_idx = select_menu(t("FIRST-TIME INITIALIZATION: SELECT DEFAULT BROWSER", "İLK KURULUM: VARSAYILAN TARAYICIYI SEÇİN"), browser_options)
            selected_browser = browser_keys[choice_idx]
            
            # Save browser to config
            set_config("cookies", "default_browser", selected_browser)
            step = 2  # Move to step 2
            
        elif step == 2:
            clear_terminal()
            display_banner()
            print("-" * 80)
            print(" [+] " + t("Configuration updated.", "Yapılandırma güncellendi."))
            print(f" [+] " + t(f"Default Browser set to: \033[1m{browser_options[choice_idx]}\033[0m", f"Varsayılan Tarayıcı şu şekilde ayarlandı: \033[1m{browser_options[choice_idx]}\033[0m"))
            print("-" * 80)
            
            # Step 2: Validate browser path
            print(" [>] " + t("Resolving default cookie database path...", "Varsayılan çerez veri tabanı yolu çözümleniyor..."))
            resolved_path = get_path(selected_browser)
            
            if resolved_path:
                set_config("cookies", "browser_path", str(resolved_path))
                print(f" [+] " + t(f"Automatically detected cookie path: \033[1m{resolved_path}\033[0m", f"Otomatik olarak algılanan çerez yolu: \033[1m{resolved_path}\033[0m"))
                print("-" * 80)
                
                try:
                    user_nav = input(" [?] " + t("Press ENTER to continue, or 'b' to go back: ", "Devam etmek için ENTER'a, geri dönmek için 'b'ye basın: ")).strip().lower()
                    if user_nav in ("b", "back"):
                        # Reset settings and go back to step 1
                        set_config("cookies", "default_browser", None)
                        set_config("cookies", "browser_path", None)
                        step = 1
                        continue
                except (KeyboardInterrupt, EOFError):
                    print("\n \033[91m[-] " + t("Setup interrupted. Exiting.", "Kurulum kesintiye uğradı. Çıkılıyor.") + "\033[0m")
                    sys.exit(1)
                
                step = 3
            else:
                print(f" \033[91m[-] " + t(f"Warning: Could not automatically locate the cookie file for {browser_options[choice_idx]}.", f"Uyarı: {browser_options[choice_idx]} için çerez dosyası otomatik olarak bulunamadı.") + "\033[0m")
                print()
                print(" \033[1m" + t("Step-by-Step Guide to Locate it:", "Konumu Bulmak İçin Adım Adım Kılavuz:") + "\033[0m")
                os_name = get_os_name()
                guide = get_browser_guide(selected_browser, os_name)
                print(f"  {guide}")
                print()
                
                back_to_menu = False
                while True:
                    try:
                        manual_input = input(" [?] " + t("Please enter the absolute path to the cookie file (or 'b' to go back): ", "Lütfen çerez dosyasının mutlak yolunu girin (veya geri dönmek için 'b' yazın): ")).strip()
                        if not manual_input:
                            print(" \033[91m[-] " + t("Path cannot be empty. Please try again.", "Yol boş olamaz. Lütfen tekrar deneyin.") + "\033[0m")
                            continue
                        
                        if manual_input.lower() in ("b", "back"):
                            # Reset browser selection and mark flag to loop back
                            set_config("cookies", "default_browser", None)
                            step = 1
                            back_to_menu = True
                            break
                        
                        path_candidate = Path(os.path.expanduser(manual_input)).resolve()
                        if path_candidate.exists() and path_candidate.is_file():
                            set_config("cookies", "browser_path", str(path_candidate))
                            print(f" [+] " + t(f"Saved manual cookie path: \033[1m{path_candidate}\033[0m", f"Manuel çerez yolu kaydedildi: \033[1m{path_candidate}\033[0m"))
                            step = 3
                            break
                        else:
                            print(f" \033[91m[-] " + t(f"Invalid path: '{manual_input}' does not exist or is not a file.", f"Geçersiz yol: '{manual_input}' mevcut değil veya bir dosya değil.") + "\033[0m")
                            print("     " + t("Please verify the path and try again.", "Lütfen yolu doğrulayın ve tekrar deneyin."))
                    except (KeyboardInterrupt, EOFError):
                        print("\n \033[91m[-] " + t("Setup interrupted. Exiting.", "Kurulum kesintiye uğradı. Çıkılıyor.") + "\033[0m")
                        sys.exit(1)
                
                if back_to_menu:
                    continue
                    
        elif step == 3:
            clear_terminal()
            display_banner()
            print("-" * 80)
            print(" " + t("FIRST-TIME INITIALIZATION: CONFIGURE SERVER SETTINGS", "İLK KURULUM: SUNUCU AYARLARINI YAPILANDIRIN"))
            print("-" * 80)
            print(" " + t("Configure the local API server host and port.", "Yerel API sunucusu ana bilgisayarını ve bağlantı noktasını yapılandırın."))
            print(" " + t("Press ENTER to accept the default suggestions, or type 'b' to go back.", "Varsayılan önerileri kabul etmek için ENTER'a basın veya geri gitmek için 'b' yazın."))
            print("-" * 80)
            
            # Suggest defaults
            default_host = "127.0.0.1"
            default_port = 4747
            
            try:
                # 1. Host selection
                host_input = input(f" [?] " + t(f"Enter host address [{default_host}]: ", f"Sunucu adresini girin [{default_host}]: ")).strip()
                if host_input.lower() in ("b", "back"):
                    # Reset the saved cookie path/browser to force full Step 2 re-evaluation
                    set_config("cookies", "browser_path", None)
                    step = 2
                    continue
                host = host_input if host_input else default_host
                
                # 2. Port selection
                port_input = input(f" [?] " + t(f"Enter port number [{default_port}]: ", f"Bağlantı noktası numarasını girin [{default_port}]: ")).strip()
                if port_input.lower() in ("b", "back"):
                    set_config("cookies", "browser_path", None)
                    step = 2
                    continue
                
                try:
                    port = int(port_input) if port_input else default_port
                except ValueError:
                    print(f" \033[91m[-] " + t("Error: Port must be an integer. Try again.", "Hata: Bağlantı noktası bir tam sayı olmalıdır. Tekrar deneyin.") + "\033[0m")
                    input(" " + t("Press ENTER to retry...", "Yeniden denemek için ENTER'a basın..."))
                    continue
                    
                # Validate host & port combination
                is_valid, err_msg = validate_server_settings(host, port)
                if not is_valid:
                    print(f" \033[91m[-] " + t(f"Error: {err_msg}", f"Hata: {err_msg}") + "\033[0m")
                    input(" " + t("Press ENTER to retry...", "Yeniden denemek için ENTER'a basın..."))
                    continue
                
                # Save to config
                set_config("server", "host", host)
                set_config("server", "port", port)
                
                print("-" * 80)
                print(" [+] " + t("Configuration updated.", "Yapılandırma güncellendi."))
                print(f" [+] " + t(f"Server configured at: \033[1mhttp://{host}:{port}\033[0m", f"Sunucu şu adreste yapılandırıldı: \033[1mhttp://{host}:{port}\033[0m"))
                print("-" * 80)
                
                step = 4  # Move to model selection step
                
            except (KeyboardInterrupt, EOFError):
                print("\n \033[91m[-] " + t("Setup interrupted. Exiting.", "Kurulum kesintiye uğradı. Çıkılıyor.") + "\033[0m")
                sys.exit(1)
                
        elif step == 4:
            # Step 4: Select Gemini Models (Weak -> Default -> Strong)
            model_options = [
                t("gemini-2.0-flash-lite (Faster, lightweight)", "gemini-2.0-flash-lite (Daha hızlı, hafif)"),
                t("gemini-2.0-flash (Balanced performance)", "gemini-2.0-flash (Dengeli performans)"),
                t("gemini-1.5-pro (High intelligence, complex tasks)", "gemini-1.5-pro (Yüksek zeka, karmaşık görevler)")
            ]
            model_keys = ["flash-lite", "flash", "pro"]
            
            sub_step = 1
            weak_model = "flash-lite"
            default_model = "flash"
            strong_model = "pro"
            
            while sub_step in (1, 2, 3):
                if sub_step == 1:
                    # Select Weak Model (suggest flash-lite, idx=0)
                    choice_weak = select_menu(t("FIRST-TIME INITIALIZATION: SELECT WEAK MODEL (AUTOCOMPLETE)", "İLK KURULUM: ZAYIF MODELİ SEÇİN (OTOMATİK TAMAMLAMA)"), model_options, default_idx=0)
                    if choice_weak == -1:
                        sub_step = 0
                        step = 3
                        break
                    weak_model = model_keys[choice_weak]
                    sub_step = 2
                    
                elif sub_step == 2:
                    # Select Default Model (suggest flash, idx=1)
                    choice_default = select_menu(t("FIRST-TIME INITIALIZATION: SELECT DEFAULT MODEL", "İLK KURULUM: VARSAYILAN MODELİ SEÇİN"), model_options, default_idx=1)
                    if choice_default == -1:
                        sub_step = 1
                        continue
                    default_model = model_keys[choice_default]
                    sub_step = 3
                    
                elif sub_step == 3:
                    # Select Strong Model (suggest pro, idx=2)
                    choice_strong = select_menu(t("FIRST-TIME INITIALIZATION: SELECT STRONG MODEL", "İLK KURULUM: GÜÇLÜ MODELİ SEÇİN"), model_options, default_idx=2)
                    if choice_strong == -1:
                        sub_step = 2
                        continue
                    strong_model = model_keys[choice_strong]
                    sub_step = 4  # Done with Step 4
            
            if step == 3:
                continue
                
            # Save models to config
            set_config("gemini", "default_model", default_model)
            set_config("gemini", "strong_model", strong_model)
            set_config("gemini", "weak_model", weak_model)
            
            clear_terminal()
            display_banner()
            print("-" * 80)
            print(" [+] " + t("Configuration updated.", "Yapılandırma güncellendi."))
            print(f" [+] " + t(f"Weak Gemini Model:    \033[1m{weak_model}\033[0m", f"Zayıf Gemini Modeli:    \033[1m{weak_model}\033[0m"))
            print(f" [+] " + t(f"Default Gemini Model: \033[1m{default_model}\033[0m", f"Varsayılan Gemini Modeli: \033[1m{default_model}\033[0m"))
            print(f" [+] " + t(f"Strong Gemini Model:  \033[1m{strong_model}\033[0m", f"Güçlü Gemini Modeli:  \033[1m{strong_model}\033[0m"))
            print("-" * 80)
            
            step = 6  # Move to meta parameters step
            
        elif step == 6:
            clear_terminal()
            display_banner()
            print("-" * 80)
            print(" " + t("FIRST-TIME INITIALIZATION: CONFIGURE META SETTINGS", "İLK KURULUM: META AYARLARINI YAPILANDIRIN"))
            print("-" * 80)
            print(" " + t("Configure system limits and background synchronization intervals.", "Sistem sınırlarını ve arka plan senkronizasyon aralıklarını yapılandırın."))
            print(" " + t("Press ENTER to accept the default suggestions, or type 'b' to go back.", "Varsayılan önerileri kabul etmek için ENTER'a basın veya geri gitmek için 'b' yazın."))
            print("-" * 80)
            
            # Suggest defaults
            default_max_files = 20
            default_cookie_update = 600
            
            try:
                # 1. Max Files selection
                max_files_input = input(f" [?] " + t(f"Enter max log files to retain [{default_max_files}]: ", f"Saklanacak maksimum günlük dosyası sayısını girin [{default_max_files}]: ")).strip()
                if max_files_input.lower() in ("b", "back"):
                    step = 4
                    continue
                
                try:
                    max_files = int(max_files_input) if max_files_input else default_max_files
                    if max_files <= 0:
                        raise ValueError
                except ValueError:
                    print(f" \033[91m[-] " + t("Error: Max log files must be a positive integer. Try again.", "Hata: Maksimum günlük dosyası pozitif bir tam sayı olmalıdır. Tekrar deneyin.") + "\033[0m")
                    input(" " + t("Press ENTER to retry...", "Yeniden denemek için ENTER'a basın..."))
                    continue
                    
                # 2. Cookie update selection
                cookie_update_input = input(f" [?] " + t(f"Enter cookie refresh interval in seconds [{default_cookie_update}]: ", f"Saniye cinsinden çerez yenileme sıklığını girin [{default_cookie_update}]: ")).strip()
                if cookie_update_input.lower() in ("b", "back"):
                    step = 4
                    continue
                    
                try:
                    cookie_update = int(cookie_update_input) if cookie_update_input else default_cookie_update
                    if cookie_update <= 0:
                        raise ValueError
                except ValueError:
                    print(f" \033[91m[-] " + t("Error: Refresh interval must be a positive integer. Try again.", "Hata: Yenileme sıklığı pozitif bir tam sayı olmalıdır. Tekrar deneyin.") + "\033[0m")
                    input(" " + t("Press ENTER to retry...", "Yeniden denemek için ENTER'a basın..."))
                    continue
                
                # Save meta configurations to config
                set_config("meta", "max_files", max_files)
                set_config("meta", "cookie_update", cookie_update)
                
                clear_terminal()
                display_banner()
                print("=" * 80)
                print(" \033[92m[+] " + t("INITIALIZATION SUCCESSFUL!", "KURULUM BAŞARILI!") + "\033[0m")
                print("=" * 80)
                print(" " + t("Your local API server configuration has been successfully saved.", "Yerel API sunucusu yapılandırmanız başarıyla kaydedildi."))
                print(" " + t("The application will now launch the Main Menu.", "Uygulama şimdi Ana Menüyü başlatacak."))
                print("=" * 80)
                input(" " + t("Press ENTER to continue...", "Devam etmek için ENTER'a basın..."))
                break
                
            except (KeyboardInterrupt, EOFError):
                print("\n \033[91m[-] " + t("Setup interrupted. Exiting.", "Kurulum kesintiye uğradı. Çıkılıyor.") + "\033[0m")
                sys.exit(1)
def manage_settings() -> None:
    """
    Interactive configuration editor menu.
    Allows changing configuration parameters via direct user inputs.
    """
    while True:
        clear_terminal()
        display_banner()
        print("=" * 80)
        print(" " + t("CONFIGURATION SETTINGS EDITOR", "YAPILANDIRMA AYARLARI EDİTÖRÜ"))
        print("=" * 80)
        
        # Load current configurations
        browser = get_config("cookies", "default_browser") or "None"
        path = get_config("cookies", "browser_path") or "None"
        host = get_config("server", "host") or "127.0.0.1"
        port = get_config("server", "port") or 4747
        lang = get_config("gemini", "language") or "en"
        def_model = get_config("gemini", "default_model") or "flash"
        str_model = get_config("gemini", "strong_model") or "pro"
        weak_model = get_config("gemini", "weak_model") or "flash-lite"
        max_files = get_config("meta", "max_files") or 20
        cookie_update = get_config("meta", "cookie_update") or 600
        
        settings_options = [
            f"{t('Default Browser', 'Varsayılan Tarayıcı')}: {browser}",
            f"{t('Browser Cookie Path', 'Tarayıcı Çerez Yolu')}: {path}",
            f"{t('Server Host', 'Sunucu Adresi')}: {host}",
            f"{t('Server Port', 'Sunucu Portu')}: {port}",
            f"{t('Gemini Language', 'Gemini Dili')}: {lang}",
            t(f"Gemini Models (Default: {def_model}, Strong: {str_model}, Weak: {weak_model})", f"Gemini Modelleri (Varsayılan: {def_model}, Güçlü: {str_model}, Zayıf: {weak_model})"),
            t(f"Meta Settings (Max Files: {max_files}, Sync Interval: {cookie_update}s)", f"Meta Ayarlar (Maks Dosya: {max_files}, Senkronizasyon Sıklığı: {cookie_update}s)"),
            t("Back to Main Menu", "Ana Menüye Dön")
        ]
        
        choice = select_menu(t("SETTINGS MANAGER - CHOOSE SETTING TO EDIT", "AYAR YÖNETİCİSİ - DÜZENLENECEK AYARI SEÇİN"), settings_options)
        if choice == -1 or choice == 7: # Back
            break
            
        try:
            if choice == 0:  # Edit Default Browser
                browser_options = ["chrome", "firefox", "edge", "safari", "opera", "brave", "chromium", "vivaldi", "librewolf", "waterfox"]
                print("\n " + t("Select default browser:", "Varsayılan tarayıcıyı seçin:"))
                for idx, b in enumerate(browser_options, 1):
                    print(f"  {idx}) {b}")
                sel_idx = input(f" [?] " + t(f"Enter selection [current: {browser}]: ", f"Seçiminizi girin [mevcut: {browser}]: ")).strip()
                if sel_idx:
                    try:
                        new_b = browser_options[int(sel_idx) - 1]
                        set_config("cookies", "default_browser", new_b)
                        # Suggest and set cookie path if possible
                        auto_path = get_path(new_b)
                        if auto_path:
                            set_config("cookies", "browser_path", str(auto_path))
                        print(f" [+] " + t(f"Browser changed to: {new_b}", f"Tarayıcı şu şekilde değiştirildi: {new_b}"))
                    except (ValueError, IndexError):
                        print(" [-] " + t("Invalid selection.", "Geçersiz seçim."))
                input("\n " + t("Press ENTER to continue...", "Devam etmek için ENTER'a basın..."))
                
            elif choice == 1:  # Edit Cookie Path
                print(f"\n " + t(f"Current cookie path: {path}", f"Mevcut çerez yolu: {path}"))
                new_path = input(" [?] " + t("Enter new absolute cookie path (or press ENTER to cancel): ", "Yeni mutlak çerez yolunu girin (veya iptal etmek için ENTER'a basın): ")).strip()
                if new_path:
                    p = Path(os.path.expanduser(new_path)).resolve()
                    if p.exists() and p.is_file():
                        set_config("cookies", "browser_path", str(p))
                        print(f" [+] " + t(f"Saved new cookie path: {p}", f"Yeni çerez yolu kaydedildi: {p}"))
                    else:
                        print(" [-] " + t("File does not exist or is not a valid file path.", "Dosya mevcut değil veya geçerli bir dosya yolu değil."))
                input("\n " + t("Press ENTER to continue...", "Devam etmek için ENTER'a basın..."))
                
            elif choice == 2:  # Edit Host
                print(f"\n " + t(f"Current host: {host}", f"Mevcut adres: {host}"))
                new_host = input(f" [?] " + t(f"Enter new host address [{host}]: ", f"Yeni sunucu adresini girin [{host}]: ")).strip()
                if new_host:
                    # Validate port with current port
                    is_valid, err = validate_server_settings(new_host, port)
                    if is_valid:
                        set_config("server", "host", new_host)
                        print(f" [+] " + t(f"Server host updated to: {new_host}", f"Sunucu adresi güncellendi: {new_host}"))
                    else:
                        print(f" [-] " + t(f"Error: {err}", f"Hata: {err}"))
                input("\n " + t("Press ENTER to continue...", "Devam etmek için ENTER'a basın..."))
                
            elif choice == 3:  # Edit Port
                print(f"\n " + t(f"Current port: {port}", f"Mevcut port: {port}"))
                new_port_str = input(f" [?] " + t(f"Enter new port number [{port}]: ", f"Yeni port numarasını girin [{port}]: ")).strip()
                if new_port_str:
                    try:
                        new_port = int(new_port_str)
                        is_valid, err = validate_server_settings(host, new_port)
                        if is_valid:
                            set_config("server", "port", new_port)
                            print(f" [+] " + t(f"Server port updated to: {new_port}", f"Sunucu portu güncellendi: {new_port}"))
                        else:
                            print(f" [-] " + t(f"Error: {err}", f"Hata: {err}"))
                    except ValueError:
                        print(" [-] " + t("Port must be a valid integer.", "Port geçerli bir tam sayı olmalıdır."))
                input("\n " + t("Press ENTER to continue...", "Devam etmek için ENTER'a basın..."))
                
            elif choice == 4:  # Edit Language
                lang_options = ["en", "tr"]
                print(f"\n " + t(f"Current language: {lang}", f"Mevcut dil: {lang}"))
                print("  1) English")
                print("  2) Türkçe (Turkish)")
                lang_sel = input(" [?] " + t("Select language [1-2]: ", "Dil seçin [1-2]: ")).strip()
                if lang_sel in ("1", "2"):
                    new_lang = lang_options[int(lang_sel) - 1]
                    set_config("gemini", "language", new_lang)
                    print(f" [+] " + t(f"Language updated to: {new_lang}", f"Dil güncellendi: {new_lang}"))
                else:
                    print(" [-] " + t("Invalid selection.", "Geçersiz seçim."))
                input("\n " + t("Press ENTER to continue...", "Devam etmek için ENTER'a basın..."))
                
            elif choice == 5:  # Edit Gemini Models
                model_options = ["flash-lite", "flash", "pro"]
                print("\n " + t("Select default model:", "Varsayılan modeli seçin:"))
                for idx, m in enumerate(model_options, 1):
                    print(f"  {idx}) {m}")
                def_sel = input(f" [?] " + t(f"Select default model [current: {def_model}]: ", f"Varsayılan modeli seçin [mevcut: {def_model}]: ")).strip()
                if def_sel:
                    try:
                        set_config("gemini", "default_model", model_options[int(def_sel) - 1])
                    except (ValueError, IndexError):
                        print(" [-] " + t("Invalid selection.", "Geçersiz seçim."))
                        
                str_sel = input(f" [?] " + t(f"Select strong model [current: {str_model}]: ", f"Güçlü modeli seçin [mevcut: {str_model}]: ")).strip()
                if str_sel:
                    try:
                        set_config("gemini", "strong_model", model_options[int(str_sel) - 1])
                    except (ValueError, IndexError):
                        print(" [-] " + t("Invalid selection.", "Geçersiz seçim."))
                        
                weak_sel = input(f" [?] " + t(f"Select weak model [current: {weak_model}]: ", f"Zayıf modeli seçin [mevcut: {weak_model}]: ")).strip()
                if weak_sel:
                    try:
                        set_config("gemini", "weak_model", model_options[int(weak_sel) - 1])
                    except (ValueError, IndexError):
                        print(" [-] " + t("Invalid selection.", "Geçersiz seçim."))
                print(" [+] " + t("Gemini models updated.", "Gemini modelleri güncellendi."))
                input("\n " + t("Press ENTER to continue...", "Devam etmek için ENTER'a basın..."))
                
            elif choice == 6:  # Edit Meta Settings
                print(f"\n " + t(f"Current max files: {max_files}", f"Mevcut maksimum dosya sayısı: {max_files}"))
                new_max = input(f" [?] " + t(f"Enter max files to retain [{max_files}]: ", f"Saklanacak maksimum dosya sayısını girin [{max_files}]: ")).strip()
                if new_max:
                    try:
                        new_max_int = int(new_max)
                        if new_max_int > 0:
                            set_config("meta", "max_files", new_max_int)
                            print(f" [+] " + t(f"Max files updated to: {new_max_int}", f"Maksimum dosya sayısı güncellendi: {new_max_int}"))
                        else:
                            print(" [-] " + t("Max files must be positive.", "Maksimum dosya sayısı pozitif olmalıdır."))
                    except ValueError:
                        print(" [-] " + t("Invalid selection.", "Geçersiz seçim."))
                        
                print(f"\n " + t(f"Current sync interval: {cookie_update}s", f"Mevcut senkronizasyon sıklığı: {cookie_update}s"))
                new_update = input(f" [?] " + t(f"Enter cookie update interval in seconds [{cookie_update}]: ", f"Saniye cinsinden çerez güncelleme sıklığını girin [{cookie_update}]: ")).strip()
                if new_update:
                    try:
                        new_update_int = int(new_update)
                        if new_update_int > 0:
                            set_config("meta", "cookie_update", new_update_int)
                            print(f" [+] " + t(f"Sync interval updated to: {new_update_int}s", f"Senkronizasyon sıklığı güncellendi: {new_update_int}s"))
                        else:
                            print(" [-] " + t("Interval must be positive.", "Süre pozitif olmalıdır."))
                    except ValueError:
                        print(" [-] " + t("Invalid selection.", "Geçersiz seçim."))
                input("\n " + t("Press ENTER to continue...", "Devam etmek için ENTER'a basın..."))
                
        except (KeyboardInterrupt, EOFError):
            print("\n [-] " + t("Cancelled.", "İptal edildi."))
            input("\n " + t("Press ENTER to continue...", "Devam etmek için ENTER'a basın..."))

def main() -> None:
    """
    Application main execution thread.
    Checks config status and routes to wizard or main server menu.
    """
    config_path = get_config_path()
    
    # Determine if this is the first launch (no config file exists yet)
    is_first_launch = not config_path.exists()
    
    # Ensure language is selected at the very beginning of the application
    lang = get_config("gemini", "language")
    if lang not in ("en", "tr"):
        clear_terminal()
        display_banner()
        print("=" * 80)
        print(" SELECT APPLICATION LANGUAGE / UYGULAMA DİLİNİ SEÇİN")
        print("=" * 80)
        print("  1) English")
        print("  2) Türkçe (Turkish)")
        print("=" * 80)
        while True:
            try:
                choice = input(" [?] Select language / Dili seçin [1-2]: ").strip()
                if choice == "1":
                    set_config("gemini", "language", "en")
                    break
                elif choice == "2":
                    set_config("gemini", "language", "tr")
                    break
                else:
                    print(" \033[91m[-] Invalid choice / Geçersiz seçim.\033[0m")
            except (KeyboardInterrupt, EOFError):
                print("\n \033[91m[-] Interrupted / İptal edildi.\033[0m")
                sys.exit(1)

    # Check if this is the first launch, show disclaimer in selected language
    if is_first_launch:
        consent_granted = show_legal_disclaimer()
        if not consent_granted:
            print(" \033[91m[-] " + t("Consent declined or invalid input. The application will now terminate.", "Onay reddedildi veya geçersiz giriş. Uygulama şimdi sonlandırılacak.") + "\033[0m")
            # Remove config file so next startup is also treated as first launch
            if config_path.exists():
                try:
                    config_path.unlink()
                except Exception:
                    pass
            sys.exit(1)
            
        print(" [+] " + t("Consent accepted.", "Onay kabul edildi."))
        run_setup_wizard()
        main()
        return

    # If config exists, validate it
    if not test_config():
        clear_terminal()
        display_banner()
        print(" \033[91m[-] " + t("Warning: Existing config.json is corrupted or invalid.", "Uyarı: Mevcut config.json bozuk veya geçersiz.") + "\033[0m")
        try:
            reset_choice = input(" [?] " + t("Reset to factory default configuration? (y/n): ", "Fabrika ayarlarına sıfırlansın mı? (e/h): ")).strip().lower()
            if reset_choice in ("y", "yes", "e", "evet"):
                reset_config()
                print(" [+] " + t("Configuration reset successfully.", "Yapılandırma başarıyla sıfırlandı."))
                main()
                return
            else:
                print(" \033[91m[-] " + t("Cannot proceed with invalid configuration. Terminating.", "Geçersiz yapılandırma ile devam edilemiyor. Sonlandırılıyor.") + "\033[0m")
                sys.exit(1)
        except (KeyboardInterrupt, EOFError):
            print("\n \033[91m[-] " + t("Cancelled. Terminating.", "İptal edildi. Sonlandırılıyor.") + "\033[0m")
            sys.exit(1)

    # Config is valid: check if default browser is selected
    default_browser = get_config("cookies", "default_browser")
    if default_browser is None:
        # User accepted disclaimer but did not finish setup wizard
        run_setup_wizard()
        main()
        return

    # Setup is complete: bypass disclaimer/wizard and display Main Menu
    menu_options = [
        t("Start Local API Server", "Yerel API Sunucusunu Başlat"),
        t("Update/Sync Cookies Manually", "Çerezleri Elle Güncelle/Eşitle"),
        t("Configuration Settings", "Yapılandırma Ayarları"),
        t("Run Diagnostics & System Test", "Teşhis ve Sistem Testini Çalıştır"),
        t("Reset Factory Defaults", "Fabrika Ayarlarına Sıfırla"),
        t("Exit", "Çıkış")
    ]
    
    while True:
        try:
            choice_idx = select_menu(t("MAIN MENU", "ANA MENÜ"), menu_options)
            
            if choice_idx == 0:  # Start Server
                start_server()
                break
            elif choice_idx == 1:  # Update Cookies
                print("\n [>] " + t("Syncing browser cookies manually...", "Tarayıcı çerezleri elle eşitleniyor..."))
                cookies = get_cookies()
                if cookies:
                    print(" \033[92m[+] " + t("Cookies synchronized successfully.", "Çerezler başarıyla eşitlendi.") + "\033[0m")
                else:
                    print(" \033[91m[-] " + t("Cookie synchronization failed.", "Çerez eşitleme başarısız oldu.") + "\033[0m")
                input("\n " + t("Press ENTER to return to menu...", "Menüye dönmek için ENTER'a basın..."))
            elif choice_idx == 2:  # Config Settings
                manage_settings()
            elif choice_idx == 3:  # Diagnostics
                print("\n [>] " + t("Running diagnostics and system verification...", "Teşhis ve sistem doğrulaması çalıştırılıyor..."))
                import asyncio
                from src.services.gemini_io import verify_session
                is_healthy = asyncio.run(verify_session())
                print("-" * 80)
                if is_healthy:
                    print(" \033[92m[+] " + t("System status: HEALTHY (Gemini session active)", "Sistem durumu: SAĞLIKLI (Gemini oturumu aktif)") + "\033[0m")
                else:
                    print(" \033[91m[-] " + t("System status: UNHEALTHY (Gemini session disconnected)", "Sistem durumu: SAĞLIKSIZ (Gemini oturumu bağlantısı kesildi)") + "\033[0m")
                print("-" * 80)
                input("\n " + t("Press ENTER to return to menu...", "Menüye dönmek için ENTER'a basın..."))
            elif choice_idx == 4:  # Reset defaults
                reset_config()
                print("\n [+] " + t("Configuration reset to factory defaults.", "Yapılandırma fabrika ayarlarına sıfırlandı."))
                print(" [>] " + t("Restarting application to trigger setup wizard...", "Kurulum sihirbazını tetiklemek için uygulama yeniden başlatılıyor..."))
                main()
                break
            elif choice_idx == 5:  # Exit
                print("\n [>] " + t("Goodbye!", "Görüşmek üzere!"))
                break
        except KeyboardInterrupt:
            print("\n \033[91m[-] " + t("Exiting.", "Çıkış yapılıyor.") + "\033[0m")
            break

if __name__ == "__main__":
    main()
