"""
Settings GUI for Waybridge Agent
Provides graphical interface for configuration management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from config_manager import get_config, ConfigurationError, reload_config
from erp_client import get_erp_client


class SettingsWindow:
    """Settings window for Waybridge Agent configuration"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize settings window
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        
        try:
            self.config = get_config(config_path)
        except ConfigurationError as e:
            messagebox.showerror("Configuration Error", str(e))
            raise
        
        self.window = tk.Tk()
        self.window.title("Waybridge Agent Settings")
        self.window.geometry("700x650")
        self.window.resizable(False, False)
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the settings UI"""
        # Main container with scrollbar
        main_container = ttk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas for scrolling
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Waybridge Agent Configuration",
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        current_row = 1
        
        # ERP Settings Section
        current_row = self.create_erp_section(scrollable_frame, current_row)
        
        # Serial Settings Section
        current_row = self.create_serial_section(scrollable_frame, current_row)
        
        # Weighbridge Settings Section
        current_row = self.create_weighbridge_section(scrollable_frame, current_row)
        
        # Logging Settings Section
        current_row = self.create_logging_section(scrollable_frame, current_row)
        
        # App Settings Section
        current_row = self.create_app_section(scrollable_frame, current_row)
        
        # Buttons
        self.create_buttons(scrollable_frame, current_row)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_erp_section(self, parent, start_row):
        """Create ERP settings section"""
        ttk.Label(parent, text="ERP Connection Settings",
                  font=('Arial', 12, 'bold')).grid(
            row=start_row, column=0, columnspan=3, sticky=tk.W, pady=(10, 10))
        
        # API Endpoint URL
        ttk.Label(parent, text="API Endpoint URL:").grid(
            row=start_row + 1, column=0, sticky=tk.W, pady=5, padx=(20, 5))
        self.url_entry = ttk.Entry(parent, width=60)
        self.url_entry.grid(row=start_row + 1, column=1, columnspan=2,
                            sticky=(tk.W, tk.E), pady=5, padx=(5, 20))
        self.url_entry.insert(0, self.config.get('erp.url', ''))
        
        # API Token
        ttk.Label(parent, text="API Token:").grid(
            row=start_row + 2, column=0, sticky=tk.W, pady=5, padx=(20, 5))
        self.token_entry = ttk.Entry(parent, width=60, show="*")
        self.token_entry.grid(row=start_row + 2, column=1, columnspan=2,
                              sticky=(tk.W, tk.E), pady=5, padx=(5, 20))
        self.token_entry.insert(0, self.config.get('erp.token', ''))
        
        # Show/Hide token
        self.show_token_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(parent, text="Show Token",
                        variable=self.show_token_var,
                        command=self.toggle_token_visibility).grid(
            row=start_row + 3, column=1, sticky=tk.W, padx=(5, 0))
        
        # Timeout
        ttk.Label(parent, text="Timeout (seconds):").grid(
            row=start_row + 4, column=0, sticky=tk.W, pady=5, padx=(20, 5))
        self.timeout_entry = ttk.Entry(parent, width=20)
        self.timeout_entry.grid(row=start_row + 4, column=1,
                                sticky=tk.W, pady=5, padx=(5, 0))
        self.timeout_entry.insert(0, str(self.config.get('erp.timeout', 10)))
        
        # Retry Attempts
        ttk.Label(parent, text="Retry Attempts:").grid(
            row=start_row + 5, column=0, sticky=tk.W, pady=5, padx=(20, 5))
        self.retry_attempts_entry = ttk.Entry(parent, width=20)
        self.retry_attempts_entry.grid(row=start_row + 5, column=1,
                                       sticky=tk.W, pady=5, padx=(5, 0))
        self.retry_attempts_entry.insert(0, str(self.config.get('erp.retry_attempts', 3)))
        
        # Retry Delay
        ttk.Label(parent, text="Retry Delay (seconds):").grid(
            row=start_row + 6, column=0, sticky=tk.W, pady=5, padx=(20, 5))
        self.retry_delay_entry = ttk.Entry(parent, width=20)
        self.retry_delay_entry.grid(row=start_row + 6, column=1,
                                    sticky=tk.W, pady=5, padx=(5, 0))
        self.retry_delay_entry.insert(0, str(self.config.get('erp.retry_delay', 2)))
        
        return start_row + 7
    
    def create_serial_section(self, parent, start_row):
        """Create serial settings section"""
        ttk.Label(parent, text="Serial Port Settings",
                  font=('Arial', 12, 'bold')).grid(
            row=start_row, column=0, columnspan=3, sticky=tk.W, pady=(20, 10))
        
        # COM Port
        ttk.Label(parent, text="COM Port:").grid(
            row=start_row + 1, column=0, sticky=tk.W, pady=5, padx=(20, 5))
        self.port_entry = ttk.Entry(parent, width=20)
        self.port_entry.grid(row=start_row + 1, column=1,
                             sticky=tk.W, pady=5, padx=(5, 0))
        self.port_entry.insert(0, self.config.get('serial.port', 'COM3'))
        
        # Baud Rate
        ttk.Label(parent, text="Baud Rate:").grid(
            row=start_row + 2, column=0, sticky=tk.W, pady=5, padx=(20, 5))
        self.baudrate_combo = ttk.Combobox(parent, width=18, state='readonly')
        self.baudrate_combo['values'] = (300, 600, 1200, 2400, 4800, 9600,
                                          14400, 19200, 38400, 57600, 115200)
        self.baudrate_combo.grid(row=start_row + 2, column=1,
                                 sticky=tk.W, pady=5, padx=(5, 0))
        self.baudrate_combo.set(str(self.config.get('serial.baudrate', 9600)))
        
        # Timeout
        ttk.Label(parent, text="Timeout (seconds):").grid(
            row=start_row + 3, column=0, sticky=tk.W, pady=5, padx=(20, 5))
        self.serial_timeout_entry = ttk.Entry(parent, width=20)
        self.serial_timeout_entry.grid(row=start_row + 3, column=1,
                                       sticky=tk.W, pady=5, padx=(5, 0))
        self.serial_timeout_entry.insert(0, str(self.config.get('serial.timeout', 1)))
        
        return start_row + 4
    
    def create_weighbridge_section(self, parent, start_row):
        """Create weighbridge settings section"""
        ttk.Label(parent, text="Weighbridge Settings",
                  font=('Arial', 12, 'bold')).grid(
            row=start_row, column=0, columnspan=3, sticky=tk.W, pady=(20, 10))
        
        # Weighbridge ID
        ttk.Label(parent, text="Weighbridge ID:").grid(
            row=start_row + 1, column=0, sticky=tk.W, pady=5, padx=(20, 5))
        self.wb_id_entry = ttk.Entry(parent, width=20)
        self.wb_id_entry.grid(row=start_row + 1, column=1,
                              sticky=tk.W, pady=5, padx=(5, 0))
        self.wb_id_entry.insert(0, self.config.get('weighbridge.id', 'WB-01'))
        
        # Unit
        ttk.Label(parent, text="Unit:").grid(
            row=start_row + 2, column=0, sticky=tk.W, pady=5, padx=(20, 5))
        self.unit_combo = ttk.Combobox(parent, width=18, state='readonly')
        self.unit_combo['values'] = ('kg', 'lb', 'ton', 'g')
        self.unit_combo.grid(row=start_row + 2, column=1,
                             sticky=tk.W, pady=5, padx=(5, 0))
        self.unit_combo.set(self.config.get('weighbridge.unit', 'kg'))
        
        # Precision
        ttk.Label(parent, text="Precision (decimals):").grid(
            row=start_row + 3, column=0, sticky=tk.W, pady=5, padx=(20, 5))
        self.precision_spin = ttk.Spinbox(parent, from_=0, to=10, width=18)
        self.precision_spin.grid(row=start_row + 3, column=1,
                                 sticky=tk.W, pady=5, padx=(5, 0))
        self.precision_spin.set(self.config.get('weighbridge.precision', 2))
        
        return start_row + 4
    
    def create_logging_section(self, parent, start_row):
        """Create logging settings section"""
        ttk.Label(parent, text="Logging Settings",
                  font=('Arial', 12, 'bold')).grid(
            row=start_row, column=0, columnspan=3, sticky=tk.W, pady=(20, 10))
        
        # Log Level
        ttk.Label(parent, text="Log Level:").grid(
            row=start_row + 1, column=0, sticky=tk.W, pady=5, padx=(20, 5))
        self.log_level_combo = ttk.Combobox(parent, width=18, state='readonly')
        self.log_level_combo['values'] = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        self.log_level_combo.grid(row=start_row + 1, column=1,
                                  sticky=tk.W, pady=5, padx=(5, 0))
        self.log_level_combo.set(self.config.get('logging.level', 'INFO'))
        
        # Log File
        ttk.Label(parent, text="Log File:").grid(
            row=start_row + 2, column=0, sticky=tk.W, pady=5, padx=(20, 5))
        self.log_file_entry = ttk.Entry(parent, width=40)
        self.log_file_entry.grid(row=start_row + 2, column=1,
                                 sticky=tk.W, pady=5, padx=(5, 0))
        self.log_file_entry.insert(0, self.config.get('logging.file', 'waybridge_agent.log'))
        
        return start_row + 3
    
    def create_app_section(self, parent, start_row):
        """Create app settings section"""
        ttk.Label(parent, text="Application Settings",
                  font=('Arial', 12, 'bold')).grid(
            row=start_row, column=0, columnspan=3, sticky=tk.W, pady=(20, 10))
        
        # Auto Start
        self.auto_start_var = tk.BooleanVar(value=self.config.get('app.auto_start', False))
        ttk.Checkbutton(parent, text="Auto-start on system boot",
                        variable=self.auto_start_var).grid(
            row=start_row + 1, column=0, columnspan=2, sticky=tk.W, padx=(20, 0), pady=5)
        
        return start_row + 2
    
    def create_buttons(self, parent, start_row):
        """Create action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=start_row, column=0, columnspan=3, pady=(30, 10))
        
        ttk.Button(button_frame, text="💾 Save Settings",
                   command=self.save_settings).grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="🔌 Test Connection",
                   command=self.test_connection).grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="🔄 Reset to Defaults",
                   command=self.reset_defaults).grid(row=0, column=2, padx=5)
        
        ttk.Button(button_frame, text="❌ Cancel",
                   command=self.window.destroy).grid(row=0, column=3, padx=5)
    
    def toggle_token_visibility(self):
        """Toggle token visibility"""
        if self.show_token_var.get():
            self.token_entry.config(show="")
        else:
            self.token_entry.config(show="*")
    
    def save_settings(self):
        """Save settings to config file"""
        try:
            # Update ERP settings
            self.config.set('erp.url', self.url_entry.get().strip())
            self.config.set('erp.token', self.token_entry.get().strip())
            self.config.set('erp.timeout', int(self.timeout_entry.get()))
            self.config.set('erp.retry_attempts', int(self.retry_attempts_entry.get()))
            self.config.set('erp.retry_delay', int(self.retry_delay_entry.get()))
            
            # Update serial settings
            self.config.set('serial.port', self.port_entry.get().strip())
            self.config.set('serial.baudrate', int(self.baudrate_combo.get()))
            self.config.set('serial.timeout', int(self.serial_timeout_entry.get()))
            
            # Update weighbridge settings
            self.config.set('weighbridge.id', self.wb_id_entry.get().strip())
            self.config.set('weighbridge.unit', self.unit_combo.get())
            self.config.set('weighbridge.precision', int(self.precision_spin.get()))
            
            # Update logging settings
            self.config.set('logging.level', self.log_level_combo.get())
            self.config.set('logging.file', self.log_file_entry.get().strip())
            
            # Update app settings
            self.config.set('app.auto_start', self.auto_start_var.get())
            
            # Save to file
            self.config.save_config()
            
            messagebox.showinfo("Success", "Settings saved successfully!\n\nRestart the application for changes to take effect.")
            
        except ValueError as e:
            messagebox.showerror("Validation Error", f"Invalid value: {e}")
        except ConfigurationError as e:
            messagebox.showerror("Configuration Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def test_connection(self):
        """Test connection to ERP endpoint"""
        # Temporarily update config for testing
        temp_url = self.url_entry.get().strip()
        temp_token = self.token_entry.get().strip()
        
        if not temp_url:
            messagebox.showwarning("Warning", "Please enter an API endpoint URL")
            return
        
        try:
            # Create temporary ERP client
            from erp_client import ERPClient
            
            # Temporarily update config
            original_url = self.config.get('erp.url')
            original_token = self.config.get('erp.token')
            
            self.config.set('erp.url', temp_url)
            self.config.set('erp.token', temp_token)
            
            # Test connection
            client = ERPClient()
            success, message = client.test_connection()
            client.close()
            
            # Restore original config
            self.config.set('erp.url', original_url)
            self.config.set('erp.token', original_token)
            
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showwarning("Connection Failed", message)
                
        except Exception as e:
            messagebox.showerror("Error", f"Connection test failed: {e}")
    

    
    def reset_defaults(self):
        """Reset configuration to defaults"""
        if messagebox.askyesno("Confirm Reset",
                               "Are you sure you want to reset all settings to defaults?\n\n"
                               "This action cannot be undone."):
            try:
                self.config.reset_to_defaults()
                messagebox.showinfo("Success", "Settings reset to defaults!")
                self.window.destroy()
                # Reopen settings window with default config
                SettingsWindow().run()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {e}")
    
    def run(self):
        """Run the settings window"""
        self.window.mainloop()


if __name__ == "__main__":
    try:
        app = SettingsWindow()
        app.run()
    except Exception as e:
        print(f"Error starting settings window: {e}")
        import traceback
        traceback.print_exc()
