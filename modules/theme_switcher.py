from fabric.widgets.eventbox import EventBox
from fabric.widgets.label import Label


class ThemeSwitcher(EventBox):
    """Widget to switch between themes via button click."""

    def __init__(self, theme_manager, icon="", **kwargs):
        self.theme_manager = theme_manager

        self.label = Label(label=icon, name="theme-switcher-label")

        super().__init__(
            name="theme-switcher",
            child=self.label,
            on_button_press_event=self.on_click,
            tooltip_text=self._format_tooltip(theme_manager.get_current_theme()),
            **kwargs,
        )

        # Update tooltip when theme changes
        self.theme_manager.connect("theme-changed", self.on_theme_changed)

    def _format_tooltip(self, theme_name):
        """Format theme name for display in tooltip."""
        # Convert "tokyo-night-storm" to "Tokyo Night Storm"
        formatted = theme_name.replace("-", " ").title()
        return f"Theme: {formatted}"

    def on_click(self, widget, event):
        """Handle click event to cycle to next theme."""
        self.theme_manager.next_theme()

    def on_theme_changed(self, manager, theme_name):
        """Update tooltip when theme changes."""
        self.set_tooltip_text(self._format_tooltip(theme_name))
