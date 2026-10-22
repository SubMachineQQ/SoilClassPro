import os
import unittest
from unittest import mock


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY"))


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestSetWindowIcon(unittest.TestCase):
    def _make_root(self):
        import tkinter as tk
        root = tk.Tk()
        self.addCleanup(root.destroy)
        return root

    def test_windows_path_uses_iconbitmap_with_the_ico_file(self):
        from soilclass.gui import icon_utils
        from soilclass.assets_path import LOGO_ICO

        root = self._make_root()
        with mock.patch.object(icon_utils.sys, "platform", "win32"), \
             mock.patch.object(root, "iconbitmap") as mock_iconbitmap:
            icon_utils.set_window_icon(root)

        mock_iconbitmap.assert_called_once_with(str(LOGO_ICO))

    def test_non_windows_path_uses_iconphoto_with_the_png(self):
        from soilclass.gui import icon_utils

        root = self._make_root()
        with mock.patch.object(icon_utils.sys, "platform", "linux"), \
             mock.patch.object(root, "iconphoto") as mock_iconphoto:
            icon_utils.set_window_icon(root)

        self.assertTrue(mock_iconphoto.called)
        args, _ = mock_iconphoto.call_args
        self.assertEqual(args[0], True)

    def test_windows_fallback_to_png_if_iconbitmap_fails(self):
        import tkinter as tk
        from soilclass.gui import icon_utils

        root = self._make_root()
        with mock.patch.object(icon_utils.sys, "platform", "win32"), \
             mock.patch.object(root, "iconbitmap",
                              side_effect=tk.TclError("bad icon")), \
             mock.patch.object(root, "iconphoto") as mock_iconphoto:
            icon_utils.set_window_icon(root)

        self.assertTrue(mock_iconphoto.called)

    def test_does_not_raise_on_a_real_window(self):
        from soilclass.gui import icon_utils
        root = self._make_root()
        icon_utils.set_window_icon(root)


if __name__ == "__main__":
    unittest.main()
