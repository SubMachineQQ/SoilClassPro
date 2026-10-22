import os
import unittest


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY"))


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestProjectForm(unittest.TestCase):
    def _make_launcher(self):
        from soilclass.gui.launcher import LauncherWindow
        launcher = LauncherWindow()

        def _safe_destroy():
            try:
                launcher.destroy()
            except Exception:
                pass

        self.addCleanup(_safe_destroy)
        return launcher

    def test_clicking_new_does_not_launch_immediately(self):
        launcher = self._make_launcher()
        launcher._on_click("New", None)
        self.assertIsNone(launcher.result,
                         "clicking New should show a form, not launch yet")

    def test_clicking_a_standard_does_not_launch_immediately(self):
        launcher = self._make_launcher()
        launcher._on_click("RSCS", "RSCS")
        self.assertIsNone(launcher.result)

    def test_create_project_populates_metadata_and_launches(self):
        import tkinter as tk
        launcher = self._make_launcher()
        launcher._show_project_form("ALL")

        entry_vars = {
            "project": tk.StringVar(value="Riverside Embankment"),
            "name": tk.StringVar(value="BH-3"),
            "location": tk.StringVar(value="Site A"),
            "operator": tk.StringVar(value="J. Doe"),
            "date": tk.StringVar(value="2026-07-11"),
        }
        launcher._create_project("ALL", entry_vars)

        self.assertIsNotNone(launcher.result)
        mode, sample = launcher.result
        self.assertEqual(mode, "ALL")
        self.assertEqual(sample.project, "Riverside Embankment")
        self.assertEqual(sample.name, "BH-3")
        self.assertEqual(sample.location, "Site A")
        self.assertFalse(sample.has_sieve_data,
                         "a freshly created project should have no "
                         "sieve data yet")

    def test_create_project_with_blank_name_defaults_sample_name(self):
        import tkinter as tk
        launcher = self._make_launcher()
        entry_vars = {k: tk.StringVar(value="")
                     for k in ("project", "name", "location", "operator",
                              "date")}
        launcher._create_project("ASTM", entry_vars)
        mode, sample = launcher.result
        self.assertEqual(mode, "ASTM")
        self.assertEqual(sample.name, "Sample 1")

    def test_hovering_away_after_click_does_not_reset_the_form(self):
        launcher = self._make_launcher()
        new_btn = launcher._buttons["New"]

        launcher._on_click("New", None)
        self.assertTrue(launcher._panel_locked)
        children_after_click = set(launcher.panel.winfo_children())

        launcher._on_leave(new_btn)

        self.assertTrue(launcher._panel_locked,
                        "the panel should still be locked")
        self.assertEqual(set(launcher.panel.winfo_children()),
                         children_after_click,
                         "leaving the button must not rebuild the panel")

    def test_hovering_a_standard_while_form_locked_does_not_reset_it(self):
        launcher = self._make_launcher()
        launcher._on_click("New", None)
        children_after_click = set(launcher.panel.winfo_children())

        astm_btn = launcher._buttons["ASTM"]
        launcher._on_hover("ASTM", astm_btn)

        self.assertEqual(set(launcher.panel.winfo_children()),
                         children_after_click,
                         "hovering a standard must not replace the "
                         "in-progress form")

    def test_default_view_is_unlocked_and_hover_preview_still_works(self):
        launcher = self._make_launcher()
        self.assertFalse(launcher._panel_locked)

        astm_btn = launcher._buttons["ASTM"]
        launcher._on_hover("ASTM", astm_btn)
        self.assertGreater(len(launcher.panel.winfo_children()), 0)

    def test_new_and_open_have_no_hover_binding(self):
        launcher = self._make_launcher()
        for label in ("New", "Open"):
            row = launcher._buttons[label]
            for w in row._tinted:
                self.assertEqual(w.bind("<Enter>"), "",
                                 f"{label} row must not bind <Enter>")
                self.assertEqual(w.bind("<Leave>"), "",
                                 f"{label} row must not bind <Leave>")


if __name__ == "__main__":
    unittest.main()
