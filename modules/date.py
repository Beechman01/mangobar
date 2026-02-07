import fabric
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.datetime import DateTime
from fabric.widgets.label import Label
import time


def seperator(sep):
    return Label(
        label=sep,
    )


class Date(CenterBox):
    def __init__(
        self,
    ):
        super().__init__(
            orientation="v",
        )
        self.day = DateTime(
            name="day",
            formatters="%d",
        )
        self.month = DateTime(
            name="month",
            formatters="%m",
        )
        self.year = DateTime(name="year", formatters="%y")
        self.start_children = [
            self.day,
            seperator("-"),
        ]
        self.center_children = [
            self.month,
            seperator("-"),
        ]
        self.end_children = [
            self.year,
        ]
