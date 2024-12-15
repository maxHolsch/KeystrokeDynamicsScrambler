import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import subprocess
import time
import platform
import logging
from typing import Optional, Tuple
from keystroke_core import KeystrokeScrambler

# Set up logging
logging.basicConfig(
    filename=os.path.expanduser('~/keystroke_scrambler.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def exception_handler(exc_type, exc_value, exc_traceback):
    """Global exception handler to log unhandled exceptions"""
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.__excepthook__(exc_type, exc_value, exc_traceback)  # Call the default handler

sys.excepthook = exception_handler

class PermissionManager:
    """Handles macOS permissions for accessibility and input monitoring."""
    
    @staticmethod
    def get_app_path() -> str:
        """Get the path to the current application or script."""
        try:
            if getattr(sys, 'frozen', False) or os.environ.get('RUNNING_AS_APP'):
                app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                logging.debug(f"App path (frozen): {app_path}")
                if app_path.endswith('.app'):
                    return app_path
            script_path = os.path.abspath(__file__)
            logging.debug(f"Script path: {script_path}")
            return script_path
        except Exception as e:
            logging.error(f"Error getting app path: {e}")
            return os.path.abspath(__file__)

    @staticmethod
    def check_permission(permission_type: str) -> bool:
        """Check if a specific permission is granted by attempting to use the functionality."""
        try:
            from pynput import keyboard
            # Create a temporary keyboard listener to test permissions
            if permission_type in ['accessibility', 'input']:
                logging.debug(f"Testing {permission_type} permission...")
                test_listener = keyboard.Listener(on_press=lambda key: None)
                test_listener.start()
                time.sleep(0.1)  # Give it a moment to start
                is_running = test_listener.is_alive()
                test_listener.stop()
                logging.debug(f"Permission test result: {is_running}")
                return is_running
            return False
        except Exception as e:
            logging.error(f"Error checking {permission_type} permission: {e}")
            return False

    @classmethod
    def check_all_permissions(cls) -> Tuple[bool, bool]:
        """Check both accessibility and input monitoring permissions."""
        logging.debug("Checking all permissions...")
        permission_granted = cls.check_permission('input')
        logging.debug(f"All permissions check result: {permission_granted}")
        return permission_granted, permission_granted

    @staticmethod
    def request_permissions() -> bool:
        """Show instructions for enabling required permissions."""
        logging.debug("Requesting permissions...")
        msg = """This application requires both Accessibility and Input Monitoring permissions.

Please follow these steps:
1. Open System Preferences
2. Go to Security & Privacy > Privacy
3. Enable permissions for:
   - Accessibility
   - Input Monitoring
4. Look for and enable KeystrokeScrambler in both sections

Would you like to open System Preferences now?"""
        
        if messagebox.askyesno("Permissions Required", msg):
            try:
                subprocess.run(['open', 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'])
                time.sleep(1)
                subprocess.run(['open', 'x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent'])
                return True
            except Exception as e:
                logging.error(f"Error opening System Preferences: {e}")
                return False
        return False

class CustomSlider(ttk.Scale):
    """Custom slider widget with value display."""
    
    def __init__(self, master, **kwargs):
        self.value_var = tk.StringVar()
        super().__init__(master, **kwargs)
        self.value_label = ttk.Label(master, textvariable=self.value_var, style="Value.TLabel")
        self.value_label.pack()
        self.bind("<Motion>", self._update_value_label)
        self._update_value_label()

    def _update_value_label(self, _event=None):
        """Update the displayed value label."""
        try:
            value = self.get()
            self.value_var.set(f"{value:.0f} ms")
        except Exception as e:
            logging.error(f"Error updating slider value: {e}")

class StatusIndicator(ttk.Frame):
    """Status indicator widget showing the current state of the scrambler."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.label = ttk.Label(
            self,
            text="Inactive",
            padding=10,
            style="Status.TLabel"
        )
        self.label.pack()

    def update_status(self, active: bool, error: Optional[str] = None):
        """Update the status display."""
        try:
            if error:
                self.label.config(text=f"Error: {error}", style="Error.TLabel")
            else:
                status = "Active: Scrambling enabled" if active else "Inactive: Normal typing"
                style = "Active.TLabel" if active else "Inactive.TLabel"
                self.label.config(text=status, style=style)
        except Exception as e:
            logging.error(f"Error updating status: {e}")

class ScramblerGUI:
    """Main GUI application for the Keystroke Scrambler."""
    
    def __init__(self):
        logging.debug("Initializing ScramblerGUI...")
        
        if platform.system() != 'Darwin':
            logging.error("Unsupported platform")
            messagebox.showerror("Unsupported Platform", 
                               "This application is currently only supported on macOS")
            sys.exit(1)

        try:
            self.root = tk.Tk()
            self.root.title("Keystroke Scrambler")
            self.root.geometry("400x550")
            self.root.configure(bg="#f0f0f0")
            
            self._setup_styles()
            
            # Check permissions before initializing
            if not self._check_and_request_permissions():
                logging.warning("Permission check failed")
                self.root.destroy()
                sys.exit(1)
                
            try:
                self.scrambler = KeystrokeScrambler()
            except Exception as e:
                logging.error(f"Failed to initialize scrambler: {e}")
                messagebox.showerror("Initialization Error", 
                                   f"Failed to initialize scrambler: {e}")
                self.root.destroy()
                sys.exit(1)
                
            self._setup_gui()
            self._setup_keybindings()
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
        except Exception as e:
            logging.error(f"Error in ScramblerGUI initialization: {e}", exc_info=True)
            raise

    def _setup_styles(self):
        """Set up custom styles for the GUI."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TButton", background="#4a86e8", foreground="white", font=("Arial", 10, "bold"))
        self.style.map("TButton", background=[("active", "#3a76d8")])
        
        self.style.configure("Header.TLabel", font=("Arial", 18, "bold"), foreground="#333333")
        self.style.configure("Subheader.TLabel", font=("Arial", 12), foreground="#666666")
        
        self.style.configure("TCheckbutton", background="#f0f0f0", font=("Arial", 10))
        self.style.map("TCheckbutton", background=[("active", "#e0e0e0")])
        
        self.style.configure("TScale", background="#f0f0f0", troughcolor="#d0d0d0", sliderlength=20)
        self.style.configure("Value.TLabel", font=("Arial", 9), foreground="#666666")
        
        self.style.configure("Status.TLabel", font=("Arial", 12, "bold"), padding=10)
        self.style.configure("Active.TLabel", foreground="#4caf50")
        self.style.configure("Inactive.TLabel", foreground="#f44336")
        self.style.configure("Error.TLabel", foreground="#f44336")

    def _check_and_request_permissions(self) -> bool:
        """Check and request all necessary permissions."""
        try:
            # First attempt to check permissions
            accessibility, input_monitoring = PermissionManager.check_all_permissions()
            if accessibility and input_monitoring:
                logging.debug("All permissions already granted")
                return True
                
            # If permissions aren't granted, show the request dialog
            if not PermissionManager.request_permissions():
                logging.debug("User declined to request permissions")
                return False
                
            # Give user a chance to enable permissions
            response = messagebox.askquestion(
                "Permissions Check",
                "Please enable both Accessibility and Input Monitoring permissions, then click 'Yes' to continue.\n\n" +
                "Click 'No' to exit the application."
            )
            
            if response != 'yes':
                logging.debug("User declined to continue after permission request")
                return False
                
            # Final check after user claims to have enabled permissions
            accessibility, input_monitoring = PermissionManager.check_all_permissions()
            if not (accessibility and input_monitoring):
                logging.warning("Permissions still not granted after user confirmation")
                messagebox.showerror(
                    "Permission Error",
                    "Required permissions are still not enabled. Please restart the application after enabling permissions."
                )
                return False
                
            logging.debug("All permissions successfully granted")
            return True
            
        except Exception as e:
            logging.error(f"Error in permission check: {e}", exc_info=True)
            return False

    def _setup_gui(self):
        """Set up the GUI elements."""
        try:
            # Title and description
            self._create_header()
            
            # Control section
            self._create_controls()
            
            # Settings section
            self._create_settings()
            
            # Status section
            self._create_status()
            
            # Help section
            self._create_help()
            
        except Exception as e:
            logging.error(f"Error setting up GUI: {e}", exc_info=True)
            raise

    def _create_header(self):
        """Create the header section with title and description."""
        try:
            header_frame = ttk.Frame(self.root)
            header_frame.pack(pady=20, padx=20)
            
            title = ttk.Label(
                header_frame,
                text="⌨️ Keystroke Scrambler",
                style="Header.TLabel"
            )
            title.pack()
            
            description = ttk.Label(
                header_frame,
                text="Protect your typing patterns by randomizing keystroke timing",
                wraplength=350,
                justify='center',
                style="Subheader.TLabel"
            )
            description.pack(pady=10)
        except Exception as e:
            logging.error(f"Error creating header: {e}")
            raise

    def _create_controls(self):
        """Create the main control section."""
        try:
            control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
            control_frame.pack(pady=10, padx=20, fill='x')
            
            self.enabled_var = tk.BooleanVar()
            self.toggle_button = ttk.Checkbutton(
                control_frame,
                text="Enable Scrambling",
                variable=self.enabled_var,
                command=self._toggle_scrambler,
                style="TCheckbutton"
            )
            self.toggle_button.pack(pady=5)
        except Exception as e:
            logging.error(f"Error creating controls: {e}")
            raise

    def _create_settings(self):
        """Create the settings section."""
        try:
            settings_frame = ttk.LabelFrame(self.root, text="Settings", padding=10)
            settings_frame.pack(pady=10, padx=20, fill='x')
            
            # Base delay slider
            ttk.Label(settings_frame, text="Base Delay:").pack()
            self.delay_var = tk.DoubleVar(value=100)
            self.delay_slider = CustomSlider(
                settings_frame,
                from_=50,
                to=200,
                variable=self.delay_var,
                orient='horizontal',
                command=self._update_delay
            )
            self.delay_slider.pack(fill='x', pady=5)
        except Exception as e:
            logging.error(f"Error creating settings: {e}")
            raise

    def _create_status(self):
        """Create the status section."""
        try:
            self.status_indicator = StatusIndicator(self.root)
            self.status_indicator.pack(pady=20, padx=20, fill='x')
        except Exception as e:
            logging.error(f"Error creating status: {e}")
            raise

    def _create_help(self):
        """Create the help section."""
        try:
            help_frame = ttk.Frame(self.root)
            help_frame.pack(pady=20, padx=20, fill='x')
            
            ttk.Label(
                help_frame,
                text="Shortcut: Press Cmd+Shift+S to toggle scrambling",
                justify='center',
                font=('Arial', 9)
            ).pack()
        except Exception as e:
            logging.error(f"Error creating help: {e}")
            raise

    def _setup_keybindings(self):
        """Set up keyboard shortcuts."""
        try:
            self.root.bind('<Command-Shift-S>', lambda e: self._toggle_scrambler())
        except Exception as e:
            logging.error(f"Error setting up keybindings: {e}")
            raise

    def _toggle_scrambler(self):
        """Toggle the scrambler on/off."""
        try:
            if self.enabled_var.get():
                self.scrambler.start()
                self.status_indicator.update_status(True)
                self._animate_toggle(True)
            else:
                self.scrambler.stop()
                self.status_indicator.update_status(False)
                self._animate_toggle(False)
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error toggling scrambler: {error_msg}")
            messagebox.showerror("Error", error_msg)
            self.enabled_var.set(False)
            self.status_indicator.update_status(False, error_msg)

    def _animate_toggle(self, enabled):
        """Animate the toggle button color change."""
        def _animate(alpha):
            if enabled:
                color = f"#{int(74 * alpha):02x}{int(134 * alpha):02x}{int(232 * alpha):02x}"
            else:
                color = f"#{int(244 * (1-alpha)):02x}{int(67 * (1-alpha)):02x}{int(54 * (1-alpha)):02x}"
            self.toggle_button.configure(style=f"Animated.TCheckbutton")
            self.style.configure(f"Animated.TCheckbutton", background=color)
            
            if (enabled and alpha < 1) or (not enabled and alpha > 0):
                alpha = min(1, alpha + 0.1) if enabled else max(0, alpha - 0.1)
                self.root.after(20, lambda: _animate(alpha))
        
        _animate(0 if enabled else 1)

    def _update_delay(self, *args):
        """Update the scrambler's base delay."""
        try:
            self.scrambler.base_delay = self.delay_var.get() / 1000
        except Exception as e:
            logging.error(f"Error updating delay: {e}")

    def _on_closing(self):
        """Handle window closing event."""
        try:
            if self.scrambler:
                self.scrambler.stop()
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
        finally:
            self.root.destroy()

    def run(self):
        """Start the GUI application."""
        try:
            logging.info("Starting main application loop")
            self.root.mainloop()
        except Exception as e:
            logging.error(f"Error in main loop: {e}", exc_info=True)
            messagebox.showerror("Error", f"Application error: {str(e)}")
        finally:
            try:
                if self.scrambler:
                    self.scrambler.stop()
            except Exception as e:
                logging.error(f"Error during final cleanup: {e}")

def main():
    """Main entry point for the application."""
    try:
        logging.info("Starting application...")
        app = ScramblerGUI()
        app.run()
    except Exception as e:
        logging.error(f"Failed to start application: {e}", exc_info=True)
        messagebox.showerror("Error", f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

