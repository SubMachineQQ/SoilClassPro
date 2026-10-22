import shutil
import tempfile
import unittest
from pathlib import Path

from soilclass.importers.csv_import import import_file

try:
    import openpyxl
except ImportError:
    openpyxl = None

SIZES = [19.0, 9.5, 4.75, 2.0, 0.85, 0.425, 0.25, 0.106, 0.075]
PASSING = [100.0, 92.0, 83.0, 65.0, 54.0, 45.0, 38.0, 31.0, 28.0]
MASS_TOTAL = 500.0


def _retained_masses():
    masses = []
    previous = 100.0
    for passing in PASSING:
        masses.append((previous - passing) / 100.0 * MASS_TOTAL)
        previous = passing
    return masses, PASSING[-1] / 100.0 * MASS_TOTAL


@unittest.skipIf(openpyxl is None, "openpyxl not installed")
class UniversalImportTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def xlsx(self, name, rows, sheets=None):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Veri"
        for row in rows:
            ws.append(list(row))
        for title, extra in (sheets or {}).items():
            other = wb.create_sheet(title)
            for row in extra:
                other.append(list(row))
        path = self.dir / name
        wb.save(path)
        return path

    def assertCurve(self, data, sizes=SIZES, passing=PASSING, places=1):
        got = dict(data.sieve)
        self.assertEqual(len(got), len(sizes), data.sieve)
        for size, value in zip(sizes, passing):
            self.assertIn(size, got)
            self.assertAlmostEqual(got[size], value, places=places)

    def test_simple_two_columns_with_metadata(self):
        rows = [["SoilClass Pro"], [],
                ["Numune adı", "BH-1 / 3.5 m"], ["Proje", "Nehir Dolgusu"],
                ["Likit limit, LL (%)", 38], ["Plastik limit, PL (%)", 19],
                [], ["Elek açıklığı (mm)", "Geçen (%)"]]
        rows += [[s, p] for s, p in zip(SIZES, PASSING)]
        data = import_file(str(self.xlsx("basit.xlsx", rows)))
        self.assertCurve(data)
        self.assertEqual(data.liquid_limit, 38)
        self.assertEqual(data.plastic_limit, 19)
        self.assertEqual(data.meta["name"], "BH-1 / 3.5 m")
        self.assertEqual(data.meta["project"], "Nehir Dolgusu")
        self.assertEqual(data.meta["_method"], "passing")

    def test_turkish_lab_sheet_with_two_row_header(self):
        masses, pan = _retained_masses()
        rows = [["ELEK ANALİZİ DENEY FÖYÜ (TS EN ISO 17892-4)"],
                ["Numune kütlesi (g)", MASS_TOTAL],
                [],
                ["Elek No", "Göz açıklığı", "Elekte kalan", "Kümülatif kalan", "Geçen"],
                [None, "(mm)", "kütle (g)", "(%)", "(%)"]]
        names = ['3/4"', '3/8"', "No.4", "No.10", "No.20", "No.40", "No.60",
                 "No.140", "No.200"]
        for name, size, mass, passing in zip(names, SIZES, masses, PASSING):
            rows.append([name, size, mass, 100 - passing, passing])
        rows.append(["Tava", None, pan, None, None])
        data = import_file(str(self.xlsx("foy.xlsx", rows)))
        self.assertCurve(data)
        self.assertEqual(data.meta["_method"], "passing")

    def test_masses_only_with_total_mass(self):
        masses, pan = _retained_masses()
        rows = [["Kuru numune kütlesi (g)", MASS_TOTAL], [],
                ["Elek açıklığı (mm)", "Elekte kalan kütle (g)"]]
        rows += [[s, m] for s, m in zip(SIZES, masses)]
        data = import_file(str(self.xlsx("kutle.xlsx", rows)))
        self.assertCurve(data)
        self.assertEqual(data.meta["_method"], "ret_mass")

    def test_masses_only_with_pan_and_no_total(self):
        masses, pan = _retained_masses()
        rows = [["Sieve opening (mm)", "Mass retained (g)"]]
        rows += [[s, m] for s, m in zip(SIZES, masses)]
        rows.append(["Pan", pan])
        data = import_file(str(self.xlsx("pan.xlsx", rows)))
        self.assertCurve(data)

    def test_cumulative_percent_retained_only(self):
        rows = [["Göz açıklığı (mm)", "Kümülatif kalan (%)"]]
        rows += [[s, 100 - p] for s, p in zip(SIZES, PASSING)]
        data = import_file(str(self.xlsx("kumulatif.xlsx", rows)))
        self.assertCurve(data)
        self.assertEqual(data.meta["_method"], "cum_ret_pct")

    def test_astm_sieve_designations_and_percent_finer(self):
        names = ['3/4 in', '3/8"', "No. 4", "#10", "No. 20", "No. 40",
                 "No. 60", "No. 140", "#200"]
        rows = [["Sieve", "Percent Finer"]]
        rows += [[n, p] for n, p in zip(names, PASSING)]
        rows += [[], ["Liquid Limit", 38], ["Plastic Limit", 19]]
        data = import_file(str(self.xlsx("astm.xlsx", rows)))
        sizes = [19.0, 9.5, 4.75, 2.0, 0.85, 0.425, 0.25, 0.106, 0.075]
        self.assertCurve(data, sizes=sizes)
        self.assertEqual(data.liquid_limit, 38)

    def test_several_samples_in_columns(self):
        second = [100, 97, 90, 78, 69, 60, 52, 44, 40]
        rows = [["Sieve size (mm)", "BH1-1.5", "BH1-3.0"]]
        rows += [[s, a, b] for s, a, b in zip(SIZES, PASSING, second)]
        rows += [[], ["LL (%)", 38, 45], ["PL (%)", 19, 22]]
        data = import_file(str(self.xlsx("coklu.xlsx", rows)))
        samples = [data] + data.others
        self.assertEqual(len(samples), 2)
        names = {s.meta["name"]: s for s in samples}
        self.assertCurve(names["BH1-1.5"])
        self.assertCurve(names["BH1-3.0"], passing=second)
        self.assertEqual(names["BH1-1.5"].liquid_limit, 38)
        self.assertEqual(names["BH1-3.0"].liquid_limit, 45)
        self.assertEqual(names["BH1-3.0"].plastic_limit, 22)

    def test_horizontal_layout(self):
        rows = [["Elek açıklığı (mm)", *SIZES], ["Geçen (%)", *PASSING],
                [], ["LL", 38], ["PL", 19]]
        data = import_file(str(self.xlsx("yatay.xlsx", rows)))
        self.assertCurve(data)
        self.assertEqual(data.plastic_limit, 19)

    def test_percent_formatted_cells(self):
        rows = [["Sieve (mm)", "% Passing"]]
        rows += [[s, p / 100.0] for s, p in zip(SIZES, PASSING)]
        data = import_file(str(self.xlsx("yuzde.xlsx", rows)))
        self.assertCurve(data)

    def test_micrometre_sizes(self):
        rows = [["Particle size (µm)", "Passing (%)"]]
        rows += [[s * 1000, p] for s, p in zip(SIZES, PASSING)]
        data = import_file(str(self.xlsx("mikron.xlsx", rows)))
        self.assertCurve(data)

    def test_ascending_order_and_hydrometer_rows(self):
        sizes = SIZES + [0.02, 0.005, 0.001]
        passing = PASSING + [18.0, 10.0, 4.0]
        rows = [["Dane çapı (mm)", "Geçen yüzde (%)"]]
        rows += [[s, p] for s, p in sorted(zip(sizes, passing))]
        data = import_file(str(self.xlsx("artan.xlsx", rows)))
        self.assertCurve(data, sizes=sizes, passing=passing)

    def test_data_on_second_sheet(self):
        rows = [["Elek açıklığı (mm)", "Geçen (%)"]]
        rows += [[s, p] for s, p in zip(SIZES, PASSING)]
        data = import_file(str(self.xlsx("sayfa.xlsx", [["Kapak"], ["Rapor"]],
                                         {"Elek": rows})))
        self.assertCurve(data)

    def test_semicolon_csv_with_decimal_commas(self):
        lines = ["Elek açıklığı (mm);Geçen (%)"]
        lines += [f"{str(s).replace('.', ',')};{str(p).replace('.', ',')}"
                  for s, p in zip(SIZES, PASSING)]
        lines += ["Likit limit;38", "Plastik limit;19"]
        path = self.dir / "veri.csv"
        path.write_text("\n".join(lines), encoding="cp1254")
        data = import_file(str(path))
        self.assertCurve(data)
        self.assertEqual(data.liquid_limit, 38)

    def test_ags4_file_written_by_soilclass(self):
        from soilclass.example_data import example_sample
        from soilclass.report.ags4_export import build_ags4_text
        sample = example_sample()
        path = self.dir / "veri.ags"
        path.write_text(build_ags4_text(sample), encoding="utf-8")
        data = import_file(str(path))
        self.assertEqual(data.sieve, sorted(sample.sieve_data, key=lambda p: -p[0]))
        self.assertEqual(data.liquid_limit, sample.liquid_limit)
        self.assertEqual(data.plastic_limit, sample.plastic_limit)

    def test_standard_ags4_grat_group(self):
        text = "\r\n".join([
            '"GROUP","PROJ"', '"HEADING","PROJ_ID","PROJ_NAME"',
            '"UNIT","",""', '"TYPE","ID","X"', '"DATA","P1","Liman"',
            '', '"GROUP","GRAT"',
            '"HEADING","LOCA_ID","SAMP_TOP","SAMP_REF","SAMP_TYPE","SAMP_ID",'
            '"SPEC_REF","SPEC_DPTH","GRAT_SIZE","GRAT_PERP"',
            '"UNIT","","m","","","","","m","mm","%"',
            '"TYPE","ID","2DP","X","PA","ID","X","2DP","3SF","0DP"',
            *[f'"DATA","BH2","4.50","1","B","","","4.50","{s}","{p}"'
              for s, p in zip(SIZES, PASSING)],
            '', '"GROUP","LLPL"',
            '"HEADING","LOCA_ID","SAMP_TOP","SAMP_REF","SAMP_TYPE","SAMP_ID",'
            '"SPEC_REF","SPEC_DPTH","LLPL_LL","LLPL_PL"',
            '"UNIT","","m","","","","","m","%","%"',
            '"TYPE","ID","2DP","X","PA","ID","X","2DP","2SF","XN"',
            '"DATA","BH2","4.50","1","B","","","4.50","41","NP"'])
        path = self.dir / "standart.ags"
        path.write_text(text, encoding="utf-8")
        data = import_file(str(path))
        self.assertCurve(data)
        self.assertEqual(data.liquid_limit, 41)
        self.assertIsNone(data.plastic_limit)
        self.assertEqual(data.meta["name"], "BH2 / 4.50 m")
        self.assertEqual(data.meta["project"], "Liman")

    def test_metadata_rows_are_not_mistaken_for_sieve_points(self):
        rows = [["Sondaj", "BH-1"], ["Derinlik (m)", 3.5],
                ["Tarih", "2026-10-22"], [],
                ["Elek açıklığı (mm)", "Geçen (%)"]]
        rows += [[s, p] for s, p in zip(SIZES, PASSING)]
        data = import_file(str(self.xlsx("meta.xlsx", rows)))
        self.assertCurve(data)

    def test_unrecognised_file_gives_a_clear_warning(self):
        rows = [["Hello"], ["Nothing to see"]]
        data = import_file(str(self.xlsx("bos.xlsx", rows)))
        self.assertFalse(data.ok)
        self.assertTrue(data.warnings)


if __name__ == "__main__":
    unittest.main()
