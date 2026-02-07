import os
import subprocess

from fabric.widgets.box import Box
from fabric.widgets.image import Image
from fabric.widgets.label import Label
from fabric.widgets.eventbox import EventBox
from services.mango import MangoService


class Layout(Box):
    def __init__(self, monitor="DP-3", use_icons=True, icon_size=24, **kwargs):
        self.service = MangoService(monitor=monitor)
        self.use_icons = use_icons
        self.icon_size = icon_size
        
        # Get the base directory (parent of modules/)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.icons_dir = os.path.join(self.base_dir, "assets", "layouts")
        
        # Layout abbreviation mapping (from mmsg) to SVG files
        self.layout_map = {
            "t": "tile.svg",
            "s": "scroller.svg",
            "m": "monocle.svg",
            "g": "grid.svg",
            "d": "deck.svg",
            "ct": "center_tile.svg",
            "vt": "vertical_tile.svg",
            "rt": "right_tile.svg",
            "vs": "vertical_scroller.svg",
            "vg": "vertical_grid.svg",
            "vd": "vertical_deck.svg",
            "tg": "tgmix.svg",
        }
        
        if self.use_icons:
            self.image = Image(
                image_file=self._get_icon_path(self.service.layout),
                pixel_size=self.icon_size,
                name="layout-image",
            )
            self.display_widget = self.image
        else:
            self.label = Label(
                label=self.service.layout or "Unknown",
                name="layout-label",
            )
            self.display_widget = self.label

        self.event_box = EventBox(
            child=self.display_widget,
            on_button_press_event=self.on_click,
            name="layout-eventbox",
        )

        super().__init__(
            name="layout",
            orientation="v",
            spacing=4,
            children=[self.event_box],
            **kwargs,
        )

        self.update_display()
        self.service.connect("layout-changed", self.update_display)
    
    def _get_icon_path(self, layout_name):
        """Get the full path to the layout icon SVG file."""
        if not layout_name:
            return None
        
        # Extract layout name (handle "monitor layout" format)
        if " " in layout_name:
            name = layout_name.split()[-1]
        else:
            name = layout_name
        
        # Convert to lowercase and get SVG filename
        layout_key = name.lower()
        svg_file = self.layout_map.get(layout_key)
        
        if svg_file:
            icon_path = os.path.join(self.icons_dir, svg_file)
            if os.path.exists(icon_path):
                return icon_path
        
        # Fallback to a default icon or None
        return None
    
    def update_display(self, *args):
        layout = self.service.layout or "Unknown"
        
        if self.use_icons:
            icon_path = self._get_icon_path(layout)
            if icon_path:
                self.image.set_from_file(icon_path)
        else:
            if " " in layout:
                name = layout.split()[-1]
            else:
                name = layout
            abbreviated = name[:2].upper() if name != "Unknown" else "UN"
            self.label.set_label(abbreviated)
        
        self.show_all()

    def on_click(self, eventbox):
        # Cycle to next layout (you can customize this command)
        cmd = ["mmsg"]
        if self.service.monitor:
            cmd.extend(["-o", self.service.monitor])
        cmd.extend(["-l", "next"])
        subprocess.run(cmd, check=False)
