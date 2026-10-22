import re
import unittest
from pathlib import Path

HEX_RE = re.compile(r'"#[0-9a-fA-F]{3,6}"')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOILCLASS_DIR = PROJECT_ROOT / "soilclass"
COLORS_FILE = SOILCLASS_DIR / "colors.py"


class TestNoStrayHexColors(unittest.TestCase):
    def test_only_colors_py_contains_hex_literals(self):
        offenders = []
        for path in SOILCLASS_DIR.rglob("*.py"):
            if path == COLORS_FILE:
                continue
            text = path.read_text(encoding="utf-8")
            matches = HEX_RE.findall(text)
            if matches:
                offenders.append((path.relative_to(PROJECT_ROOT), matches))
        if offenders:
            detail = "\n".join(f"  {p}: {m}" for p, m in offenders)
            self.fail(f"Found hardcoded hex colours outside colors.py:\n{detail}")


class TestColorsModuleStructure(unittest.TestCase):
    def test_expected_sections_exist(self):
        from soilclass import colors
        for name in ("THEME_LIGHT", "THEME_DARK", "SPLASH", "SPLASH_DARK",
                    "LAUNCHER", "LAUNCHER_DARK", "THEME_TOGGLE",
                    "CHART", "PDF_REPORT"):
            self.assertTrue(hasattr(colors, name), f"missing {name}")
            self.assertIsInstance(getattr(colors, name), dict)

    def test_dark_theme_has_key_parity_with_light(self):
        from soilclass import colors
        for dark_name, light_name in (
            ("THEME_DARK", "THEME_LIGHT"),
            ("LAUNCHER_DARK", "LAUNCHER"),
            ("SPLASH_DARK", "SPLASH"),
        ):
            self.assertTrue(hasattr(colors, dark_name), f"missing {dark_name}")
            dark = getattr(colors, dark_name)
            light = getattr(colors, light_name)
            self.assertIsInstance(dark, dict)
            self.assertEqual(set(dark.keys()), set(light.keys()),
                             f"{dark_name} keys must match {light_name} exactly")

    def test_every_theme_value_is_a_hex_string(self):
        from soilclass import colors
        hex_re = re.compile(r"^#[0-9a-fA-F]{6}$")
        for section_name in ("THEME_LIGHT", "THEME_DARK", "SPLASH", "SPLASH_DARK",
                            "LAUNCHER", "LAUNCHER_DARK", "THEME_TOGGLE",
                            "CHART", "PDF_REPORT"):
            section = getattr(colors, section_name)
            for key, value in section.items():
                self.assertRegex(value, hex_re,
                                 f"{section_name}['{key}'] = {value!r} is "
                                 "not a valid 6-digit hex colour")


class TestConsumersReadFromColorsModule(unittest.TestCase):
    def test_theme_reexports_colors_module_values(self):
        from soilclass import colors
        from soilclass.gui import theme
        self.assertEqual(theme.LIGHT, colors.THEME_LIGHT)

    def test_chart_style_reexports_colors_module_values(self):
        from soilclass import colors
        from soilclass.charts import style
        self.assertEqual(style.COLORS, colors.CHART)


if __name__ == "__main__":
    unittest.main()
