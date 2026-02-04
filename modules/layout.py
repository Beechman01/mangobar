from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.eventbox import EventBox
from services.mango import MangoService
import subprocess


class Layout(Box):
    def __init__(self, monitor="DP-3", **kwargs):
        self.service = MangoService(monitor=monitor)
        self.label = Label(
            label=self.service.layout or "Unknown",
            name="layout-label",
        )

        self.event_box = EventBox(
            child=self.label,
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

        self.update_label()
        self.service.connect("layout-changed", self.update_label)

    def update_label(self, *args):
        layout = self.service.layout or "Unknown"
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
