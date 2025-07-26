# FakeAccountScanner 🔍

Eine benutzerfreundliche macOS Desktop-App zum Scannen von Social Media Plattformen nach Benutzernamen. Die App durchsucht Instagram, TikTok und Twitter/X nach existierenden Accounts und erstellt automatisch Screenshots sowie detaillierte Berichte.

## 🌟 Features

- **Multi-Plattform-Scanning**: Unterstützt Instagram, TikTok und Twitter/X
- **Batch-Processing**: Scannen mehrerer Benutzernamen gleichzeitig
- **Automatische Screenshots**: Vollständige Screenshots von gefundenen Profilen
- **Detaillierte Berichte**: JSON-Export mit allen gefundenen Informationen
- **Headless Browser**: Verwendet Playwright für zuverlässiges Web-Scraping
- **Native macOS App**: Standalone .app-Datei ohne zusätzliche Installationen
- **Universal Binary**: Unterstützt sowohl Intel (x64) als auch Apple Silicon (arm64)

## 📱 Screenshot

```
┌─────────────────────────────────────────┐
│  FakeAccountScanner                     │
├─────────────────────────────────────────┤
│  Durchsuche Social Media Plattformen   │
│  nach Benutzernamen                     │
│                                         │
│  Benutzernamen (kommagetrennt):         │
│  ┌─────────────────────────────────────┐ │
│  │ testuser, example, demouser         │ │
│  └─────────────────────────────────────┘ │
│                                         │
│  Plattformen:                           │
│  ☑ Instagram  ☑ TikTok  ☑ Twitter/X    │
│                                         │
│  [Scan starten] [Stop] [Ordner öffnen] │
│                                         │
│  Scan-Log:                              │
│  ┌─────────────────────────────────────┐ │
│  │ [14:30:15] Starte Scan für 3       │ │
│  │ [14:30:16] ✓ Gefunden: testuser    │ │
│  │ [14:30:18] ✗ Nicht gefunden: ex... │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 🚀 Installation

### Option 1: Fertige App herunterladen (Empfohlen)

1. Lade die neueste Version von der [Releases-Seite] herunter
2. Entpacke die `FakeAccountScanner.app`
3. Ziehe die App in den Programme-Ordner
4. Doppelklick zum Starten

### Option 2: Aus Quellcode bauen

#### Voraussetzungen

- macOS 10.15+ (Catalina oder neuer)
- Python 3.8+
- Xcode Command Line Tools

#### Build-Anweisungen

```bash
# Repository klonen
git clone https://github.com/fakeaccountscanner/fake-account-scanner.git
cd fake-account-scanner

# Abhängigkeiten installieren und App bauen
make all

