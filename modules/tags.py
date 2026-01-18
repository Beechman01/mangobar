from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.eventbox import EventBox
from services.mango import MangoService
import subprocess

class Tags(Box):
    def __init__(self, monitor="DP-3", **kwargs):
        self.service = MangoService(monitor=monitor)
        self.buttons = []

        super().__init__(
            orientation="v",
            spacing=4,
            **kwargs
        )

        self.update_buttons()
        self.service.connect(
            'tags-changed',
            self.update_buttons
        )

    def update_buttons(self, *args):
        # clear existing
        for child in self.get_children():
            self.remove(child)

        self.buttons = []
        for i in self.service.available_tags:
            btn = Button(
                label="",
                name="tag-button",
                on_clicked=self.on_tag_click,
                tooltip_text=f"Tag {i}"
            )
            btn.tag_num = i
            self.buttons.append(btn)
            self.add(btn)

        self.update_styles()

    def update_styles(self):
        for i, btn in enumerate(self.buttons, 1):
            btn.remove_style_class("active")
            btn.remove_style_class("occupied")
            if i in self.service.active_tags:
                btn.add_style_class("active")
            if i in self.service.occupied_tags:
                btn.add_style_class("occupied")

        self.show_all()

    def on_tag_click(self, btn):
        tag_num = btn.tag_num
        # switch to tag
        cmd = ['mmsg']
        if self.service.monitor:
            cmd.extend(['-o', self.service.monitor])
        cmd.extend(['-t', str(tag_num)])
        subprocess.run(cmd, check=False)
