import os

import gi
from fabric.core.fabricator import Fabricator
from fabric.widgets.box import Box
from fabric.widgets.image import Image
from fabric.widgets.overlay import Overlay
from fabric.widgets.eventbox import EventBox
from fabric.widgets.circularprogressbar import CircularProgressBar

from widgets.animated_circular_progress_bar import AnimatedCircularProgressBar

gi.require_version("Playerctl", "2.0")

MEDIA_WIDGET = True

try:
    from gi.repository import Playerctl

    test_manager = Playerctl.PlayerManager()
except Exception as e:
    MEDIA_WIDGET = False
    print(f"Playerctl not available: {e}")


class MediaWidget(Box):
    def __init__(self, **kwargs):
        self.progress_bar = AnimatedCircularProgressBar(
            name="media-progress-bar",
            pie=False,
            size=34,
        )

        self.progress_back = CircularProgressBar(
            name="circle-progress-back",
            pie=False,
            size=34,
            value=100,
        )

        self.thumbnail = Image(
            name="media-thumbnail",
            icon_name="multimedia-player",
            icon_size=34,
        )

        self.status_icon = Image(
            name="media-status-icon",
            icon_name="media-playback-stop",
            icon_size=12,
        )

        self.overlay = Overlay(
            child=self.thumbnail,
            overlays=[self.progress_back, self.progress_bar, self.status_icon],
        )

        self.player = None
        self.manager = None

        super().__init__(
            name="media-widget",
            children=EventBox(
                events="button-press",
                child=self.overlay,
                on_button_press_event=self.on_click,
            ),
            visible=False,
            **kwargs,
        )

        self.fabricator = Fabricator(
            interval=1000,
            poll_from=lambda f: self.update_position(),
        )

        self.setup_manager()

    def setup_manager(self):
        try:
            self.manager = Playerctl.PlayerManager()
            self.manager.connect("name-appeared", self.on_player_appeared)
            self.manager.connect("player-vanished", self.on_player_vanished)

            # Check for existing Spotify players
            for player_name in self.manager.props.player_names:
                if "spotify" in player_name.name.lower():
                    self.init_player(player_name)
        except Exception as e:
            print(f"Error setting up PlayerManager: {e}")

    def on_player_appeared(self, manager, player_name):
        # Only accept Spotify players
        if "spotify" not in player_name.name.lower():
            print(f"Ignoring non-Spotify player: {player_name.name}")
            return
        print(f"Spotify player appeared: {player_name.name}")
        self.init_player(player_name)

    def on_player_vanished(self, manager, player):
        # Only care about Spotify players
        if "spotify" not in player.props.player_name.lower():
            return
        print(f"Spotify player vanished: {player.props.player_name}")
        if self.player == player:
            self.player = None
            self.set_visible(False)

    def init_player(self, player_name):
        try:
            # Double-check this is Spotify
            if "spotify" not in player_name.name.lower():
                return

            player = Playerctl.Player.new_from_name(player_name)
            player.connect("metadata", self.on_metadata_changed)
            player.connect("playback-status", self.on_status_changed)
            player.connect("exit", self.on_player_exit)

            # Set as active player if we don't have one
            if self.player is None:
                self.player = player
                self.update_all()
                print(f"Initialized Spotify player: {player.props.player_name}")
        except Exception as e:
            print(f"Error initializing player: {e}")

    def on_metadata_changed(self, player, metadata):
        if player != self.player:
            return
        self.update_thumbnail()
        self.update_position()

    def on_status_changed(self, player, status):
        if player != self.player:
            return
        try:
            is_running = self.player is not None
            self.set_visible(is_running)
            self.update_status_icon(status)
        except Exception as e:
            print(f"Error in status change handler: {e}")

    def on_player_exit(self, player):
        if player == self.player:
            print(f"Player exited: {player.props.player_name}")
            self.set_visible(False)
            self.player = None

    def on_click(self, widget, event):
        if self.player:
            try:
                self.player.play_pause()
            except Exception as e:
                print(f"Error toggling playback: {e}")

    def update_position(self):
        if not self.player:
            return

        try:
            metadata = self.player.props.metadata
            if not metadata:
                return

            position = self.player.get_position()
            length = (
                metadata["mpris:length"] if "mpris:length" in metadata.keys() else None
            )

            if length and length > 0:
                progress = position / length
                self.progress_bar.animate_value(progress)

            status = self.player.props.status
            is_running = self.player is not None
            if self.get_visible() != is_running:
                self.set_visible(is_running)
            self.update_status_icon(status)
        except Exception as e:
            print(f"Error updating position: {e}")

    def update_thumbnail(self):
        if not self.player:
            return

        try:
            metadata = self.player.props.metadata
            if not metadata:
                return

            art_url = (
                metadata["mpris:artUrl"] if "mpris:artUrl" in metadata.keys() else None
            )

            if art_url:
                art_url_str = str(art_url)
                # Handle local files
                if art_url_str.startswith("file://"):
                    art_path = art_url_str.replace("file://", "")
                    if os.path.exists(art_path):
                        self.thumbnail.set_from_file(art_path)
                        return
                # Handle remote URLs (http/https)
                elif art_url_str.startswith("http://") or art_url_str.startswith(
                    "https://"
                ):
                    # GTK Image can load from URIs directly
                    self.thumbnail.set_from_pixbuf(None)  # Clear old image
                    # Use fabric's Image widget to load from URL
                    try:
                        import urllib.request
                        import tempfile
                        from gi.repository import GdkPixbuf

                        # Download and cache the image
                        with urllib.request.urlopen(art_url_str) as response:
                            with tempfile.NamedTemporaryFile(
                                delete=False, suffix=".jpg"
                            ) as tmp_file:
                                tmp_file.write(response.read())
                                tmp_path = tmp_file.name

                        # Load the pixbuf and scale it
                        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                            tmp_path, 34, 34
                        )
                        self.thumbnail.set_from_pixbuf(pixbuf)
                        os.unlink(tmp_path)  # Clean up temp file
                        return
                    except Exception as e:
                        print(f"Error loading remote album art: {e}")

            self.thumbnail.set_from_icon_name("multimedia-player", 34)
        except Exception as e:
            print(f"Error updating thumbnail: {e}")
            self.thumbnail.set_from_icon_name("multimedia-player", 34)

    def update_status_icon(self, status):
        try:
            icon_map = {
                "Playing": "media-playback-start",
                "Paused": "media-playback-pause",
                "Stopped": "media-playback-stop",
            }
            icon = icon_map.get(status, "media-playback-stop")
            self.status_icon.set_from_icon_name(icon, 12)
        except Exception as e:
            print(f"Error updating status icon: {e}")

    def update_all(self):
        if not self.player:
            self.set_visible(False)
            return

        try:
            self.update_thumbnail()
            self.update_position()
            self.set_visible(True)
        except Exception as e:
            print(f"Error updating widget: {e}")
            self.set_visible(False)
