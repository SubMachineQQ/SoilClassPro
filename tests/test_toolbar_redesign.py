import os
import unittest


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY"))


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestToolbarRedesign(unittest.TestCase):
    def _make_app(self):
        from soilclass.gui.app import SoilClassApp
        app = SoilClassApp(mode="ALL")
        self.addCleanup(app._on_close)
        return app

    def test_no_about_method_or_about_dialog(self):
        app = self._make_app()
        self.assertFalse(hasattr(app, "_about"),
                         "the About feature should be fully removed")

    def test_no_logo_button_in_toolbar(self):
        app = self._make_app()

        def find_all_buttons(w):
            found = []
            for c in w.winfo_children():
                if c.winfo_class() in ("TButton", "TMenubutton"):
                    found.append(c)
                found.extend(find_all_buttons(c))
            return found

        for btn in find_all_buttons(app):
            has_image = bool(btn.cget("image")) if "image" in btn.keys() \
                       else False
            self.assertFalse(has_image,
                             "no toolbar button should show the logo image")
            text = btn.cget("text") if "text" in btn.keys() else ""
            self.assertNotEqual(text, "\u25cf",
                                "no leftover decorative circle button")

    @staticmethod
    def _collect_labels(entries):
        from soilclass.gui.dropdown_menu import MenuItem
        labels = []
        for entry in entries:
            if isinstance(entry, MenuItem):
                labels.append(entry.label)
                if entry.items:
                    labels.extend(TestToolbarRedesign._collect_labels(entry.items))
        return labels

    def test_single_consolidated_menu_button(self):
        app = self._make_app()
        self.assertIn("Menu", app._menu_btn.cget("text"))

        popup = app._open_main_menu()
        self.addCleanup(popup.close)
        labels = self._collect_labels(popup._entries)
        for expected in ("Save Project", "Save As", "Open Project"):
            self.assertTrue(any(expected in l for l in labels),
                           f"{expected!r} missing from the menu: {labels}")
        for expected in ("Import", "Export"):
            self.assertTrue(any(expected in l for l in labels),
                           f"{expected!r} group missing from the menu: {labels}")
        for gone in ("Options", "Language", "Print", "OCR", "AI"):
            self.assertFalse(any(gone in l for l in labels),
                             f"{gone!r} should no longer be in the menu: {labels}")
        for expected in ("Home", "Undo", "Compare"):
            self.assertTrue(any(expected in l for l in labels),
                           f"{expected!r} missing from the menu: {labels}")

    def test_only_the_menu_button_and_classify_button_are_visible(self):
        app = self._make_app()

        def find_buttons(w):
            found = []
            for c in w.winfo_children():
                if c.winfo_class() == "TButton":
                    found.append(c)
                found.extend(find_buttons(c))
            return found

        buttons = find_buttons(app._toolbar_bar)
        self.assertEqual(len(buttons), 2)

    def test_classify_button_still_present_and_prominent(self):
        app = self._make_app()

        def find_classify(w):
            for c in w.winfo_children():
                if (c.winfo_class() == "TButton"
                        and str(c.cget("style")) == "Classify.TButton"):
                    return c
                found = find_classify(c)
                if found is not None:
                    return found
            return None

        from soilclass.i18n import t

        btn = find_classify(app)
        self.assertIsNotNone(btn)
        self.assertIn(t("classify_button"), btn.cget("text"))


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestInputTabLayout(unittest.TestCase):
    def _make_tab(self):
        import tkinter as tk
        from soilclass.gui.input_tab import InputTab
        root = tk.Tk()
        self.addCleanup(root.destroy)
        return InputTab(root)

    def test_no_sample_information_labelframe(self):
        tab = self._make_tab()

        def find_labelframes(w):
            found = []
            for c in w.winfo_children():
                if c.winfo_class() == "TLabelframe":
                    found.append(c.cget("text"))
                found.extend(find_labelframes(c))
            return found

        labelframe_texts = find_labelframes(tab)
        joined = " ".join(labelframe_texts)
        self.assertNotIn("Sample information", joined)

    def test_metadata_vars_exist_but_are_not_bound_to_visible_entries(self):
        tab = self._make_tab()
        for key in ("name", "project", "location", "operator", "date"):
            self.assertIn(key, tab.meta_vars)
        tab.meta_vars["project"].set("Test Project")
        sample = None
        tab.size_var.set("4.75")
        tab.pass_var.set("83")
        tab.add_row()
        tab.size_var.set("0.075")
        tab.pass_var.set("28")
        tab.add_row()
        tab.np_var.set(True)
        sample = tab.build_sample()
        self.assertEqual(sample.project, "Test Project")

    def test_atterberg_limits_still_present(self):
        tab = self._make_tab()
        self.assertTrue(hasattr(tab, "ll_var"))
        self.assertTrue(hasattr(tab, "pl_var"))
        self.assertTrue(hasattr(tab, "organic_var"))
        self.assertTrue(hasattr(tab, "np_var"))


if __name__ == "__main__":
    unittest.main()
