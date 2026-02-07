# AGENTS.md - Development Guidelines for MangoBar

## Overview
MangoBar is a Python-based status bar for Wayland compositors built with Fabric framework. Provides system monitoring widgets (CPU, GPU, memory, audio, time, workspace management).

**Tech Stack**: Python 3.10+, Fabric (Wayland GUI), psutil, PyGObject, pynvml

## Build, Lint, and Test Commands

### Running the Application
```bash
python config.py          # Run on default monitor
python config.py 2        # Run on monitor 2
./test_media_widget.sh    # Manual integration test script
```

### Testing (Manual - No pytest yet)
```bash
# Quick module import test
python -c "from modules.cpu import Cpu; print('OK')"

# Test specific functionality
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%')"

# Full application test
python config.py
```

**Future pytest commands** (when implemented):
```bash
pytest                                        # Run all tests
pytest tests/test_cpu.py                     # Run specific test file
pytest tests/test_cpu.py::test_cpu_widget    # Run single test function
pytest -v --cov=modules --cov-report=html    # Run with coverage
```

### Code Quality
```bash
# Format code (Black - line length 88)
black modules/ widgets/ services/ config.py

# Lint (flake8)
flake8 modules/ widgets/ services/ config.py

# Type check (mypy)
mypy modules/ widgets/ services/ config.py

# Run all checks
black modules/ widgets/ services/ config.py && flake8 modules/ widgets/ services/ config.py && mypy modules/ widgets/ services/ config.py
```

**Note**: Expect ~19 flake8 issues (unused imports) and ~15 mypy issues (missing stubs for fabric/pynvml).

### Build Commands
```bash
python -m build                    # Build distribution
pip install -e .                   # Development install
rm -rf build/ dist/ *.egg-info/   # Clean artifacts
```

## Code Style Guidelines

### General Principles
- **Self-documenting code**: Avoid redundant comments
- **Widget-based architecture**: Clear separation of concerns per system component
- **Optional features**: Use try/except for imports with fallback flags (see `AUDIO_WIDGET`)
- **Modern Python**: Use match/case (3.10+), f-strings, type hints where possible

### Import Order (PEP 8)
```python
# 1. Standard library (alphabetical)
import sys
import subprocess

# 2. Third-party (Fabric grouped together)
from fabric import Application, Fabricator
from fabric.widgets.box import Box
from fabric.widgets.label import Label

# 3. Local modules
from modules.audio import VolumeWidget
from widgets.animated_circular_progress_bar import AnimatedCircularProgressBar
from services.animator import Animator
```

### Naming Conventions
- **Classes**: `PascalCase` (VolumeWidget, StatusBar, AnimatedCircularProgressBar)
- **Functions/Methods**: `snake_case` (on_scroll, get_cpu_temp, animate_value)
- **Variables**: `snake_case` (self.audio, progress_bar, cpu_usage)
- **Constants**: `UPPER_CASE` (AUDIO_WIDGET = True)
- **CSS names**: `kebab-case` (name="cpu-progress-bar", name="volume-widget")
- **Private**: `_single_underscore` (_update_display, _start_time)

### Widget Class Pattern
```python
class ExampleWidget(Box):
    def __init__(self, **kwargs):
        # 1. Initialize child widgets first
        self.label = Label(label="Example")
        self.progress = AnimatedCircularProgressBar(name="example-progress", size=34)
        
        # 2. Call super().__init__ with widget tree
        super().__init__(
            name="example-widget",
            orientation="v",  # 'v' vertical, 'h' horizontal
            spacing=8,        # Use: 4 (tight), 6 (normal), 8 (loose), 10 (sections)
            children=[self.progress, self.label],
            **kwargs,
        )
    
    def on_event(self, widget, data):
        """Event handlers use snake_case."""
        pass
```

### Common Patterns
```python
# Fabricator for polling system data (1000ms = 1 second)
Fabricator(
    interval=1000,
    poll_from=lambda f: psutil.cpu_percent(),
    on_changed=lambda _, value: self.label.set_label(f"{int(value)}%"),
)

# AnimatedCircularProgressBar with Overlay
Overlay(
    child=CircularProgressBar(name="circle-progress-back", size=34, value=100),
    overlays=AnimatedCircularProgressBar(name="cpu-bar", size=34, child=Label()),
)

# EventBox for scroll/click events
EventBox(events="scroll", child=widget, on_scroll_event=self.on_scroll)

# Binding for reactive updates
self.audio.speaker.bind("volume", "value", self.progress_bar,
                        lambda _, v: self.progress_bar.animate_value(v / 100))

# Optional feature with fallback
FEATURE_ENABLED = True
try:
    from fabric.feature import Feature
except ImportError as e:
    FEATURE_ENABLED = False
    print(f"Feature unavailable: {e}")
```

### String Formatting
```python
# Use f-strings (preferred)
self.label.set_label(f"{int(value)}%")
self.temp.set_label(f"{temp}°C")

# Double quotes for strings
label = Label(label="CPU Usage")
```

### Layout & Spacing
- **Box**: `orientation="v"` (vertical) or `"h"` (horizontal)
- **CenterBox**: Three sections: `start_children`, `center_children`, `end_children`
- **Spacing values**: 4px, 6px, 8px, 10px (consistent increments)
- **Alignment**: `h_align="center"`, `v_align="center"`
- **Progress bars**: 34px size standard

### CSS (style.css)
- **Theme**: Tokyo Night Storm colors
- **Font**: "Terminess Nerd Font Mono"
- **Border radius**: 9px for pill shapes
- **Use CSS variables**: Define in `:vars` block, reference with `var(--color-name)`

## File Structure
```
mangobar/
├── config.py                    # Main app + StatusBar class (entry point)
├── style.css                    # GTK CSS with Tokyo Night theme
├── pyproject.toml/.flake8       # Build & quality tool config
├── test_media_widget.sh         # Manual integration test script
├── modules/                     # System monitoring widgets
│   ├── cpu.py                   # CPU/RAM with temp (Cpu class)
│   ├── gpu.py                   # NVIDIA GPU monitoring (Gpu class)
│   ├── audio.py                 # Volume control (VolumeWidget + AUDIO_WIDGET flag)
│   ├── time.py, date.py         # DateTime displays
│   ├── tags.py, layout.py       # Workspace/window management
│   └── uptime.py                # System uptime
├── widgets/                     # Reusable custom widgets
│   └── animated_circular_progress_bar.py
└── services/                    # Utility services
    ├── animator.py              # Bezier curve animation service
    └── mango.py                 # Workspace service integration
```

## Development Workflow
1. **Create widget**: New file in `modules/` inheriting from `Box`
2. **Import in config.py**: Add to StatusBar layout (start/center/end children)
3. **Test**: Run `python config.py` and verify functionality
4. **Quality checks**: Run `black && flake8 && mypy`
5. **Commit**: Follow existing patterns, test on target Wayland compositor

## Architecture Notes
- **Reactive**: `Fabricator` polls system data, `.bind()` for widget updates
- **Wayland-only**: Uses `WaylandWindow`, layer shell protocol (`layer="top"`)
- **Multi-monitor**: Pass monitor index as CLI arg to `config.py`
- **Animation**: Custom `Animator` service with bezier curves (0.8s duration)