import fabric
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.datetime import DateTime
from fabric.widgets.box import Box
from fabric.widgets.label import Label


def seperator(sep):
    return Label(
        label=sep,
    )


class Time(CenterBox):
    def __init__(
        self,
    ):
        super().__init__(
            orientation="v",
            name="clock",
            h_align="center",
            v_align="center",
        )

        self.hour = DateTime(formatters="%H")
        self.minute = DateTime(formatters="%M")
        self.second = DateTime(formatters="%S")
        self.start_children = [self.hour, seperator("-")]
        self.center_children = [self.minute, seperator("-")]
        self.end_children = [self.second]
