import os
import unittest


@unittest.skipUnless(os.environ.get("DISPLAY"), "no DISPLAY available for a GUI test")
class TestNoFocusRing(unittest.TestCase):
    def test_clickable_widgets_have_no_focus_element(self):
        import tkinter as tk
        from tkinter import ttk
        from soilclass.gui import theme
        root = tk.Tk()
        self.addCleanup(root.destroy)
        theme.apply_theme(root, dark=False)
        style = ttk.Style(root)

        def names(layout):
            for element, options in layout:
                yield element
                yield from names((options or {}).get("children", []))

        for layout in ("TNotebook.Tab", "TButton", "TCheckbutton",
                       "TRadiobutton", "Treeview.Item"):
            elements = list(names(style.layout(layout)))
            self.assertTrue(elements, layout)
            self.assertFalse([e for e in elements if e.endswith(".focus")],
                             layout)
        self.assertTrue(any(e.endswith(".label") or e.endswith(".text")
                            for e in names(style.layout("TNotebook.Tab"))))


if __name__ == "__main__":
    unittest.main()
