import sys
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
from modules.media import MediaWidget
from modules.media import MEDIA_WIDGET
from modules.time import Time
from modules.date import Date
from modules.cpu import Cpu
from modules.gpu import Gpu
from modules.tags import Tags
from modules.layout import Layout
from modules.uptime import Uptime


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
            margin="9px 0px 9px 5px",
            exclusivity="auto",
            # h_align="center",
            visible=False,
        )

        self.children = CenterBox(
            name="bar-inner",
            orientation="v",
            h_align="center",
            start_children=Box(
                name="start-container",
                orientation="v",
                h_align="center",
                spacing=5,
                children=[
                    Layout(),
                    Tags(),
                ],
            ),
            center_children=Box(
                name="center-container",
                orientation="v",
                h_align="center",
                children=[
                    Cpu(),
                    Time(),
                    Gpu(),
                ],
            ),
            end_children=Box(
                name="end-container",
                spacing=8,
                orientation="v",
                h_align="center",
                children=[
                    MediaWidget() if MEDIA_WIDGET else None,
                    SystemTray(name="system-tray", spacing=4, orientation="v"),
                    VolumeWidget(),
                    Uptime(),
                ],
            ),
        )

        return self.show_all()


if __name__ == "__main__":
    monitor = 1
    bar = StatusBar(monitor)
    app = Application("mangobar", bar)
    app.set_stylesheet_from_file(get_relative_path("./style.css"))

    app.run()
