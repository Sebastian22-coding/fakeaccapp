#!/usr/bin/env python3
"""
Build-Skript für FakeAccountScanner macOS App
Erstellt eine standalone .app mit PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform


def get_playwright_browsers_path():
    """Finde den Pfad zu den Playwright Browsern"""
    try:
        import playwright
        playwright_path = Path(playwright.__file__).parent
        browsers_path = playwright_path / "driver" / "package" / ".local-browsers"
        if browsers_path.exists():
            return str(browsers_path)
    except ImportError:
        pass
    
    # Fallback: Standard-Pfad
    home = Path.home()
    browsers_path = home / ".cache" / "ms-playwright"
    if browsers_path.exists():
        return str(browsers_path)
    
    return None


def create_pyinstaller_spec():
    """Erstelle eine .spec Datei für PyInstaller"""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Playwright Browser-Pfad
def get_playwright_data():
    """Sammle Playwright-Dateien"""
    datas = []
    
    try:
        import playwright
        playwright_path = Path(playwright.__file__).parent
        
        # Driver-Dateien
        driver_path = playwright_path / "driver"
        if driver_path.exists():
            datas.append((str(driver_path), "playwright/driver"))
        
        # Browser-Binaries (falls vorhanden)
        browsers_path = Path.home() / ".cache" / "ms-playwright"
        if browsers_path.exists():
            for browser_dir in browsers_path.iterdir():
                if browser_dir.is_dir():
                    datas.append((str(browser_dir), f"ms-playwright/{browser_dir.name}"))
    except ImportError:
        pass
    
    return datas

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=get_playwright_data(),
    hiddenimports=[
        'playwright',
        'playwright.async_api',
        'playwright._impl',
        'playwright._impl._api_structures',
        'playwright._impl._browser',
        'playwright._impl._browser_context',
        'playwright._impl._page',
        'playwright._impl._connection',
        'asyncio',
        'concurrent.futures',
        'websockets',
        'pyee',
        'greenlet'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FakeAccountScanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='universal2',
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FakeAccountScanner',
)

app = BUNDLE(
    coll,
    name='FakeAccountScanner.app',
    icon=None,
    bundle_identifier='com.fakeaccountscanner.app',
    version='1.0.0',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'CFBundleDisplayName': 'FakeAccountScanner',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2024 FakeAccountScanner',
    },
)
'''
    
    with open('FakeAccountScanner.spec', 'w') as f:
        f.write(spec_content)
    
    print("✓ PyInstaller spec file created")


def install_dependencies():
    """Installiere alle notwendigen Abhängigkeiten"""
    print("📦 Installiere Python-Abhängigkeiten...")
    
    # Installiere Requirements
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
    
    # Installiere PyInstaller falls nicht vorhanden
    try:
        import PyInstaller
    except ImportError:
        print("📦 Installiere PyInstaller...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    
    # Installiere Playwright Browser
    print("🌐 Installiere Playwright Browser...")
    subprocess.run([sys.executable, '-m', 'playwright', 'install'], check=True)
    
    print("✓ Alle Abhängigkeiten installiert")


def build_app():
    """Baue die macOS App"""
    print("🔨 Starte App-Build...")
    
    # Bereinige vorherige Builds
    for path in ['build', 'dist', '__pycache__']:
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"✓ {path} bereinigt")
    
    # Erstelle spec file
    create_pyinstaller_spec()
    
    # Baue mit PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'FakeAccountScanner.spec'
    ]
    
    print("🔨 Führe PyInstaller aus...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Build fehlgeschlagen!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    print("✅ Build erfolgreich!")
    
    # Überprüfe ob App erstellt wurde
    app_path = Path('dist/FakeAccountScanner.app')
    if app_path.exists():
        print(f"✅ App erstellt: {app_path.absolute()}")
        
        # Zeige App-Größe
        size = get_directory_size(app_path)
        print(f"📦 App-Größe: {format_size(size)}")
        
        return True
    else:
        print("❌ App nicht gefunden!")
        return False


def get_directory_size(path):
    """Berechne Verzeichnisgröße"""
    total = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.exists(file_path):
                total += os.path.getsize(file_path)
    return total


def format_size(size_bytes):
    """Formatiere Größe in lesbarer Form"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def create_dmg():
    """Erstelle ein DMG-Image (optional)"""
    app_path = Path('dist/FakeAccountScanner.app')
    if not app_path.exists():
        print("❌ App nicht gefunden für DMG-Erstellung")
        return False
    
    print("📀 Erstelle DMG-Image...")
    
    dmg_name = "FakeAccountScanner-1.0.0"
    
    # Entferne altes DMG falls vorhanden
    if os.path.exists(f"{dmg_name}.dmg"):
        os.remove(f"{dmg_name}.dmg")
    
    # Erstelle DMG mit hdiutil
    cmd = [
        'hdiutil', 'create',
        '-volname', 'FakeAccountScanner',
        '-srcfolder', 'dist/FakeAccountScanner.app',
        '-ov',
        '-format', 'UDZO',
        f'{dmg_name}.dmg'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ DMG erstellt: {dmg_name}.dmg")
        return True
    except subprocess.CalledProcessError as e:
        print("⚠️  DMG-Erstellung fehlgeschlagen (optional):")
        print(e.stderr)
        return False


def main():
    """Hauptfunktion für den Build-Prozess"""
    print("🚀 FakeAccountScanner macOS Build")
    print("=" * 50)
    
    # Überprüfe Betriebssystem
    if platform.system() != 'Darwin':
        print("⚠️  Warnung: Dieser Build ist für macOS optimiert")
    
    try:
        # 1. Installiere Abhängigkeiten
        install_dependencies()
        
        # 2. Baue App
        if build_app():
            print("\n🎉 Build erfolgreich abgeschlossen!")
            
            # 3. Optionale DMG-Erstellung
            create_dmg()
            
            print("\n📂 Output-Dateien:")
            print(f"   App: dist/FakeAccountScanner.app")
            if os.path.exists("FakeAccountScanner-1.0.0.dmg"):
                print(f"   DMG: FakeAccountScanner-1.0.0.dmg")
            
            print("\n✅ Die App ist bereit für die Verteilung!")
        else:
            print("\n❌ Build fehlgeschlagen!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Build abgebrochen durch Benutzer")
        return 1
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())