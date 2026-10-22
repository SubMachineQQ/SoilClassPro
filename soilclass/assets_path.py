import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    ASSETS_DIR = Path(getattr(sys, "_MEIPASS", ".")) / "soilclass" / "assets"
else:
    ASSETS_DIR = Path(__file__).resolve().parent / "assets"

LOGO_PNG = ASSETS_DIR / "logo.png"
LOGO_ICO = ASSETS_DIR / "logo.ico"
EXAMPLES_DIR = ASSETS_DIR / "examples"
IMPORT_HELP_DIR = ASSETS_DIR / "import_help"
