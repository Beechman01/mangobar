import psutil
from fabric import Application, Fabricator
from fabric.widgets.box import Box
from fabric.widgets.image import Image
from fabric.widgets.eventbox import EventBox
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.system_tray.widgets import SystemTray
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import FormattedString, get_relative_path, bulk_replace

from modules.audio import VolumeWidget
from modules.audio import AUDIO_WIDGET
from modules.time import Time
from modules.date import Date
from modules.cpu import Cpu
from modules.gpu import Gpu
from modules.tags import Tags


class StatusBar(Window):
    def __init__(
        self,
        monitor,
    ):
        super().__init__(
            name="mangobar",
            layer="top",
            monitor=monitor,
            title="MangoBar",
            anchor="top left bottom",
            margin="10px 10px 10px 10px",
            exclusivity="auto",
            # h_align="center",
            visible=False,
        )

        self.system_status = Box(
            name="system-status",
            spacing=4,
            orientation="v",
            children=[
            ]
        )

        self.children = CenterBox(
            name="bar-inner",
            orientation="v",
            h_align="center",
            start_children=Box(
                name="start-container",
                orientation="v",
                h_align="center",
                children=[
                    Tags(),
                ]
            ),
            center_children=Box(
                name="center-container",
                orientation="v",
                h_align="center",
                children=[
                    Cpu(),
                    Time(),
                    Gpu(),
                    # Date()
                ]
            ),
            end_children=Box(
                name="end-container",
                spacing=4,
                orientation="v",
                h_align="center",
                children=[
                    SystemTray(name="system-tray", spacing=4),
                    self.system_status,
                    VolumeWidget(),
               ],
            ),
        )

        return self.show_all()


if __name__ == "__main__":
    bar = StatusBar(1)
    app = Application("mangobar", bar)
    app.set_stylesheet_from_file(get_relative_path("./style.css"))

    app.run()
