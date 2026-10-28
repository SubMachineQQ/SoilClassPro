from __future__ import annotations

import sys

if sys.platform == "darwin":
    UI_FONT = "Helvetica Neue"
    MONO_FONT = "Menlo"
else:
    UI_FONT = "Segoe UI"
    MONO_FONT = "Consolas"
