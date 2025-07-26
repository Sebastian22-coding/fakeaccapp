#!/bin/bash

# FakeAccountScanner Build-Skript für macOS
# Einfaches Shell-Skript zum Bauen der App

set -e  # Exit bei Fehlern

echo "🚀 FakeAccountScanner Build-Skript"
echo "=================================="

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktionen
print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Überprüfe Betriebssystem
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_warning "Dieses Skript ist für macOS optimiert"
fi

# Überprüfe Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 ist nicht installiert"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_step "Python Version: $PYTHON_VERSION"

# Überprüfe pip
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 ist nicht installiert"
    exit 1
fi

# Arbeitsverzeichnis
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

print_step "Arbeitsverzeichnis: $PWD"

# Bereinige vorherige Builds
print_step "Bereinige vorherige Builds..."
rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/
rm -f *.spec *.dmg
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
print_success "Bereinigung abgeschlossen"

# Installiere Abhängigkeiten
print_step "Installiere Python-Abhängigkeiten..."
pip3 install -r requirements.txt

# Installiere PyInstaller falls nicht vorhanden
if ! pip3 show pyinstaller &> /dev/null; then
    print_step "Installiere PyInstaller..."
    pip3 install pyinstaller
fi

# Installiere Playwright Browser
print_step "Installiere Playwright Browser..."
python3 -m playwright install chromium
print_success "Abhängigkeiten installiert"

# Erstelle App
print_step "Baue macOS App..."
python3 build_spec.py

# Überprüfe Ergebnis
if [ -d "dist/FakeAccountScanner.app" ]; then
    print_success "App erfolgreich erstellt!"
    
    # Zeige App-Größe
    APP_SIZE=$(du -sh "dist/FakeAccountScanner.app" | cut -f1)
    echo "📦 App-Größe: $APP_SIZE"
    
    # Erstelle DMG (optional)
    if command -v hdiutil &> /dev/null; then
        print_step "Erstelle DMG-Image..."
        DMG_NAME="FakeAccountScanner-1.0.0"
        
        if [ -f "$DMG_NAME.dmg" ]; then
            rm "$DMG_NAME.dmg"
        fi
        
        hdiutil create -volname "FakeAccountScanner" \
            -srcfolder "dist/FakeAccountScanner.app" \
            -ov -format UDZO \
            "$DMG_NAME.dmg" > /dev/null 2>&1
        
        if [ -f "$DMG_NAME.dmg" ]; then
            DMG_SIZE=$(du -sh "$DMG_NAME.dmg" | cut -f1)
            print_success "DMG erstellt: $DMG_NAME.dmg ($DMG_SIZE)"
        else
            print_warning "DMG-Erstellung fehlgeschlagen"
        fi
    else
        print_warning "hdiutil nicht gefunden - DMG wird übersprungen"
    fi
    
    echo ""
    echo "🎉 Build erfolgreich abgeschlossen!"
    echo ""
    echo "📂 Erstellte Dateien:"
    echo "   App: $(pwd)/dist/FakeAccountScanner.app"
    if [ -f "FakeAccountScanner-1.0.0.dmg" ]; then
        echo "   DMG: $(pwd)/FakeAccountScanner-1.0.0.dmg"
    fi
    echo ""
    print_success "Die App ist bereit für die Verteilung!"
    
    # Frage ob App geöffnet werden soll
    echo ""
    read -p "Möchtest du die App jetzt testen? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_step "Starte FakeAccountScanner..."
        open "dist/FakeAccountScanner.app"
    fi
    
else
    print_error "App-Build fehlgeschlagen!"
    exit 1
fi