import fabric
from fabric.widgets.box import Box
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.overlay import Overlay
from fabric.widgets.label import Label
from fabric import Fabricator
from widgets.animated_circular_progress_bar import AnimatedCircularProgressBar
from pynvml import (
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetUtilizationRates,
    nvmlDeviceGetTemperature,
    nvmlInit,
    nvmlShutdown,
)


class Gpu(Box):
    def __init__(
        self,
    ):
        super().__init__(
            name="gpu",
            orientation="v",
            h_align="center",
            v_align="center",
        )

        self.title = CenterBox(
            orientation="v",
            start_children=[Label(label="---")],
            center_children=[Label(label="GPU")],
            end_children=[Label(label="---")],
        )

        self.usage = Box(
            orientation="v",
            children=[
                Overlay(
                    child=[
                        CircularProgressBar(
                            name="circle-progress-back",
                            pie=False,
                            size=34,
                            line_width=4,
                            value=100,
                        ),
                    ],
                    overlays=[
                        AnimatedCircularProgressBar(
                            name="gpu-progress-bar",
                            pie=False,
                            size=34,
                            line_width=4,
                            child=Label(
                                name="gpu",
                            ).build(
                                lambda progress: Fabricator(
                                    interval=1000,
                                    poll_from=lambda f: self.getGpuPercent(),
                                    on_changed=lambda _, value: progress.set_label(
                                        f"{str(int(value))}%"
                                    ),
                                )
                            ),
                        ).build(
                            lambda progress: Fabricator(
                                interval=1000,
                                poll_from=lambda f: int(self.getGpuPercent()) / 100,
                                on_changed=lambda _, value: progress.animate_value(
                                    value
                                ),
                            )
                        )
                    ],
                )
            ],
        )

        self.vram = Box(
            orientation="v",
            children=[
                Overlay(
                    child=[
                        CircularProgressBar(
                            name="circle-progress-back",
                            pie=False,
                            size=34,
                            line_width=4,
                            value=100,
                        ),
                    ],
                    overlays=[
                        AnimatedCircularProgressBar(
                            name="vram-progress-bar",
                            pie=False,
                            size=34,
                            line_width=4,
                            child=Label(
                                name="vram",
                            ).build(
                                lambda progress: Fabricator(
                                    interval=1000,
                                    poll_from=lambda f: self.getVramPercent(),
                                    on_changed=lambda _, value: progress.set_label(
                                        f"{str(int(value))}%"
                                    ),
                                )
                            ),
                        ).build(
                            lambda progress: Fabricator(
                                interval=1000,
                                poll_from=lambda f: int(self.getVramPercent()) / 100,
                                on_changed=lambda _, value: progress.animate_value(
                                    value
                                ),
                            )
                        )
                    ],
                )
            ],
        )

        self.temp = Label(
            name="temp",
        ).build(
            lambda temp: Fabricator(
                interval=1000,
                poll_from=lambda f: self.getGpuTemp(),
                on_changed=lambda _, value: temp.set_label(f"{str(value)}°C"),
            )
        )

        self.children = Box(
            orientation="v",
            spacing=8,
            children=[
                self.title,
                self.temp,
                self.usage,
                self.vram,
            ],
        )

    def getGpuPercent(self):
        nvmlInit()
        handle = nvmlDeviceGetHandleByIndex(0)
        usage = nvmlDeviceGetUtilizationRates(handle)

        # print(usage.gpu)
        nvmlShutdown()
        return usage.gpu

    def getVramPercent(self):
        nvmlInit()
        handle = nvmlDeviceGetHandleByIndex(0)
        usage = nvmlDeviceGetUtilizationRates(handle)

        # print(usage.memory)
        nvmlShutdown()
        return usage.memory

    def getGpuTemp(self):
        nvmlInit()
        handle = nvmlDeviceGetHandleByIndex(0)
        temp = nvmlDeviceGetTemperature(handle, 0)

        # print(temp)
        nvmlShutdown()
        return str(temp)
