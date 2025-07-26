"""
Social Media Scanner Modul
Verwendet Playwright für das Scannen von Social Media Plattformen
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
import json
import time

from playwright.async_api import async_playwright, Browser, Page
from utils import setup_output_directory


class SocialMediaScanner:
    def __init__(self):
        self.browser = None
        self.context = None
        self.should_stop = False
        self.platforms = {
            'instagram': {
                'name': 'Instagram',
                'url_template': 'https://www.instagram.com/{}/',
                'selectors': {
                    'profile_exists': 'header section',
                    'profile_name': 'h2',
                    'not_found': 'span:has-text("Diese Seite ist leider nicht verfügbar")'
                }
            },
            'tiktok': {
                'name': 'TikTok',
                'url_template': 'https://www.tiktok.com/@{}',
                'selectors': {
                    'profile_exists': '[data-e2e="user-page"]',
                    'profile_name': '[data-e2e="user-title"]',
                    'not_found': 'div:has-text("Couldn\'t find this account")'
                }
            },
            'twitter_x': {
                'name': 'Twitter/X',
                'url_template': 'https://x.com/{}',
                'selectors': {
                    'profile_exists': '[data-testid="UserName"]',
                    'profile_name': '[data-testid="UserName"]',
                    'not_found': 'span:has-text("This account doesn\'t exist")'
                }
            }
        }
        
    async def scan_usernames(self, usernames: List[str], platforms: List[str], 
                           log_callback: Callable[[str], None]) -> List[Dict[str, Any]]:
        """Scanne Benutzernamen auf den angegebenen Plattformen"""
        results = []
        
        try:
            log_callback("Initialisiere Browser...")
            await self._setup_browser()
            
            total_scans = len(usernames) * len(platforms)
            current_scan = 0
            
            for username in usernames:
                if self.should_stop:
                    log_callback("Scan wurde gestoppt")
                    break
                    
                for platform in platforms:
                    if self.should_stop:
                        break
                        
                    current_scan += 1
                    log_callback(f"Scanne {username} auf {self.platforms[platform]['name']} "
                               f"({current_scan}/{total_scans})")
                    
                    try:
                        result = await self._scan_single_profile(username, platform, log_callback)
                        if result:
                            results.append(result)
                            log_callback(f"✓ Gefunden: {username} auf {self.platforms[platform]['name']}")
                        else:
                            log_callback(f"✗ Nicht gefunden: {username} auf {self.platforms[platform]['name']}")
                            
                        # Kurze Pause zwischen Anfragen
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        log_callback(f"Fehler bei {username} auf {platform}: {str(e)}")
                        
        except Exception as e:
            log_callback(f"Kritischer Fehler: {str(e)}")
            raise
        finally:
            await self._cleanup_browser()
            
        log_callback(f"Scan abgeschlossen. {len(results)} Accounts gefunden.")
        return results
        
    async def _setup_browser(self):
        """Initialisiere den Browser"""
        self.playwright = await async_playwright().start()
        
        # Browser starten (Chromium für beste Kompatibilität)
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Browser-Kontext mit realistischen Headers erstellen
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='de-DE'
        )
        
    async def _cleanup_browser(self):
        """Schließe Browser und Playwright"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
            
    async def _scan_single_profile(self, username: str, platform: str, 
                                 log_callback: Callable[[str], None]) -> Optional[Dict[str, Any]]:
        """Scanne ein einzelnes Profil auf einer Plattform"""
        platform_config = self.platforms[platform]
        url = platform_config['url_template'].format(username)
        
        try:
            page = await self.context.new_page()
            
            # Zusätzliche Stealth-Maßnahmen
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            # Seite laden mit Timeout
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Warten bis Seite geladen ist
            await page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(3)  # Zusätzliche Wartezeit für dynamischen Content
            
            # Prüfen ob Profil existiert
            profile_exists = await self._check_profile_exists(page, platform_config)
            
            if profile_exists:
                # Screenshot erstellen
                screenshot_path = await self._take_screenshot(page, username, platform)
                
                result = {
                    'platform': platform_config['name'],
                    'username': username,
                    'url': url,
                    'timestamp': datetime.now().isoformat(),
                    'screenshot_path': str(screenshot_path) if screenshot_path else None,
                    'status': 'found'
                }
                
                return result
                
            await page.close()
            return None
            
        except Exception as e:
            if 'page' in locals():
                await page.close()
            raise Exception(f"Fehler beim Laden von {url}: {str(e)}")
            
    async def _check_profile_exists(self, page: Page, platform_config: Dict) -> bool:
        """Überprüfe ob ein Profil auf der Seite existiert"""
        try:
            # Warte auf einen der möglichen Zustände
            selectors = platform_config['selectors']
            
            # Prüfe auf "Nicht gefunden" Indikatoren
            if 'not_found' in selectors:
                not_found_elements = await page.query_selector_all(selectors['not_found'])
                if not_found_elements:
                    return False
                    
            # Prüfe auf Profil-Existenz Indikatoren
            if 'profile_exists' in selectors:
                profile_elements = await page.query_selector_all(selectors['profile_exists'])
                if profile_elements:
                    return True
                    
            # Fallback: Prüfe HTTP Status
            response = page.url
            if '404' in response or 'not-found' in response.lower():
                return False
                
            # Weitere Heuristiken basierend auf Seiteninhalt
            page_content = await page.content()
            
            # Negative Indikatoren
            negative_indicators = [
                'not found',
                'user not found',
                'page not found',
                'this account doesn\'t exist',
                'profile not found',
                'user does not exist',
                'Diese Seite ist leider nicht verfügbar',
                'Couldn\'t find this account'
            ]
            
            for indicator in negative_indicators:
                if indicator.lower() in page_content.lower():
                    return False
                    
            # Positive Indikatoren
            positive_indicators = [
                'followers',
                'following',
                'posts',
                'profile',
                'bio'
            ]
            
            for indicator in positive_indicators:
                if indicator.lower() in page_content.lower():
                    return True
                    
            # Default: Als nicht gefunden betrachten
            return False
            
        except Exception as e:
            # Im Zweifelsfall als nicht existierend betrachten
            return False
            
    async def _take_screenshot(self, page: Page, username: str, platform: str) -> Optional[Path]:
        """Erstelle einen Screenshot der Profilseite"""
        try:
            output_dir = setup_output_directory()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"{platform}_{username}_{timestamp}.png"
            screenshot_path = output_dir / screenshot_name
            
            # Vollständigen Screenshot erstellen
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            return screenshot_path
            
        except Exception as e:
            print(f"Fehler beim Erstellen des Screenshots: {e}")
            return None
            
    def stop_scan(self):
        """Stoppe den aktuellen Scan"""
        self.should_stop = True


# Hilfsfunktionen für spezielle Plattform-Behandlung

async def handle_instagram_login_popup(page: Page):
    """Behandle Instagram Login-Popup falls es erscheint"""
    try:
        # Warte kurz und prüfe auf Login-Dialog
        await asyncio.sleep(2)
        close_button = await page.query_selector('button:has-text("Nicht jetzt")')
        if close_button:
            await close_button.click()
            await asyncio.sleep(1)
    except:
        pass


async def handle_cookie_banner(page: Page):
    """Behandle Cookie-Banner"""
    try:
        # Verschiedene Cookie-Banner-Selektoren
        cookie_selectors = [
            'button:has-text("Accept")',
            'button:has-text("Akzeptieren")',
            'button:has-text("OK")',
            '[aria-label="Close"]',
            '.cookie-banner button'
        ]
        
        for selector in cookie_selectors:
            button = await page.query_selector(selector)
            if button:
                await button.click()
                await asyncio.sleep(1)
                break
    except:
        pass