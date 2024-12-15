import time
import random
import threading
from queue import Queue
from Foundation import NSObject
from AppKit import NSEvent, NSApplication, NSKeyDown, NSCommandKeyMask, NSSystemDefined

class KeystrokeScrambler:
    def __init__(self, root=None):
        self.root = root
        self.key_buffer = Queue()
        self.last_key = None
        self.enabled = False
        self.base_delay = 0.1
        self.monitor = None
        self._initialize()

    def _initialize(self):
        """Initialize the monitor with proper error handling."""
        try:
            # Initialize NSApplication if not already running
            NSApplication.sharedApplication()
        except Exception as e:
            print(f"Failed to initialize NSApplication: {e}")
            raise

    def get_delay(self):
        """Calculate randomized delay."""
        import random
        base = 0.1
        variation = 0.02
        return base + random.uniform(-variation, variation)

    def _handle_event(self, event):
        """Handle keyboard event."""
        try:
            if not self.enabled:
                return event

            # Get key information
            characters = event.characters()
            if not characters:
                return event

            # Calculate delay
            delay = self.get_delay() * (self.base_delay / 0.1)

            # Schedule key press on main thread
            if self.root:
                self.root.after(int(delay * 1000), lambda: self._process_key(characters))

            return None  # Suppress original event
            
        except Exception as e:
            print(f"Error handling event: {e}")
            return event

    def _process_key(self, key):
        """Process a key press on the main thread."""
        try:
            if self.enabled:
                # Create and post a new key event
                event = NSEvent.keyEventWithType_location_modifierFlags_timestamp_windowNumber_context_characters_charactersIgnoringModifiers_isARepeat_keyCode_(
                    NSKeyDown,
                    (0, 0),
                    0,
                    NSEvent.timestamp(),
                    0,
                    None,
                    key,
                    key,
                    False,
                    0
                )
                NSApplication.sharedApplication().postEvent_atStart_(event, True)
        except Exception as e:
            print(f"Error processing key: {e}")

    def start(self):
        """Start the scrambler with improved error handling."""
        try:
            if self.enabled:
                return  # Already running

            # Start monitoring keyboard events
            mask = NSKeyDown
            self.monitor = NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
                mask,
                self._handle_event
            )
            
            self.enabled = True
            
        except Exception as e:
            self.enabled = False
            if self.monitor:
                NSEvent.removeMonitor_(self.monitor)
                self.monitor = None
            raise RuntimeError(f"Failed to start scrambler: {e}")

    def stop(self):
        """Stop the scrambler with improved error handling."""
        try:
            self.enabled = False
            if self.monitor:
                NSEvent.removeMonitor_(self.monitor)
                self.monitor = None
        except Exception as e:
            print(f"Error stopping scrambler: {e}")
