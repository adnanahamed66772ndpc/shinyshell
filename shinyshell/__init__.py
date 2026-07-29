"""
shinyshell — Beautiful terminal output for Python. Zero dependencies.
=====================================
One import. All the pretty you need.

    from shinyshell import Shell
    sh = Shell()
    sh.success("Deployed!")
    sh.table(users)
    sh.progress("Loading...")

Pure Python stdlib. Works on Linux, macOS, Windows.
"""

__version__ = "0.6.0"
__all__ = ["Shell"]

import shutil
from typing import Any

from .colors import _supports_color, _Style
from .icons import _ICONS, _BORDERS
from .messages import _MessageMixin, _LayoutMixin
from .progress import _ProgressMixin
from .tables import _TableMixin
from .charts import _ChartMixin
from .interactive import _InteractiveMixin
from .code import _CodeMixin
from .network import _NetworkMixin
from .data import _DataMixin
from .games import _GamesMixin
from .utils import _UtilsMixin
from .files import _FilesMixin
from .qr import _QRMixin
from .pipe import _PipeOutput


class Shell(
    _MessageMixin,
    _LayoutMixin,
    _ProgressMixin,
    _TableMixin,
    _ChartMixin,
    _InteractiveMixin,
    _CodeMixin,
    _NetworkMixin,
    _DataMixin,
    _GamesMixin,
    _UtilsMixin,
    _FilesMixin,
    _QRMixin,
):
    """Beautiful terminal output for Python scripts and CLIs."""

    def __init__(self, color: bool = True, width: int | None = None):
        self._color_enabled = color and _supports_color()
        self._style = _Style(self._color_enabled)
        self._width = width or min(shutil.get_terminal_size().columns, 120)
        self._theme: dict[str, str] = {}
        self._session_file: str | None = None

    def pipe(self, data: Any):
        """Chained output: sh.pipe(data).table().metrics()"""
        return _PipeOutput(data, self)

    @property
    def icons(self):
        """Access icon constants."""
        return _ICONS