# Oder schrittweise:
make install    # Abhängigkeiten installieren
make build      # App bauen
make dmg        # DMG-Image erstellen (optional)
```

Die fertige App befindet sich dann in `dist/FakeAccountScanner.app`.

## 🎯 Verwendung

### 1. App starten

Doppelklick auf `FakeAccountScanner.app` oder aus dem Launchpad.

### 2. Benutzernamen eingeben

- Gib die zu suchenden Benutzernamen kommagetrennt ein
- Beispiel: `testuser, example_account, demo123`
- URLs werden automatisch bereinigt (du kannst auch `@username` oder vollständige Profile-URLs eingeben)

### 3. Plattformen auswählen

Wähle die zu durchsuchenden Plattformen:
- ☑ Instagram
- ☑ TikTok  
- ☑ Twitter/X

### 4. Scan starten

Klicke auf "Scan starten" und verfolge den Fortschritt im Log-Bereich.

### 5. Ergebnisse anzeigen

- Gefundene Accounts werden in einem Pop-up angezeigt
- Screenshots und JSON-Berichte werden automatisch gespeichert
- Klicke "Ordner öffnen" um die Ergebnisse im Finder zu öffnen

## 📁 Output-Struktur

Alle Ergebnisse werden im `~/fake_account_reports/` Ordner gespeichert:

```
~/fake_account_reports/
├── instagram_testuser_20241208_143015.png
├── tiktok_testuser_20241208_143018.png
├── twitter_x_testuser_20241208_143021.png
└── scan_results_20241208_143025.json
```

### JSON-Report Format

```json
[
  {
    "platform": "Instagram",
    "username": "testuser",
    "url": "https://www.instagram.com/testuser/",
    "timestamp": "2024-12-08T14:30:15.123456",
    "screenshot_path": "/Users/name/fake_account_reports/instagram_testuser_20241208_143015.png",
    "status": "found"
  }
]
```

## ⚙️ Konfiguration

### Browser-Einstellungen

Die App verwendet Playwright mit Chromium im Headless-Modus. Die Browser-Binaries sind in die App integriert.

### Rate Limiting

- Automatische Pausen zwischen Anfragen (2 Sekunden)
- Realistische User-Agent-Strings
- Stealth-Modus um Erkennung zu vermeiden

## 🛠️ Entwicklung

### Projektstruktur

```
fake-account-scanner/
├── main.py              # Haupt-GUI-Anwendung
├── scanner.py           # Playwright-basierter Scanner
├── utils.py             # Hilfsfunktionen
├── build_spec.py        # PyInstaller Build-Skript
├── requirements.txt     # Python-Abhängigkeiten
├── Makefile            # Build-Automatisierung
├── setup.py            # Package-Setup
└── README.md           # Diese Datei
```

### Verfügbare Make-Befehle

```bash
make help           # Zeige alle verfügbaren Befehle
make install        # Installiere Abhängigkeiten
make run            # Starte App im Entwicklungsmodus
make build          # Baue macOS App
make dmg            # Erstelle DMG-Image
make clean          # Bereinige Build-Artefakte
make test           # Führe Tests aus
make lint           # Code-Überprüfung
make format         # Code-Formatierung
```

### Debugging

```bash
# App mit Debug-Output starten
python main.py

# Playwright-Debug-Modus
PWDEBUG=1 python main.py
```

## 🔒 Sicherheit & Datenschutz

- **Keine Anmeldung erforderlich**: Die App greift nur auf öffentlich verfügbare Profile zu
- **Lokale Datenverarbeitung**: Alle Daten bleiben auf deinem Mac
- **Keine Datenübertragung**: Keine Verbindung zu externen Servern (außer den Social Media Plattformen)
- **Respekt für Rate Limits**: Automatische Pausen um Server-Überlastung zu vermeiden

## ⚠️ Rechtliche Hinweise

- Diese App dient nur zu Informationszwecken
- Respektiere die Nutzungsbedingungen der jeweiligen Plattformen
- Verwende die App verantwortungsvoll und nicht für Stalking oder Harassment
- Beachte lokale Gesetze und Datenschutzbestimmungen

## 🐛 Fehlerbehebung

### Häufige Probleme

**App startet nicht:**
- Überprüfe macOS-Version (10.15+)
- Installiere Xcode Command Line Tools: `xcode-select --install`
- Prüfe Gatekeeper-Einstellungen in den Systemeinstellungen

**Scan-Fehler:**
- Überprüfe Internetverbindung
- Manche Plattformen können vorübergehend blockieren
- Starte die App neu und versuche es erneut

**Screenshots fehlerhaft:**
- Stelle sicher, dass genügend Speicherplatz vorhanden ist
- Überprüfe Schreibberechtigungen für den Home-Ordner

### Debug-Logs

Wenn Probleme auftreten, überprüfe die Konsole-App nach FakeAccountScanner-Logs.

## 🤝 Beitragen

Beiträge sind willkommen! Bitte:

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/amazing-feature`)
3. Committe deine Änderungen (`git commit -m 'Add amazing feature'`)
4. Push den Branch (`git push origin feature/amazing-feature`)
5. Öffne eine Pull Request

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE) für Details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/fakeaccountscanner/fake-account-scanner/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/fakeaccountscanner/fake-account-scanner/discussions)
- **E-Mail**: info@fakeaccountscanner.com

## 🎉 Danksagungen

- [Playwright](https://playwright.dev/) für das Web-Scraping-Framework
- [PyInstaller](https://pyinstaller.org/) für die App-Paketierung
- [Tkinter](https://docs.python.org/3/library/tkinter.html) für die GUI

---

**⚡ FakeAccountScanner - Schnell, zuverlässig und benutzerfreundlich**