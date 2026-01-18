import gi
gi.require_version('GLib', '2.0')
from gi.repository import GLib, GObject
import subprocess

class MangoService(GObject.Object):
    __gsignals__ = {
        'tags-changed': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'layout-changed': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'client-changed': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, monitor=None):
        super().__init__()
        self.monitor = monitor
        self.num_tags = 9  # default
        self.available_tags = list(range(1, self.num_tags + 1))
        self.active_tags = []
        self.occupied_tags = []
        self.layout = None
        self.focused_client = None
        self.update()
        GLib.timeout_add(1000, self.update)  # poll every second

    def run_mmsg(self, args):
        cmd = ['mmsg']
        if self.monitor:
            cmd.extend(['-o', self.monitor])
        cmd.extend(args)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except subprocess.TimeoutExpired:
            pass
        except FileNotFoundError:
            pass  # mmsg not found
        return None

    def update(self):
        changed = False

        # get number of tags
        num_str = self.run_mmsg(['-T'])
        if num_str:
            try:
                new_num = int(num_str)
                if new_num != self.num_tags:
                    self.num_tags = new_num
                    self.available_tags = list(range(1, self.num_tags + 1))
                    changed = True
            except ValueError:
                pass

        # get tags info
        tags_info = self.run_mmsg(['-g', '-t'])
        if tags_info:
            lines = tags_info.split('\n')
            target_monitor = self.monitor
            for line in lines:
                parts = line.split()
                if len(parts) >= 4 and parts[1] == 'tags':
                    if target_monitor is None:
                        # for no monitor, take first
                        pass
                    else:
                        # for specific monitor, take it (since -o filters to that monitor)
                        pass
                    try:
                        occupied_str = parts[2]
                        active_str = parts[3]
                        occupied_mask = int(occupied_str, 2)
                        active_mask = int(active_str, 2)

                        new_occupied = [i for i in range(1, self.num_tags + 1) if occupied_mask & (1 << (i - 1))]
                        new_active = [i for i in range(1, self.num_tags + 1) if active_mask & (1 << (i - 1))]

                        if new_occupied != self.occupied_tags or new_active != self.active_tags:
                            self.occupied_tags = new_occupied
                            self.active_tags = new_active
                            changed = True
                        if target_monitor is not None:
                            break  # only one for specific monitor
                    except (ValueError, IndexError):
                        pass
                    if target_monitor is None:
                        break  # take first for no monitor

        # get current layout
        layout_str = self.run_mmsg(['-g', '-l'])
        if layout_str and layout_str != self.layout:
            self.layout = layout_str
            self.emit('layout-changed')

        # get focused client
        client_str = self.run_mmsg(['-g', '-c'])
        new_client = None
        if client_str:
            parts = client_str.split(' ', 1)
            if len(parts) == 2:
                new_client = {'title': parts[0], 'appid': parts[1]}
            else:
                new_client = {'title': client_str, 'appid': ''}
        if new_client != self.focused_client:
            self.focused_client = new_client
            self.emit('client-changed')

        if changed:
            self.emit('tags-changed')

        return True  # continue polling