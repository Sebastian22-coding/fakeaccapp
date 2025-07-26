"""
Hilfsfunktionen für den FakeAccountScanner
"""

import os
import re
from pathlib import Path
from typing import List
import unicodedata


def setup_output_directory() -> Path:
    """Erstelle und gib das Output-Verzeichnis zurück"""
    # Bestimme Home-Verzeichnis
    home_dir = Path.home()
    
    # Erstelle fake_account_reports Ordner
    output_dir = home_dir / "fake_account_reports"
    
    # Erstelle Verzeichnis falls es nicht existiert
    output_dir.mkdir(exist_ok=True)
    
    return output_dir


def validate_usernames(usernames_text: str) -> List[str]:
    """Validiere und bereinige Benutzernamen"""
    if not usernames_text.strip():
        return []
    
    # Teile nach Kommas und bereinige
    usernames = []
    raw_names = usernames_text.split(',')
    
    for name in raw_names:
        cleaned_name = clean_username(name.strip())
        if cleaned_name and is_valid_username(cleaned_name):
            usernames.append(cleaned_name)
    
    # Entferne Duplikate und behalte Reihenfolge bei
    seen = set()
    unique_usernames = []
    for username in usernames:
        if username.lower() not in seen:
            seen.add(username.lower())
            unique_usernames.append(username)
    
    return unique_usernames


def clean_username(username: str) -> str:
    """Bereinige einen einzelnen Benutzernamen"""
    if not username:
        return ""
    
    # Entferne Whitespace
    username = username.strip()
    
    # Entferne @ am Anfang falls vorhanden
    if username.startswith('@'):
        username = username[1:]
    
    # Entferne URLs/Domains falls jemand vollständige URLs eingegeben hat
    url_patterns = [
        r'https?://(?:www\.)?instagram\.com/',
        r'https?://(?:www\.)?tiktok\.com/@?',
        r'https?://(?:www\.)?x\.com/',
        r'https?://(?:www\.)?twitter\.com/',
        r'instagram\.com/',
        r'tiktok\.com/@?',
        r'x\.com/',
        r'twitter\.com/'
    ]
    
    for pattern in url_patterns:
        username = re.sub(pattern, '', username, flags=re.IGNORECASE)
    
    # Entferne trailing slashes
    username = username.rstrip('/')
    
    # Normalisiere Unicode-Zeichen
    username = unicodedata.normalize('NFKC', username)
    
    return username


def is_valid_username(username: str) -> bool:
    """Überprüfe ob ein Benutzername gültig ist"""
    if not username:
        return False
    
    # Länge prüfen (die meisten Plattformen haben Limits)
    if len(username) < 1 or len(username) > 30:
        return False
    
    # Grundlegende Zeichen-Validierung
    # Erlaube Buchstaben, Zahlen, Unterstriche, Punkte und Bindestriche
    if not re.match(r'^[a-zA-Z0-9._-]+$', username):
        return False
    
    # Kann nicht nur aus Punkten oder Unterstrichen bestehen
    if re.match(r'^[._-]+$', username):
        return False
    
    # Kann nicht mit Punkt oder Bindestrich beginnen/enden
    if username.startswith('.') or username.endswith('.'):
        return False
    if username.startswith('-') or username.endswith('-'):
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """Bereinige einen Dateinamen für das Dateisystem"""
    # Ersetze problematische Zeichen
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Entferne aufeinanderfolgende Unterstriche
    filename = re.sub(r'_+', '_', filename)
    
    # Trimme Unterstriche am Anfang/Ende
    filename = filename.strip('_')
    
    return filename


def format_file_size(size_bytes: int) -> str:
    """Formatiere Dateigröße in lesbarer Form"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_app_version() -> str:
    """Gib die App-Version zurück"""
    return "1.0.0"


def create_app_info() -> dict:
    """Erstelle App-Informationen für Reports"""
    return {
        "app_name": "FakeAccountScanner",
        "version": get_app_version(),
        "platform": "macOS",
        "author": "FakeAccountScanner Team"
    }