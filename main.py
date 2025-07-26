#!/usr/bin/env python3
"""
FakeAccountScanner - macOS Desktop App
Eine App zum Scannen von Social Media Plattformen nach Benutzernamen
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import asyncio
from typing import List, Dict, Any
import webbrowser

# Import unserer Scanner-Module
from scanner import SocialMediaScanner
from utils import setup_output_directory, validate_usernames


class FakeAccountScannerApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_ui()
        self.scanner = SocialMediaScanner()
        self.is_scanning = False
        
    def setup_window(self):
        """Konfiguriere das Hauptfenster"""
        self.root.title("FakeAccountScanner")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # macOS App Icon setzen (falls vorhanden)
        try:
            if sys.platform == "darwin":
                self.root.iconbitmap("")  # Default für macOS
        except:
            pass
            
        # Zentrierung des Fensters
        self.center_window()
        
    def center_window(self):
        """Zentriere das Fenster auf dem Bildschirm"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_ui(self):
        """Erstelle die Benutzeroberfläche"""
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Titel
        title_label = ttk.Label(main_frame, text="FakeAccountScanner", 
                               font=("Helvetica", 24, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Beschreibung
        desc_label = ttk.Label(main_frame, 
                              text="Durchsuche Social Media Plattformen nach Benutzernamen",
                              font=("Helvetica", 12))
        desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Benutzernamen-Eingabe
        ttk.Label(main_frame, text="Benutzernamen (kommagetrennt):").grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.username_entry = tk.Text(main_frame, height=4, width=50)
        self.username_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                                pady=(0, 10))
        
        # Scrollbar für Text-Widget
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", 
                                 command=self.username_entry.yview)
        scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))
        self.username_entry.configure(yscrollcommand=scrollbar.set)
        
        # Plattform-Auswahl
        ttk.Label(main_frame, text="Plattformen:").grid(
            row=4, column=0, sticky=tk.W, pady=(10, 5))
        
        platform_frame = ttk.Frame(main_frame)
        platform_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                           pady=(0, 20))
        
        self.platform_vars = {}
        platforms = ["Instagram", "TikTok", "Twitter/X"]
        for i, platform in enumerate(platforms):
            var = tk.BooleanVar(value=True)
            self.platform_vars[platform.lower().replace("/", "_")] = var
            cb = ttk.Checkbutton(platform_frame, text=platform, variable=var)
            cb.grid(row=0, column=i, padx=(0, 20), sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(0, 20))
        
        self.scan_button = ttk.Button(button_frame, text="Scan starten", 
                                     command=self.start_scan)
        self.scan_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self.stop_scan, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Ordner öffnen", 
                  command=self.open_output_folder).pack(side=tk.LEFT)
        
        # Progress Bar
        self.progress_var = tk.StringVar(value="Bereit zum Scannen")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(
            row=7, column=0, columnspan=2, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                              pady=(0, 20))
        
        # Ergebnisse-Bereich
        ttk.Label(main_frame, text="Scan-Log:").grid(
            row=9, column=0, sticky=tk.W, pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, width=70)
        self.log_text.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(10, weight=1)
        
    def log_message(self, message: str):
        """Füge eine Nachricht zum Log hinzu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_scan(self):
        """Starte den Scan-Prozess"""
        if self.is_scanning:
            return
            
        # Validiere Eingaben
        usernames_text = self.username_entry.get("1.0", tk.END).strip()
        if not usernames_text:
            messagebox.showerror("Fehler", "Bitte geben Sie mindestens einen Benutzernamen ein.")
            return
            
        usernames = validate_usernames(usernames_text)
        if not usernames:
            messagebox.showerror("Fehler", "Keine gültigen Benutzernamen gefunden.")
            return
            
        # Überprüfe ausgewählte Plattformen
        selected_platforms = [name for name, var in self.platform_vars.items() if var.get()]
        if not selected_platforms:
            messagebox.showerror("Fehler", "Bitte wählen Sie mindestens eine Plattform aus.")
            return
            
        # UI für Scan-Modus konfigurieren
        self.is_scanning = True
        self.scan_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_bar.start()
        self.progress_var.set("Scan wird gestartet...")
        self.log_text.delete("1.0", tk.END)
        
        # Scan in separatem Thread starten
        scan_thread = threading.Thread(
            target=self.run_scan,
            args=(usernames, selected_platforms),
            daemon=True
        )
        scan_thread.start()
        
    def run_scan(self, usernames: List[str], platforms: List[str]):
        """Führe den Scan in einem separaten Thread aus"""
        try:
            self.log_message(f"Starte Scan für {len(usernames)} Benutzernamen auf {len(platforms)} Plattformen")
            self.log_message(f"Benutzernamen: {', '.join(usernames)}")
            
            # Erstelle Output-Verzeichnis
            output_dir = setup_output_directory()
            self.log_message(f"Output-Verzeichnis: {output_dir}")
            
            # Führe den Scan aus
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                results = loop.run_until_complete(
                    self.scanner.scan_usernames(usernames, platforms, self.log_callback)
                )
                
                # Speichere Ergebnisse
                self.save_results(results, output_dir)
                
                # Zeige Ergebnisse an
                self.show_results(results)
                
            finally:
                loop.close()
                
        except Exception as e:
            self.log_message(f"Fehler beim Scannen: {str(e)}")
            messagebox.showerror("Scan-Fehler", f"Ein Fehler ist aufgetreten: {str(e)}")
        finally:
            # UI zurücksetzen
            self.root.after(0, self.finish_scan)
            
    def log_callback(self, message: str):
        """Callback-Funktion für Log-Nachrichten vom Scanner"""
        self.root.after(0, lambda: self.log_message(message))
        
    def save_results(self, results: List[Dict[str, Any]], output_dir: Path):
        """Speichere die Scan-Ergebnisse"""
        if results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = output_dir / f"scan_results_{timestamp}.json"
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
                
            self.log_message(f"Ergebnisse gespeichert: {results_file}")
        
    def show_results(self, results: List[Dict[str, Any]]):
        """Zeige die Scan-Ergebnisse in einem Pop-up an"""
        if not results:
            messagebox.showinfo("Scan abgeschlossen", "Keine Accounts gefunden.")
            return
            
        # Erstelle Pop-up-Fenster
        result_window = tk.Toplevel(self.root)
        result_window.title("Scan-Ergebnisse")
        result_window.geometry("600x400")
        result_window.transient(self.root)
        result_window.grab_set()
        
        # Ergebnisse-Text
        text_widget = scrolledtext.ScrolledText(result_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, f"Gefundene Accounts ({len(results)}):\n\n")
        
        for result in results:
            text_widget.insert(tk.END, f"Plattform: {result['platform']}\n")
            text_widget.insert(tk.END, f"Benutzername: {result['username']}\n")
            text_widget.insert(tk.END, f"URL: {result['url']}\n")
            text_widget.insert(tk.END, f"Zeitstempel: {result['timestamp']}\n")
            if result.get('screenshot_path'):
                text_widget.insert(tk.END, f"Screenshot: {result['screenshot_path']}\n")
            text_widget.insert(tk.END, "-" * 50 + "\n\n")
            
        text_widget.config(state=tk.DISABLED)
        
        # Button-Frame
        button_frame = ttk.Frame(result_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Schließen", 
                  command=result_window.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Ordner öffnen", 
                  command=self.open_output_folder).pack(side=tk.RIGHT, padx=(0, 10))
        
    def stop_scan(self):
        """Stoppe den aktuellen Scan"""
        if self.scanner:
            self.scanner.stop_scan()
        self.log_message("Scan-Stopp angefordert...")
        
    def finish_scan(self):
        """Setze die UI nach dem Scan zurück"""
        self.is_scanning = False
        self.scan_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_bar.stop()
        self.progress_var.set("Scan abgeschlossen")
        
    def open_output_folder(self):
        """Öffne den Output-Ordner"""
        output_dir = setup_output_directory()
        if sys.platform == "darwin":  # macOS
            os.system(f'open "{output_dir}"')
        elif sys.platform == "win32":  # Windows
            os.system(f'explorer "{output_dir}"')
        else:  # Linux
            os.system(f'xdg-open "{output_dir}"')


def main():
    """Hauptfunktion der Anwendung"""
    root = tk.Tk()
    app = FakeAccountScannerApp(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Anwendung beendet durch Benutzer")
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")
        messagebox.showerror("Kritischer Fehler", f"Ein kritischer Fehler ist aufgetreten:\n{e}")


if __name__ == "__main__":
    main()