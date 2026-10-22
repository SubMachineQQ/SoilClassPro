import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from soilclass.charts import ALL_FIGURES, classifiable_chart_defs
from soilclass.charts import rscs_figure
from soilclass.classifiers import RSCSClassifier
from soilclass.example_data import example_sample
from soilclass.project_file import load_project, save_project


class TestRscsSwitch(unittest.TestCase):
    def test_disabled_sample_is_not_classified(self):
        sample = example_sample()
        sample.rscs_enabled = False
        result = RSCSClassifier().classify(sample)
        self.assertFalse(result.ok)

    def test_enabled_sample_without_parameters_uses_defaults(self):
        sample = example_sample()
        sample.rscs_enabled = True
        result = RSCSClassifier().classify(sample)
        self.assertTrue(result.ok)
        self.assertTrue(any("assumed R=" in note for note in result.notes))

    def test_disabled_sample_has_no_rscs_charts(self):
        sample = example_sample()
        sample.rscs_enabled = False
        builders = [b for _, b in classifiable_chart_defs(ALL_FIGURES, sample)]
        self.assertNotIn(rscs_figure, builders)
        sample.rscs_enabled = True
        builders = [b for _, b in classifiable_chart_defs(ALL_FIGURES, sample)]
        self.assertIn(rscs_figure, builders)

    def test_project_file_keeps_the_switch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "p.soilpro"
            for enabled in (True, False):
                sample = example_sample()
                sample.rscs_enabled = enabled
                save_project(path, sample, "ALL")
                loaded, _ = load_project(path)
                self.assertEqual(loaded.rscs_enabled, enabled)

    def test_old_project_files_infer_the_switch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "old.soilpro"
            save_project(path, example_sample(), "ALL")
            data = json.loads(path.read_text(encoding="utf-8"))
            del data["sample"]["rscs_enabled"]
            for mode, extra, expected in (("ALL", {}, False),
                                          ("ALL", {"ll_brine": 35.0}, True),
                                          ("RSCS", {}, True)):
                data["mode"] = mode
                data["sample"].update({"ll_brine": None}, **extra)
                path.write_text(json.dumps(data), encoding="utf-8")
                loaded, _ = load_project(path)
                self.assertEqual(loaded.rscs_enabled, expected, (mode, extra))


@unittest.skipUnless(os.environ.get("DISPLAY"), "no DISPLAY available for a GUI test")
class TestRscsCheckbox(unittest.TestCase):
    def _make(self, mode):
        from soilclass.gui.app import SoilClassApp
        app = SoilClassApp(mode=mode)
        self.addCleanup(app.destroy)
        app.update()
        return app

    def _fill(self, app, enabled):
        sample = example_sample()
        app.input_tab.load_sample(sample)
        app.input_tab.set_rscs_enabled(enabled)
        app.update()

    def test_all_mode_starts_unchecked(self):
        app = self._make("ALL")
        self.assertFalse(app.input_tab.rscs_shown.get())

    def test_rscs_mode_starts_checked(self):
        app = self._make("RSCS")
        self.assertTrue(app.input_tab.rscs_shown.get())

    def test_unchecked_box_leaves_rscs_out(self):
        app = self._make("ALL")
        self._fill(app, False)
        app.input_tab.rscs_vars["e_max_sand"].set("not a number")
        app.classify()
        app.update()
        systems = [r.system for r in app.results_tab.results]
        self.assertFalse(any("RSCS" in s for s in systems))
        self.assertEqual(len(systems), 4)

    def test_checked_box_with_empty_fields_uses_defaults(self):
        app = self._make("ALL")
        self._fill(app, True)
        app.classify()
        app.update()
        rscs = [r for r in app.results_tab.results if "RSCS" in r.system]
        self.assertEqual(len(rscs), 1)
        self.assertTrue(rscs[0].ok)

    def test_summary_and_button_follow_the_checkbox(self):
        from soilclass.i18n import t
        app = self._make("ALL")
        tab = app.input_tab
        tab.set_rscs_enabled(False)
        self.assertTrue(tab.rscs_button.instate(["disabled"]))
        self.assertEqual(tab.rscs_summary.get(), t("rscs_summary_off"))
        tab.set_rscs_enabled(True)
        self.assertFalse(tab.rscs_button.instate(["disabled"]))
        self.assertEqual(tab.rscs_summary.get(), t("rscs_summary_defaults"))
        tab.rscs_vars["ll_brine"].set("35")
        self.assertEqual(tab.rscs_summary.get(),
                         t("rscs_summary_count").format(count=1))

    def test_parameters_dialog_edits_the_same_fields(self):
        from soilclass.gui.input_tab import RscsParametersDialog
        app = self._make("ALL")
        self._fill(app, True)
        tab = app.input_tab
        dialog = RscsParametersDialog(app, tab.RSCS_FIELDS, tab.rscs_vars,
                                      app.palette)
        app.update()
        entries = [w for w in dialog.winfo_children()[0].winfo_children()
                   if w.winfo_class() == "TEntry"]
        self.assertEqual(len(entries), len(tab.RSCS_FIELDS))
        entries[0].insert(0, "0.45")
        dialog._clear()
        self.assertTrue(all(not v.get() for v in tab.rscs_vars.values()))
        entries[0].insert(0, "0.45")
        dialog.destroy()
        self.assertEqual(tab.rscs_vars["e_min_gravel"].get(), "0.45")
        sample = tab.build_sample()
        self.assertEqual(sample.e_min_gravel, 0.45)

    def test_rscs_mode_unchecked_explains_instead_of_classifying(self):
        from soilclass.gui import app as app_module
        app = self._make("RSCS")
        self._fill(app, False)
        with mock.patch.object(app_module.messagebox, "showinfo") as info:
            app.classify()
        self.assertTrue(info.called)
        self.assertIn("RSCS", info.call_args[0][1])
        self.assertIsNone(app.results_window)


if __name__ == "__main__":
    unittest.main()
