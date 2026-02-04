# MangoBar

A feature-rich status bar for Wayland compositors built with the Fabric framework. Provides real-time system monitoring, media controls, and workspace management with a sleek Tokyo Night Storm theme.

## Features

- **CPU & Memory Monitoring**: Real-time CPU usage, temperature, and RAM tracking with animated circular progress bars
- **GPU Monitoring**: NVIDIA GPU usage and temperature monitoring (requires `nvidia-smi`)
- **Spotify Media Widget**: Dynamic album art, playback progress, and play/pause controls
- **Audio Control**: Volume control with mouse wheel scroll support
- **Workspace Management**: Mango workspace switching and layout display
- **System Info**: Date, time, and uptime displays
- **Multi-Monitor Support**: Run separate instances on different monitors

## Screenshots

*Screenshots coming soon*

## Requirements

### System Dependencies
- Python 3.10 or higher
- Wayland compositor (tested with Mango)
- `playerctl` (for media widget)
- `nvidia-smi` (optional, for GPU monitoring)

### Python Dependencies
- `fabric` - Wayland GUI framework
- `psutil` - System monitoring
- `PyGObject` (gi) - GTK/GObject introspection
- `pynvml` - NVIDIA GPU monitoring (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mangobar.git
cd mangobar
```

2. Install Python dependencies:
```bash
pip install fabric psutil PyGObject pynvml
```

3. Install system dependencies (Arch Linux):
```bash
sudo pacman -S playerctl python-gobject gtk3
```

## Customization

### Styling
Edit `style.css` to customize colors, fonts, and spacing. The default theme uses Tokyo Night Storm colors.

### Widgets
Enable/disable widgets by modifying the flags in module files:
- `AUDIO_WIDGET` in `modules/audio.py`
- `GPU_WIDGET` in `modules/gpu.py`
- `MEDIA_WIDGET` in `modules/media.py`

Add or remove widgets in `config.py` by editing the `StatusBar` class's `start_children`, `center_children`, and `end_children` lists.

## Development

### Code Quality
```bash
# Format code
black modules/ widgets/ services/ config.py

# Lint
flake8 modules/ widgets/ services/ config.py

# Type check
mypy modules/ widgets/ services/ config.py
```

### Testing
Currently uses manual testing. Run the application and verify functionality:
```bash
python config.py
```

See `AGENTS.md` for detailed development guidelines.

## Architecture

MangoBar uses a widget-based architecture with clear separation of concerns:
- **modules/**: System monitoring widgets (CPU, GPU, audio, media, etc.)
- **widgets/**: Reusable custom widgets (animated progress bars, etc.)
- **services/**: Utility services (animation, workspace integration)
- **config.py**: Main application entry point and status bar layout

The bar uses Fabric's reactive `Fabricator` for polling system data and `.bind()` for widget updates.

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please follow the code style guidelines in `AGENTS.md` when submitting pull requests.

## Credits

Built with [Fabric](https://github.com/Fabric-Development/fabric) - A Python GUI framework for Wayland
