import os
import unittest


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY"))


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestContradictionDetection(unittest.TestCase):
    def _make_tab(self):
        import tkinter as tk
        from soilclass.gui.input_tab import InputTab
        root = tk.Tk()
        self.addCleanup(root.destroy)
        return InputTab(root)

    def _add(self, tab, size, passing):
        tab.size_var.set(str(size))
        tab.pass_var.set(str(passing))
        tab.add_row()

    def test_valid_monotonic_data_builds_fine(self):
        tab = self._make_tab()
        self._add(tab, 4.75, 83)
        self._add(tab, 2.0, 65)
        self._add(tab, 0.075, 28)
        tab.np_var.set(True)
        sample = tab.build_sample()
        self.assertEqual(len(sample.sieve_data), 3)

    def test_increasing_passing_toward_finer_sieve_raises(self):
        tab = self._make_tab()
        self._add(tab, 4.75, 50)
        self._add(tab, 0.075, 80)
        tab.np_var.set(True)
        with self.assertRaises(ValueError) as ctx:
            tab.build_sample()
        self.assertIn("Contradiction", str(ctx.exception))

    def test_equal_passing_between_sieves_is_allowed(self):
        tab = self._make_tab()
        self._add(tab, 4.75, 65)
        self._add(tab, 2.0, 65)
        self._add(tab, 0.075, 28)
        tab.np_var.set(True)
        sample = tab.build_sample()
        self.assertEqual(len(sample.sieve_data), 3)

    def test_error_message_identifies_the_offending_rows(self):
        tab = self._make_tab()
        self._add(tab, 4.75, 50)
        self._add(tab, 0.075, 80)
        tab.np_var.set(True)
        with self.assertRaises(ValueError) as ctx:
            tab.build_sample()
        msg = str(ctx.exception)
        self.assertIn("4.75", msg)
        self.assertIn("0.075", msg)


if __name__ == "__main__":
    unittest.main()
