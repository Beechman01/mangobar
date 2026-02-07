from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.system_tray.widgets import SystemTray
from fabric.widgets.wayland import WaylandWindow as Window

from modules.audio import VolumeWidget
from modules.media import MediaWidget
from modules.media import MEDIA_WIDGET
from modules.time import Time
from modules.cpu import Cpu
from modules.gpu import Gpu
from modules.tags import Tags
from modules.layout import Layout
from modules.uptime import Uptime
from modules.theme_switcher import ThemeSwitcher
from services.theme_manager import ThemeManager


class StatusBar(Window):
    def __init__(
        self,
        monitor,
        theme_manager,
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
                    # Icon options: 󰏘 󰌁   󰃟  󰔎  󰌆 
                    ThemeSwitcher(theme_manager, icon="󰏘"),
                    Uptime(),
                ],
            ),
        )

        return self.show_all()


if __name__ == "__main__":
    monitor = 1
    app = Application("mangobar")

    # Create ThemeManager before StatusBar
    theme_manager = ThemeManager(app)

    # Create StatusBar with theme_manager
    bar = StatusBar(monitor, theme_manager)

    # Load saved theme (or default)
    theme_manager.load_saved_theme()

    app.run()
