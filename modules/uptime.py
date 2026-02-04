import time
import psutil
from fabric.widgets.label import Label
from fabric.widgets.box import Box
from fabric import Fabricator


class Uptime(Box):
    def __init__(self, **kwargs):
        super().__init__(
            name="uptime",
            orientation="v",
            spacing=4,
            **kwargs,
        )

        self.days_label = Label(name="uptime-days")
        self.hours_label = Label(name="uptime-hours")
        self.minutes_label = Label(name="uptime-minutes")
        self.seconds_label = Label(name="uptime-seconds")

        self.children = [
            self.days_label,
            self.hours_label,
            self.minutes_label,
            self.seconds_label,
        ]

        # Update uptime every second
        self.fabricator = Fabricator(
            interval=1000,
            poll_from=lambda f: self.get_uptime(),
            on_changed=lambda _, value: self.update_display(value),
        )

    def get_uptime(self):
        """Get system uptime in seconds"""
        return time.time() - psutil.boot_time()

    def update_display(self, uptime_seconds):
        """Update display with formatted uptime"""
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)

        self.days_label.set_label(f"{days}d")
        self.hours_label.set_label(f"{hours:02d}h")
        self.minutes_label.set_label(f"{minutes:02d}m")
        self.seconds_label.set_label(f"{seconds:02d}s")
