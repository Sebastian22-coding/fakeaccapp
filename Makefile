# Makefile für FakeAccountScanner

.PHONY: help install build clean test run dev dmg all

# Hilfe-Nachricht
help:
	@echo "FakeAccountScanner Build-System"
	@echo "================================"
	@echo ""
	@echo "Verfügbare Befehle:"
	@echo "  install    - Installiere alle Abhängigkeiten"
	@echo "  build      - Baue die macOS App"
	@echo "  dmg        - Erstelle DMG-Image"
	@echo "  run        - Starte die App (Entwicklungsmodus)"
	@echo "  test       - Führe Tests aus"
	@echo "  clean      - Bereinige Build-Artefakte"
	@echo "  dev        - Setup für Entwicklung"
	@echo "  all        - Vollständiger Build-Prozess"
	@echo ""

# Installation der Abhängigkeiten
install:
	@echo "📦 Installiere Abhängigkeiten..."
	pip install -r requirements.txt
	pip install pyinstaller
	playwright install
	@echo "✅ Installation abgeschlossen"

# Entwicklungssetup
dev: install
	@echo "🛠️  Setup für Entwicklung..."
	pip install -e .
	pip install black flake8 pytest
	@echo "✅ Entwicklungsumgebung bereit"

# App ausführen (Entwicklungsmodus)
run:
	@echo "🚀 Starte FakeAccountScanner..."
	python main.py

# Tests ausführen
test:
	@echo "🧪 Führe Tests aus..."
	python -m pytest tests/ -v
	@echo "✅ Tests abgeschlossen"

# Build bereinigen
clean:
	@echo "🧹 Bereinige Build-Artefakte..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -f *.spec
	rm -f *.dmg
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	@echo "✅ Bereinigung abgeschlossen"

# App bauen
build: clean
	@echo "🔨 Baue FakeAccountScanner App..."
	python build_spec.py
	@echo "✅ Build abgeschlossen"

# DMG erstellen
dmg:
	@echo "📀 Erstelle DMG-Image..."
	@if [ ! -d "dist/FakeAccountScanner.app" ]; then \
		echo "❌ App nicht gefunden. Führe zuerst 'make build' aus."; \
		exit 1; \
	fi
	hdiutil create -volname "FakeAccountScanner" \
		-srcfolder "dist/FakeAccountScanner.app" \
		-ov -format UDZO \
		"FakeAccountScanner-1.0.0.dmg"
	@echo "✅ DMG erstellt: FakeAccountScanner-1.0.0.dmg"

# Vollständiger Build-Prozess
all: install build dmg
	@echo "🎉 Vollständiger Build abgeschlossen!"
	@echo ""
	@echo "📂 Erstellte Dateien:"
	@ls -la dist/FakeAccountScanner.app
	@if [ -f "FakeAccountScanner-1.0.0.dmg" ]; then \
		ls -la FakeAccountScanner-1.0.0.dmg; \
	fi
	@echo ""
	@echo "✅ Die App ist bereit für die Verteilung!"

# Code-Formatierung
format:
	@echo "🎨 Formatiere Code..."
	black *.py
	@echo "✅ Code formatiert"

# Linting
lint:
	@echo "🔍 Überprüfe Code..."
	flake8 *.py
	@echo "✅ Code-Überprüfung abgeschlossen"

# Installiere macOS Entwicklungstools (falls benötigt)
install-macos-tools:
	@echo "🔧 Überprüfe macOS Entwicklungstools..."
	@if ! command -v hdiutil &> /dev/null; then \
		echo "❌ hdiutil nicht gefunden. Installiere Xcode Command Line Tools."; \
		xcode-select --install; \
	else \
		echo "✅ macOS Entwicklungstools verfügbar"; \
	fi

# Zeige System-Informationen
info:
	@echo "ℹ️  System-Informationen:"
	@echo "  Python-Version: $(shell python --version)"
	@echo "  Plattform: $(shell uname -sm)"
	@echo "  Arbeitsverzeichnis: $(shell pwd)"
	@echo "  Pip-Version: $(shell pip --version)"
	@if command -v playwright &> /dev/null; then \
		echo "  Playwright: ✅ installiert"; \
	else \
		echo "  Playwright: ❌ nicht installiert"; \
	fi