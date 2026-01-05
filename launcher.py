import sys
import tkinter as tk
from tkinter import ttk
import subprocess
import os

class LauncherWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Waybridge Agent Launcher")
        self.window.geometry("400x250")
        self.window.resizable(False, False)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create the launcher UI"""
        main_frame = ttk.Frame(self.window, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Waybridge Agent", 
                                font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 30))
        
        # Description
        desc_label = ttk.Label(main_frame, 
                              text="Choose an option to continue:",
                              font=('Arial', 10))
        desc_label.grid(row=1, column=0, pady=(0, 20))
        
        # Buttons
        settings_btn = ttk.Button(main_frame, text="⚙️  Settings", 
                                 command=self.open_settings,
                                 width=30)
        settings_btn.grid(row=2, column=0, pady=10)
        
        start_btn = ttk.Button(main_frame, text="▶️  Start Agent", 
                              command=self.start_agent,
                              width=30)
        start_btn.grid(row=3, column=0, pady=10)
        
        exit_btn = ttk.Button(main_frame, text="❌  Exit", 
                             command=self.window.destroy,
                             width=30)
        exit_btn.grid(row=4, column=0, pady=10)
        
    def open_settings(self):
        """Open settings window"""
        from settings_gui import SettingsWindow
        self.window.withdraw()  # Hide launcher
        settings = SettingsWindow()
        settings.run()
        self.window.deiconify()  # Show launcher again
        
    def start_agent(self):
        """Start the waybridge agent"""
        self.window.destroy()
        # Import and run main
        import main
        
    def run(self):
        """Run the launcher window"""
        self.window.mainloop()

if __name__ == "__main__":
    app = LauncherWindow()
    app.run()
