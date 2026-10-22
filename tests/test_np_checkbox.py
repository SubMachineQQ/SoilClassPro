import os
import unittest


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY"))


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestNpCheckbox(unittest.TestCase):
    def _make_tab(self):
        import tkinter as tk
        from soilclass.gui.input_tab import InputTab
        root = tk.Tk()
        root.geometry("900x700+0+0")
        self.addCleanup(root.destroy)
        tab = InputTab(root)
        tab.pack(fill="both", expand=True)
        root.update()
        return root, tab

    def test_typing_a_limit_unticks_np_and_keeps_the_value(self):
        root, tab = self._make_tab()
        tab.np_var.set(True)
        tab.ll_entry.focus_force()
        root.update()
        tab.ll_entry.event_generate("<KeyPress>", keysym="4")
        root.update()
        self.assertFalse(tab.np_var.get())

    def test_tab_key_alone_does_not_untick_np(self):
        root, tab = self._make_tab()
        tab.np_var.set(True)
        tab.ll_entry.focus_force()
        root.update()
        tab.ll_entry.event_generate("<KeyPress>", keysym="Tab")
        root.update()
        self.assertTrue(tab.np_var.get())

    def test_typed_limits_reach_the_sample_after_unticking(self):
        root, tab = self._make_tab()
        tab.np_var.set(True)
        tab.ll_entry.focus_force()
        root.update()
        tab.ll_entry.event_generate("<KeyPress>", keysym="2")
        tab.ll_var.set("25")
        tab.pl_var.set("20")
        root.update()
        for size, passing in ((4.75, 100), (0.075, 30)):
            tab.tree.insert("", "end", values=(f"{size:g}", f"{passing:g}"))
        sample = tab.build_sample()
        self.assertEqual(sample.liquid_limit, 25.0)
        self.assertEqual(sample.plastic_limit, 20.0)


if __name__ == "__main__":
    unittest.main()
