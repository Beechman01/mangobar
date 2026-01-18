import fabric
import psutil
from fabric.widgets.label import Label
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.overlay import Overlay
from fabric import Fabricator



class Cpu(Box):
    def __init__(
        self,
    ):
        super().__init__(
            name="cpu",
            orientation="v",
            h_align="center",
            v_align="center",
        )

        self.title = CenterBox(
            orientation="v",
            start_children=[
                Label(
                    label="---"
                )
            ],
            center_children=[
                Label(
                    label="CPU"
                )
            ],
            end_children=[
                Label(
                    label="---"
                )
            ]
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
                        CircularProgressBar(
                            name="cpu-progress-bar",
                            pie=False,
                            size=34,
                            line_width=4,
                            child=Label(
                                name="cpu",
                            ).build(
                                lambda progress: Fabricator(
                                    interval=1000,
                                    poll_from=lambda f: psutil.cpu_percent(),
                                    on_changed=lambda _, value: progress.set_label(f"{str(int(value))}%"),
                                )
                            )
                        ).build(
                            lambda progress: Fabricator(
                                interval=1000,
                                poll_from=lambda f: psutil.cpu_percent()/100,
                                on_changed=lambda _, value: progress.set_value(value),
                            )
                        )
                    ]
                )
            ]
        )

        self.ram = Box(
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
                        CircularProgressBar(
                            name="ram-progress-bar",
                            pie=False,
                            size=34,
                            line_width=4,
                            child=Label(
                                name="ram",
                            ).build(
                                lambda progress: Fabricator(
                                    interval=1000,
                                    poll_from=lambda f: psutil.virtual_memory().percent,
                                    on_changed=lambda _, value: progress.set_label(f"{str(int(value))}%"),
                                )
                            )
                        ).build(
                            lambda progress: Fabricator(
                                interval=1000,
                                poll_from=lambda f: psutil.virtual_memory().percent/100,
                                on_changed=lambda _, value: progress.set_value(value),
                            )
                        )
                    ]
                )
            ]
        )

        self.children = Box(
            orientation="v",
            children=[
                self.ram,
                self.usage,
                self.title,
            ]
        )
