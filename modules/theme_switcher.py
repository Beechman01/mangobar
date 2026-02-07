import os
import tempfile
from fabric.widgets.eventbox import EventBox
from fabric.widgets.image import Image


class ThemeSwitcher(EventBox):
    """Widget to switch between themes via button click."""

    # Theme color mapping for icon
    THEME_COLORS = {
        "tokyo-night-storm": "#9d7cd8",
        "dracula": "#bd93f9",
        "nord": "#81a1c1",
        "catppuccin-mocha": "#cba6f7",
        "gruvbox": "#d3869b",
    }

    def __init__(self, theme_manager, icon_size=32, **kwargs):
        self.theme_manager = theme_manager
        self.icon_size = icon_size

        # Get the base directory and icon path
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.icon_template_path = os.path.join(
            self.base_dir, "assets", "icons", "theme-switcher.svg"
        )

        # Create temp directory for colored icon
        self.temp_dir = tempfile.mkdtemp(prefix="mangobar_")
        self.colored_icon_path = os.path.join(
            self.temp_dir, "theme-switcher-colored.svg"
        )

        # Create initial colored icon
        self._update_icon_color(theme_manager.get_current_theme())

        self.image = Image(
            image_file=self.colored_icon_path,
            pixel_size=self.icon_size,
            name="theme-switcher-image",
        )

        super().__init__(
            name="theme-switcher",
            child=self.image,
            on_button_press_event=self.on_click,
            tooltip_text=self._format_tooltip(theme_manager.get_current_theme()),
            **kwargs,
        )

        # Update tooltip and icon when theme changes
        self.theme_manager.connect("theme-changed", self.on_theme_changed)

    def _update_icon_color(self, theme_name):
        """Update the icon color based on the current theme."""
        # Get color for this theme (default to purple if theme not in map)
        color = self.THEME_COLORS.get(theme_name, "#9d7cd8")

        # Read template SVG
        try:
            with open(self.icon_template_path, "r") as f:
                svg_content = f.read()

            # Replace currentColor with actual theme color
            colored_svg = svg_content.replace("currentColor", color)

            # Write colored SVG to temp file
            with open(self.colored_icon_path, "w") as f:
                f.write(colored_svg)

        except Exception as e:
            print(f"Error updating icon color: {e}")

    def _format_tooltip(self, theme_name):
        """Format theme name for display in tooltip."""
        # Convert "tokyo-night-storm" to "Tokyo Night Storm"
        formatted = theme_name.replace("-", " ").title()
        return f"Theme: {formatted}"

    def on_click(self, widget, event):
        """Handle click event to cycle to next theme."""
        self.theme_manager.next_theme()

    def on_theme_changed(self, manager, theme_name):
        """Update tooltip and icon color when theme changes."""
        self.set_tooltip_text(self._format_tooltip(theme_name))

        # Update icon color
        self._update_icon_color(theme_name)

        # Reload the image
        self.image.set_from_file(self.colored_icon_path)
