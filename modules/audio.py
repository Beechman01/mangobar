from fabric.core.fabricator import Fabricator
from fabric.widgets.box import Box
from fabric.widgets.image import Image
from fabric.widgets.overlay import Overlay
from fabric.widgets.eventbox import EventBox
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.label import Label

from widgets.animated_circular_progress_bar import AnimatedCircularProgressBar

AUDIO_WIDGET = True

if AUDIO_WIDGET is True:
    try:
        from fabric.audio.service import Audio
    except Exception as e:
        AUDIO_WIDGET = False
        print(e)


class VolumeWidget(Box):
    def __init__(self, **kwargs):
        self.label = Label(label="0%")

        self.progress_bar = AnimatedCircularProgressBar(
            name="volume-progress-bar",
            pie=False,
            child=self.label,
            size=34,
        )

        self.progress_back = CircularProgressBar(
            name="circle-progress-back",
            pie=False,
            size=34,
        )

        self.overlay = Overlay(
            child=self.progress_back,
            overlays=self.progress_bar,
        )

        self.audio = Audio(notify_speaker=self.on_speaker_changed)

        super().__init__(
            children=EventBox(
                events="scroll", child=self.overlay, on_scroll_event=self.on_scroll
            ),
            **kwargs,
        )

    def on_scroll(self, _, event):
        match event.direction:
            case 0:
                self.audio.speaker.volume += 8
            case 1:
                self.audio.speaker.volume -= 8
        return

    def on_speaker_changed(self):
        if not self.audio.speaker:
            return

        self.progress_bar.animate_value(self.audio.speaker.volume / 100)
        self.label.set_label(str(int(self.audio.speaker.volume)) + "%")
        self.audio.speaker.bind(
            "volume",
            "value",
            self.progress_bar,
            lambda _, v: self.progress_bar.animate_value(v / 100),
        )
        self.audio.speaker.bind(
            "volume",
            "label",
            self.label,
            lambda _, v: self.label.set_label(str(int(v)) + "%"),
        )
        return
