from __future__ import annotations

import sys


def selftest() -> int:
    import matplotlib
    matplotlib.use("Agg")

    from soilclass.classifiers import classify_all
    from soilclass.example_data import example_sample
    from soilclass.report import build_pdf

    sample = example_sample()
    print(f"Self-test sample: {sample.name}")
    print("-" * 62)
    for r in classify_all(sample):
        print(f"{r.system:<34} {r.symbol:<12} {r.name}")
    path = build_pdf(sample, "selftest_report.pdf")
    print("-" * 62)
    print(f"PDF report written to: {path}")
    return 0


def main() -> int:
    from soilclass.gui.scaling import enable_dpi_awareness
    enable_dpi_awareness()
    if "--selftest" in sys.argv:
        return selftest()
    if "--launcher" in sys.argv:
        from soilclass.gui import run_launcher_loop
        run_launcher_loop()
        return 0
    from soilclass.gui import run
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
