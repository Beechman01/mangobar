import os
import json
import gi

gi.require_version("GLib", "2.0")
gi.require_version("Gio", "2.0")
from gi.repository import GLib, GObject, Gio


class ThemeManager(GObject.Object):
    """Manages theme switching for MangoBar with persistence and keybind support."""

    __gsignals__ = {
        "theme-changed": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.current_theme = None
        self.available_themes = []

        # Get base directory (parent of services/)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.themes_dir = os.path.join(self.base_dir, "themes")

        # XDG config directory
        config_home = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        self.config_dir = os.path.join(config_home, "mangobar")
        self.config_path = os.path.join(self.config_dir, "config.json")

        # Ensure directories exist
        self._ensure_directories()

        # Scan available themes
        self.available_themes = self.get_available_themes()

        # Setup file monitor for keybind support
        self._setup_file_monitor()

    def _ensure_directories(self):
        """Ensure themes and config directories exist."""
        if not os.path.exists(self.themes_dir):
            os.makedirs(self.themes_dir, exist_ok=True)
            print(f"Created themes directory: {self.themes_dir}")

        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)
            print(f"Created config directory: {self.config_dir}")

    def get_available_themes(self):
        """Scan themes directory and return sorted list of theme names."""
        if not os.path.exists(self.themes_dir):
            print(f"Warning: Themes directory not found: {self.themes_dir}")
            return []

        themes = []
        for filename in os.listdir(self.themes_dir):
            if filename.endswith(".css"):
                theme_name = filename[:-4]  # Remove .css extension
                themes.append(theme_name)

        # Sort alphabetically
        themes.sort()

        if not themes:
            print(f"Warning: No themes found in {self.themes_dir}")

        return themes

    def load_theme(self, theme_name):
        """Load and apply a theme by name."""
        if theme_name not in self.available_themes:
            print(
                f"Warning: Theme '{theme_name}' not found. Using first available theme."
            )
            if not self.available_themes:
                print("Error: No themes available!")
                return False
            theme_name = self.available_themes[0]

        theme_path = os.path.join(self.themes_dir, f"{theme_name}.css")

        try:
            with open(theme_path, "r") as f:
                css_content = f.read()

            # Apply theme using Fabric's set_stylesheet_from_string
            self.app.set_stylesheet_from_string(css_content)

            # Update current theme
            old_theme = self.current_theme
            self.current_theme = theme_name

            print(f"Loaded theme: {theme_name}")

            # Emit signal if theme changed
            if old_theme != theme_name:
                self.emit("theme-changed", theme_name)

            return True

        except Exception as e:
            print(f"Error loading theme '{theme_name}': {e}")
            return False

    def next_theme(self):
        """Cycle to the next theme alphabetically."""
        if not self.available_themes:
            print("No themes available to switch")
            return

        if self.current_theme is None:
            # Load first theme
            next_theme = self.available_themes[0]
        else:
            try:
                current_index = self.available_themes.index(self.current_theme)
                next_index = (current_index + 1) % len(self.available_themes)
                next_theme = self.available_themes[next_index]
            except ValueError:
                # Current theme not in list, start from beginning
                next_theme = self.available_themes[0]

        self.load_theme(next_theme)
        self._save_config()

    def get_current_theme(self):
        """Return the name of the current theme."""
        return self.current_theme or "none"

    def _load_config(self):
        """Load configuration from config.json."""
        if not os.path.exists(self.config_path):
            # Return default config
            return {"theme": "tokyo-night-storm"}

        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"theme": "tokyo-night-storm"}

    def _save_config(self):
        """Save current theme to config.json."""
        config = {"theme": self.current_theme}

        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
            print(f"Saved theme preference: {self.current_theme}")
        except Exception as e:
            print(f"Error saving config: {e}")

    def load_saved_theme(self):
        """Load the theme saved in config file, or default if none."""
        config = self._load_config()
        theme_name = config.get("theme", "tokyo-night-storm")

        # If saved theme doesn't exist, use first available
        if theme_name not in self.available_themes and self.available_themes:
            theme_name = self.available_themes[0]

        self.load_theme(theme_name)

    def _setup_file_monitor(self):
        """Setup file monitor for keybind support via /tmp/mangobar-switch-theme."""
        trigger_path = "/tmp/mangobar-switch-theme"

        # Clean up leftover trigger file from previous session
        if os.path.exists(trigger_path):
            try:
                os.remove(trigger_path)
            except Exception:
                pass

        # Use GLib timeout to poll for file existence
        # This is simpler than Gio.File monitoring which can be unreliable with tmpfs
        def check_trigger():
            if os.path.exists(trigger_path):
                try:
                    os.remove(trigger_path)
                    self.next_theme()
                    print("Theme switched via keybind trigger")
                except Exception as e:
                    print(f"Error processing keybind trigger: {e}")
            return True  # Continue polling

        # Poll every 500ms for the trigger file
        GLib.timeout_add(500, check_trigger)
        print(f"File monitor active: {trigger_path}")
