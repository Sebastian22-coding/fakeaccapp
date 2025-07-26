#!/usr/bin/env python3
"""
Entwicklungs-Startskript für FakeAccountScanner
Startet die App mit zusätzlichen Debug-Optionen
"""

import os
import sys
import argparse
from pathlib import Path

def setup_environment():
    """Setup für Entwicklungsumgebung"""
    # Füge aktuelles Verzeichnis zu Python-Path hinzu
    current_dir = Path(__file__).parent.absolute()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Debug-Umgebungsvariablen
    os.environ['PYTHONPATH'] = str(current_dir)
    os.environ['FAKEACCOUNTSCANNER_DEBUG'] = '1'


def check_dependencies():
    """Überprüfe ob alle Abhängigkeiten installiert sind"""
    missing_deps = []
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append('tkinter')
    
    try:
        import playwright
    except ImportError:
        missing_deps.append('playwright')
    
    if missing_deps:
        print(f"❌ Fehlende Abhängigkeiten: {', '.join(missing_deps)}")
        print("Führe 'pip install -r requirements.txt' aus")
        return False
    
    return True


def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(description='FakeAccountScanner Entwicklungsversion')
    parser.add_argument('--debug', action='store_true', 
                       help='Aktiviere Debug-Modus')
    parser.add_argument('--playwright-debug', action='store_true',
                       help='Aktiviere Playwright Debug-Modus (zeigt Browser)')
    parser.add_argument('--test-mode', action='store_true',
                       help='Starte im Test-Modus mit Mock-Daten')
    parser.add_argument('--profile', action='store_true',
                       help='Aktiviere Performance-Profiling')
    
    args = parser.parse_args()
    
    print("🚀 FakeAccountScanner Entwicklungsversion")
    print("=" * 40)
    
    # Setup
    setup_environment()
    
    # Überprüfe Abhängigkeiten
    if not check_dependencies():
        return 1
    
    # Debug-Einstellungen
    if args.debug:
        os.environ['FAKEACCOUNTSCANNER_LOG_LEVEL'] = 'DEBUG'
        print("🐛 Debug-Modus aktiviert")
    
    if args.playwright_debug:
        os.environ['PWDEBUG'] = '1'
        print("🌐 Playwright Debug-Modus aktiviert (Browser wird sichtbar)")
    
    if args.test_mode:
        os.environ['FAKEACCOUNTSCANNER_TEST_MODE'] = '1'
        print("🧪 Test-Modus aktiviert")
    
    if args.profile:
        os.environ['FAKEACCOUNTSCANNER_PROFILE'] = '1'
        print("⏱️  Performance-Profiling aktiviert")
    
    print(f"📁 Arbeitsverzeichnis: {os.getcwd()}")
    print(f"🐍 Python: {sys.version}")
    print()
    
    try:
        # Importiere und starte Hauptanwendung
        from main import main as app_main
        
        print("▶️  Starte FakeAccountScanner...")
        app_main()
        
    except KeyboardInterrupt:
        print("\n⚠️  Anwendung beendet durch Benutzer")
        return 0
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        print("Stelle sicher, dass alle Module im richtigen Verzeichnis sind")
        return 1
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())