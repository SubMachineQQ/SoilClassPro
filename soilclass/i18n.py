from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

STORE_DIR = Path.home() / ".soilclasspro"
STORE_FILE = STORE_DIR / "settings.json"

DEFAULT_LANGUAGE = "en"
LANGUAGES = {"en": "English", "tr": "Türkçe"}

_current_language = None


_EN: Dict[str, str] = {
    "file_menu": "Menu",
    "save_project": "Save Project",
    "save_as": "Save As…",
    "open_project": "Open Project…",
    "import_menu": "Import",
    "import_csv": "From CSV / Excel…",
    "import_example": "Load example data",
    "export_menu": "Export",
    "results_export_pdf": "Generate PDF Report",
    "export_ags4": "Export AGS4 data file…",
    "tt_home": "Home",
    "tt_undo": "Undo",
    "tt_compare": "Compare soils",
    "tt_classify": "Classify",
    "launcher_new": "New",
    "launcher_open": "Open",
    "launcher_classification_standard": "Classification standard",
    "launcher_recent_projects": "Recently opened projects",
    "launcher_no_recent": "No recent projects yet.",
    "launcher_no_recent_help": "Choose 'New' for a project covering every "
                              "standard, pick a single standard on the "
                              "left, or use 'Open' to load a saved "
                              ".soilpro file.",
    "launcher_create_project": "Create Project",
    "launcher_project_name": "Project name",
    "launcher_sample_name": "Sample / borehole name",
    "launcher_location": "Location",
    "launcher_tested_by": "Tested by",
    "launcher_date": "Date",
    "launcher_units": "Units",
    "launcher_sieve_set": "Sieve set",
    "launcher_language": "Language",
    "launcher_theme": "Theme",
    "launcher_required_tests": "Required laboratory tests",
    "launcher_required_inputs": "Required inputs",
    "launcher_worth_knowing": "Worth knowing",
    "launcher_back_to_projects": "Back to recent projects",
    "tab_input_data": "Input Data",
    "tab_results": "Results",
    "results_classification_summary": "Classification summary",
    "results_system": "System",
    "results_group_symbol": "Group symbol",
    "results_group_name": "Group name / description",
    "results_decision_trail": "Decision trail / details",
    "input_particle_size": "Particle size",
    "input_percent_passing": "Percent passing",
    "input_liquid_limit": "Liquid Limit",
    "input_plastic_limit": "Plastic Limit",
    "input_non_plastic": "Non-plastic",
    "input_add": "ADD",
    "input_remove": "REMOVE",
    "input_clear": "CLEAR TABLE",
    "compare_title": "Compare soils",
    "compare_add_soils": "Add soils…",
    "compare_remove_selected": "Remove selected",
    "compare_clear": "Clear",
    "compare_boundaries": "Particle size boundaries:",
    "compare_export_pdf": "Export charts to PDF",
    "compare_soils_in_comparison": "Soils in this comparison",
    "dlg_save_project_title": "Save SoilClass Pro project",
    "dlg_open_project_title": "Open SoilClass Pro project",
    "dlg_save_failed": "Save failed",
    "dlg_open_failed": "Could not open project",
    "dlg_unsaved_changes": "Unsaved changes",

    "chart_gsd_title": "Grain Size Distribution",
    "chart_gsd_xlabel": "Particle size (mm)",
    "chart_gsd_ylabel": "Cumulative Percent Passing (%)",
    "chart_gsd_gravel": "Gravel",
    "chart_gsd_sand": "Sand",
    "chart_gsd_fines": "Fines (silt & clay)",
    "chart_gsd_cobbles": "Cobbles",
    "chart_gsd_boulders_cobbles": "Boulders/Cobbles",
    "chart_gsd_silt_clay": "Silt-clay",
    "chart_gsd_clay": "Clay",
    "chart_gsd_silt": "Silt",
    "chart_gsd_boundaries_suffix": "particle size boundaries",
    "chart_astm_title": "Plasticity Chart — USCS (ASTM D2487)",
    "chart_bs_title": "Plasticity Chart — British Standard (BS 5930)",
    "chart_iso14688_title": "Plasticity Chart — TS EN ISO 14688",
    "chart_aashto_title": "AASHTO M 145 — LL–PI Ranges for Silt-Clay Materials",
    "chart_rscs_title": "RSCS ternary chart",
    "chart_xlabel_ll": "Liquid Limit, LL (%)",
    "chart_ylabel_pi": "Plasticity Index, PI (%)",
    "chart_comparison_suffix": "comparison",
    "chart_no_sieve_data": "No sieve data to plot",
    "chart_non_plastic_note": "non-plastic — no Liquid Limit measured, "
                             "nothing to plot here",
    "chart_rscs_gravel_axis": "GRAVEL  [%]",
    "chart_rscs_sand_axis": "SAND  [%]",
    "chart_rscs_fines_axis": "FINES  [%]",
    "chart_rscs_mech_boundary": "Mechanical control boundary",
    "chart_rscs_flow_boundary": "Fluid-flow control boundary",
    "chart_rscs_notable_mixtures": "Notable mixtures 1–13",
    "chart_rscs_gravel_e": "gravel e",
    "chart_rscs_sand_e": "sand e",
    "chart_rscs_letter_gravel": "G",
    "chart_rscs_letter_sand": "S",
    "chart_rscs_letter_fines": "F",
    "chart_a_line": "A-line",
    "chart_aashto_and": "and",
    "chart_or": "or",
    "tb_home": "Reset original view",
    "tb_back": "Back to previous view",
    "tb_forward": "Forward to next view",
    "tb_pan": "Left button pans, right button zooms",
    "tb_zoom": "Zoom to rectangle",
    "tb_subplots": "Configure margins",
    "tb_save": "Save the figure",
    "chart_sample": "Sample",
    "chart_u_line": "U-line",
    "chart_rscsf_ratio_title": "RSCS Fines — Liquid-limit ratio plane (Jang & Santamarina 2016)",
    "chart_rscsf_sens_title": "RSCS Fines — Plasticity vs electrical sensitivity (Jang & Santamarina 2016)",
    "chart_rscsf_sens_xlabel": "Liquid limit using brine, LL$_{brine}$ (corrected)",
    "chart_rscsf_sens_ylabel": "Electrical sensitivity, S$_E$",
    "chart_rscsf_fines": "fines",
    "chart_rscsf_band_legend": "Plasticity band (x):  N non-plastic   ·   L low   ·   I intermediate   ·   H high          Sensitivity band (y):  L low   ·   I intermediate   ·   H high",
    "chart_rscsf_no_data": "{name}: LL with 2-M NaCl brine and with kerosene not measured\n— enter them under 'RSCS parameters' on the Input Data tab to plot this soil",
    "bs_band_low": "low",
    "bs_band_intermediate": "intermediate",
    "bs_band_high": "high",
    "bs_band_very_high": "very high",
    "bs_band_extremely_high": "extremely high",
    "iso_band_low": "low",
    "iso_band_medium": "medium",
    "iso_band_high": "high",
    "iso_band_very_high": "very high",

    "pdf_title": "SOIL CLASSIFICATION REPORT",
    "pdf_sample": "Sample",
    "pdf_project": "Project",
    "pdf_untitled": "Untitled",
    "title_untitled": "Untitled",
    "example_project": "Demo Project - Riverside Embankment",
    "example_location": "Borehole BH-1, depth 3.5 m",
    "example_operator": "Geotechnical Laboratory",
    "title_not_saved": "not saved yet",
    "pdf_location": "Location",
    "pdf_tested_by": "Tested by",
    "pdf_date": "Date",
    "pdf_classification_summary": "Classification summary",
    "pdf_col_system": "System",
    "pdf_col_group_symbol": "Group symbol",
    "pdf_col_group_name": "Group name",
    "pdf_index_properties": "Index properties",
    "pdf_sieve_analysis": "Sieve analysis",
    "pdf_sieve_analysis_continued": "Sieve analysis (continued)",
    "pdf_continued_suffix": "(continued)",
    "pdf_size_mm": "Size (mm)",
    "pdf_passing_pct": "Passing (%)",
    "pdf_decision_trails_title": "Classification details and decision trails",
    "pdf_decision_trails_continued": "Classification details and decision "
                                    "trails (continued)",
    "pdf_generated": "SoilClass Pro — generated",
    "pdf_disclaimer": "Results must be checked by a qualified engineer before use; the software is provided without warranty (MIT License).",
    "pdf_page": "page",
    "res_group_symbol_label": "Group symbol :",
    "res_group_name_label": "Group name   :",
    "res_decision_trail_label": "Decision trail:",
    "res_liquid_limit": "Liquid Limit, LL",
    "res_plastic_limit": "Plastic Limit, PL",
    "res_plasticity_index": "Plasticity Index, PI",
    "res_organic_soil": "Organic soil",
    "res_yes": "Yes",
    "res_no": "No",
    "res_gravel_sand_fines": "Gravel / Sand / Fines",

    "classify_button": "CLASSIFY",
    "results_hero_placeholder": "Run 'Classify' to see results.",
    "results_hero_primary": "Primary group symbol",

    "input_sieve_size": "Sieve Size",
    "input_cumulative_passing": "Cumulative Passing",
    "input_atterberg_box_title": "Atterberg limits",
    "input_organic_soil": "Organic soil",
    "input_non_plastic_tag": "NON-PLASTIC",
    "input_above_a_line": "ABOVE A-LINE",
    "input_a_line_pi": "A-LINE PI =",
    "input_below_a_line": "BELOW A-LINE",
    "rail_points_logged": "Points logged",
    "rail_fractions": "Fractions %",
    "rail_gradation": "Gradation",
    "rail_gravel": "Gravel > 4.75",
    "rail_sand": "Sand 4.75-0.075",
    "rail_fines": "Fines < 0.075",
    "rscs_checkbox_label": "RSCS parameters (packing void ratios and the "
                           "two extra liquid limits) — optional",
    "rscs_help_text": "Give e_min/e_max where measured, otherwise R (0.2 "
                      "angular … 0.9 rounded) and Cu; blank fields "
                      "fall back to documented defaults. LL above is LL "
                      "with deionized water.",
    "rscs_field_gravel_emin": "Gravel  e_min",
    "rscs_field_sand_emin": "Sand  e_min",
    "rscs_field_fines_ll_brine": "Fines  LL_brine (2M NaCl)",
    "rscs_field_or": "or  R",

    "msg_invalid_value_title": "Invalid value",
    "msg_invalid_point_title": "Invalid point",
    "msg_enter_size": "Enter a positive size (mm).",
    "msg_enter_passing": "Enter a passing value between 0 and 100 %.",
    "msg_enter_size_and_passing": "Enter a positive size (mm) and a "
                                  "passing value between 0 and 100 %.",
    "msg_need_two_points": "Enter at least two sieve points (or use "
                           "'Load example').",
    "msg_sieve_contradiction": "Contradiction in sieve data: percent "
                               "passing increases from {p1:g}% at {d1:g} "
                               "mm to {p2:g}% at the finer sieve {d2:g} "
                               "mm. Percent passing cannot increase as "
                               "sieve size decreases - please check "
                               "these two rows.",
    "msg_number_or_blank": "{label} must be a number (or left blank).",
    "msg_out_of_range": "{label} outside a plausible range.",
    "msg_pl_exceeds_ll": "Plastic Limit cannot exceed Liquid Limit.",
    "msg_rscs_must_be_number": "RSCS: {label} must be a number (or left "
                               "blank).",
    "msg_rscs_must_be_positive": "RSCS: {label} must be positive.",
    "msg_rscs_roundness_range": "RSCS: roundness R must lie between 0.05 "
                                "and 1.0.",
    "dlg_import_file_title": "Import sieve data from file",
    "msg_import_title": "Import",
    "import_warn_increasing": "Percent passing increases from {p1} % at {d1} mm to {p2} % at {d2} mm - please verify these rows.",
    "import_warn_pl_gt_ll": "PL > LL was read - please verify the limits.",
    "import_warn_too_few": "Fewer than two sieve points were recognised.",
    "import_warn_openpyxl": "Reading .xlsx files needs the 'openpyxl' package. Alternatively save the sheet as CSV.",
    "import_warn_unreadable": "The file could not be opened as an Excel workbook.",
    "dlg_import_filetypes": "Supported files",
    "dlg_all_files": "All files",
    "import_help_hint": "See Menu > Import > Supported file formats for the layouts SoilClass Pro can read.",
    "import_warn_convert_xlsx": "This file type cannot be read directly. Please save it as Excel (.xlsx) or CSV and import again.",
    "import_warn_xlrd": "Reading old Excel (.xls) files needs the 'xlrd' package. Alternatively save the file as .xlsx.",
    "import_method_passing": "Percent passing read directly from the file.",
    "import_method_cum_ret_pct": "Percent passing calculated as 100 - cumulative % retained.",
    "import_method_ret_pct": "Percent passing calculated from the % retained on each sieve.",
    "import_method_cum_ret_mass": "Percent passing calculated from the cumulative mass retained.",
    "import_method_ret_mass": "Percent passing calculated from the mass retained on each sieve.",
    "import_method_ags": "Read from an AGS file (particle size distribution and Atterberg limit groups).",
    "import_sample": "Sample:",
    "import_samples_found": "{count} samples were found in this file.",
    "import_help_menu": "Supported file formats…",
    "import_save_examples": "Save example files…",
    "import_examples_saved": "The example files were saved to:\n{path}",
    "import_help_title": "Importing data from Excel / CSV",
    "import_help_intro": "SoilClass Pro does not need a fixed template. It looks for the sieve table anywhere in the first visible sheet, recognises Turkish and English headings and works out percent passing from whichever columns the lab sheet contains. The layouts below are all read automatically; the example files can be saved and opened in Excel.",
    "import_help_tips": "•  Column order and heading language do not matter; the table may start in any cell.\n•  Sizes may be given in mm, µm or inches, or as sieve names (No. 200, #4, 3/4\").\n•  Percent passing, % retained, cumulative % retained, mass retained or cumulative mass retained are all accepted; Pan and Total rows are ignored.\n•  Labels such as Sample, Project, Location, Date, LL and PL next to the table are filled in automatically.\n•  Every imported value is shown for review before it is applied - always compare it with the lab sheet.",
    "import_layout_basit_iki_sutun": "Simple two columns",
    "import_layout_basit_iki_sutun_desc": "Sieve opening (mm) and percent passing columns. Label-value pairs above the table (sample name, project, location, date, LL, PL) are read as well.",
    "import_layout_laboratuvar_foyu": "Laboratory sheet",
    "import_layout_laboratuvar_foyu_desc": "Two-row headings, sieve numbers, mass retained, % retained, cumulative % retained and % passing columns, as on a typical TS EN ISO 17892-4 / ASTM D6913 sheet. Pan and Total rows are skipped.",
    "import_layout_sadece_kalan_kutle": "Mass retained only",
    "import_layout_sadece_kalan_kutle_desc": "When only the mass retained on each sieve is given, percent passing is calculated from the total dry mass. If the total is missing, the retained masses and the pan are added up.",
    "import_layout_coklu_numune": "Several samples",
    "import_layout_coklu_numune_desc": "One column per sample next to a shared sieve column. During import the sample to load is chosen from a list.",
    "import_layout_astm_elek_numarasi_en": "ASTM sieve names, English",
    "import_layout_astm_elek_numarasi_en_desc": "Sieve names (#4, #200, 3/4 in) instead of openings and English headings such as Percent Finer. Cells formatted as percentages (98 %) are recognised too.",
    "import_layout_yatay_duzen": "Horizontal layout",
    "import_layout_yatay_duzen_desc": "Sieve openings in one row and percent passing in the row below.",
    "import_layout_noktali_virgul": "Semicolon CSV",
    "import_layout_noktali_virgul_desc": "CSV files saved by Excel with a semicolon separator and decimal commas. Comma- and tab-separated files are supported as well.",
    "import_layout_ags4_ornek": "AGS4 file",
    "import_layout_ags4_ornek_desc": "AGS4 data transfer files: particle size distribution (GRAT / GRAD) and Atterberg limits (LLPL) groups. Every sample in the file can be chosen.",

    "msg_input_error": "Input error",
    "msg_no_classification": "None of the selected systems could classify "
                             "this sample with the data entered so far - "
                             "check the sieve data (a size boundary each "
                             "standard needs may be missing).",
    "status_ready": "READY — load the example or enter your own "
                    "laboratory data.",
    "status_data_changed": "Data changed — press Classify to update "
                           "results and charts.",
    "status_undo_done": "Undid the last change to the sieve table.",
    "status_undo_none": "Nothing to undo.",
    "status_classified": "Classified '{name}'   {symbols}",
    "status_opened_project": "Opened project: {path}",
    "status_project_saved": "Project saved: {path}",
    "dlg_save_pdf_title": "Save PDF report",
    "msg_export_failed": "Export failed",
    "status_pdf_saved": "PDF report saved: {path}",
    "msg_report_created_title": "Report created",
    "msg_report_created_body": "The PDF report was saved to:\n{path}",
    "dlg_export_ags4_title": "Export AGS4 data file",
    "status_ags4_saved": "AGS4 data file saved: {path}",
    "msg_ags4_created_title": "AGS4 file created",
    "msg_ags4_created_body": "The AGS4 data file was saved to:\n{path}"
                             "\n\nThis is a best-effort, single-sample "
                             "export - validate it with the AGS4 Data "
                             "Format Checker before relying on it for a "
                             "formal submittal.",
    "msg_unsaved_body": "This project has unsaved changes.\n\nSave "
                        "before {what}?\n\nYes = save, No = discard, "
                        "Cancel = stay here.",
    "confirm_closing": "closing",
    "confirm_returning_home": "returning to the start screen",

    "launcher_window_title": "Start a project",
    "launcher_workspace": "WORKSPACE",
    "launcher_session_start": "SESSION START",
    "launcher_dossier": "DOCUMENT",
    "launcher_dossiers": "DOCUMENTS",
    "launcher_resume_or_start": "RESUME OR START A NEW RUN",
    "launcher_open_arrow": "OPEN ›",
    "launcher_moisture_footer": "MOISTURE MODULE LINKED  ·  SIEVE "
                                "SET ASTM E11  ·  UNITS SI",
    "launcher_sieve_note": "Sieve data and Atterberg limits are entered "
                          "on the next screen.",
    "launcher_all_standards": "All Standards",
    "launcher_new_project": "New Project",
    "launcher_group_caption": "Group",
    "launcher_group_no_data": "NO DATA",
    "launcher_group_ready": "READY",
    "launcher_opened_prefix": "OPENED",
    "launcher_file_not_found": "FILE NOT FOUND",
    "pill_active": "ACTIVE",
    "pill_review": "REVIEW",
    "pill_signed": "SIGNED",
    "launcher_samples_caption": "Samples",
    "launcher_standard_placeholder": "PROJECT",

    "splash_version": "Version {version}",
    "splash_copyright": "© 2026  ·  MIT License",
    "splash_thanks": "Thank you for using SoilClass Pro!",
    "welcome_title": 'Welcome',
    "welcome_thanks": 'Thank you for using SoilClass Pro!',
    "welcome_thanks_body": 'SoilClass Pro is a free, open-source tool that classifies a soil according to USCS, BS 5930, TS EN ISO 14688, AASHTO and the Revised Soil Classification System (RSCS) from a single set of laboratory data.',
    "welcome_developers": 'Developed by',
    "welcome_institution": 'Middle East Technical University (METU), Department of Civil Engineering',
    "acknowledgement": "With special thanks to {name} for the guidance and support.",
    "welcome_disclaimer_title": 'Disclaimer',
    "welcome_disclaimer": 'SoilClass Pro is an auxiliary tool intended for education and research. Its results depend solely on the data entered and on how the standards are implemented in the software, and they may be incorrect or incomplete. Classification results must not be used in design, construction or official reports without being checked by a qualified engineer against the governing standards. The software is provided "as is" under the MIT License, without warranty of any kind. The developers accept no legal liability for any direct or indirect damage arising from the use of the software or from an incorrect classification. By continuing you accept these terms.',
    "welcome_license": 'Open-source software released under the MIT License. Source code and updates are published on GitHub.',
    "welcome_accept": 'I have read and accept',
    "welcome_exit": 'Exit',
    "about_menu": 'About SoilClass Pro',
    "about_close": 'Close',
    "update_available": 'New version v{version} available - click to download',

    "import_review_title": "Review imported data — {source}",
    "import_review_source_default": "import",
    "import_review_instructions": "Check every value against the paper. "
                                  "Double-click a cell to edit it.",
    "import_review_size_col": "Particle size (mm)",
    "import_review_passing_col": "Percent passing (%)",
    "import_review_delete_rows": "Delete selected row(s)",
    "import_review_ll": "LL (%):",
    "import_review_pl": "PL (%):",
    "import_review_cancel": "Cancel",
    "import_review_apply": "Apply to input table",
    "import_review_not_enough_title": "Not enough data",
    "import_review_not_enough_body": "At least two valid sieve points "
                                     "are needed.",

    "compare_add_dialog_title": "Add soils to the comparison",
    "compare_some_failed_title": "Some files could not be opened",
    "compare_nothing_to_export_title": "Nothing to export",
    "compare_save_charts_title": "Save comparison charts",
    "compare_export_failed_title": "Export failed",
    "compare_charts_exported_title": "Charts exported",
    "compare_col_soil": "Soil",
    "compare_col_source": "File",
    "compare_unnamed": "(unnamed)",
    "compare_current_project": "current project",
    "compare_chart_gsd": "Grain Size (all soils)",
    "compare_chart_astm": "Plasticity ASTM (all soils)",
    "compare_chart_bs": "Plasticity BS (all soils)",
    "compare_nothing_to_export_body": "Add at least one soil first.",
    "compare_charts_exported_body": "Comparison charts saved to:\n{path}",

    "mode_bs": "British Standard (BS 5930)",
    "status_units_si": "UNITS SI",
    "chart_tab_grain_size": "Grain Size",
    "chart_tab_plasticity_astm": "Plasticity (ASTM)",
    "chart_tab_plasticity_bs": "Plasticity (BS)",
    "chart_tab_plasticity_iso14688": "Plasticity (ISO 14688)",
    "chart_tab_aashto": "AASHTO Chart",
    "chart_tab_rscs_ternary": "RSCS Ternary",
    "chart_tab_rscs_fines_a": "RSCS Fines (a)",
    "chart_tab_rscs_fines_b": "RSCS Fines (b)",
}

_TR: Dict[str, str] = {
    "file_menu": "Menü",
    "save_project": "Projeyi Kaydet",
    "save_as": "Farklı Kaydet…",
    "open_project": "Proje Aç…",
    "import_menu": "İçe Aktar",
    "import_csv": "CSV / Excel'den…",
    "import_example": "Örnek veriyi yükle",
    "export_menu": "Dışa Aktar",
    "results_export_pdf": "PDF Rapor Oluştur",
    "export_ags4": "AGS4 veri dosyası olarak dışa aktar…",
    "tt_home": "Ana Sayfa",
    "tt_undo": "Geri Al",
    "tt_compare": "Zeminleri karşılaştır",
    "tt_classify": "Sınıflandır",
    "launcher_new": "Yeni",
    "launcher_open": "Aç",
    "launcher_classification_standard": "Sınıflandırma standardı",
    "launcher_recent_projects": "Son açılan projeler",
    "launcher_no_recent": "Henüz son kullanılan proje yok.",
    "launcher_no_recent_help": "Her standardı kapsayan bir proje için "
                              "'Yeni'yi, tek bir standart için soldaki "
                              "seçeneklerden birini seçin, ya da "
                              "kaydedilmiş bir .soilpro dosyasını açmak "
                              "için 'Aç'ı kullanın.",
    "launcher_create_project": "Proje Oluştur",
    "launcher_project_name": "Proje adı",
    "launcher_sample_name": "Numune / sondaj adı",
    "launcher_location": "Konum",
    "launcher_tested_by": "Deneyi yapan",
    "launcher_date": "Tarih",
    "launcher_units": "Birimler",
    "launcher_sieve_set": "Elek seti",
    "launcher_language": "Dil",
    "launcher_theme": "Tema",
    "launcher_required_tests": "Gerekli laboratuvar deneyleri",
    "launcher_required_inputs": "Gerekli girdiler",
    "launcher_worth_knowing": "Bilinmesi gerekenler",
    "launcher_back_to_projects": "Son projelere dön",
    "tab_input_data": "Veri Girişi",
    "tab_results": "Sonuçlar",
    "results_classification_summary": "Sınıflandırma özeti",
    "results_system": "Sistem",
    "results_group_symbol": "Grup sembolü",
    "results_group_name": "Grup adı / açıklama",
    "results_decision_trail": "Karar izlemesi / detaylar",
    "input_particle_size": "Dane boyutu",
    "input_percent_passing": "Geçen yüzde",
    "input_liquid_limit": "Likit Limit",
    "input_plastic_limit": "Plastik Limit",
    "input_non_plastic": "Plastik değil",
    "input_add": "EKLE",
    "input_remove": "KALDIR",
    "input_clear": "TABLOYU SİL",
    "compare_title": "Zeminleri karşılaştır",
    "compare_add_soils": "Zemin ekle…",
    "compare_remove_selected": "Seçileni kaldır",
    "compare_clear": "Temizle",
    "compare_boundaries": "Dane boyutu sınırları:",
    "compare_export_pdf": "Grafikleri PDF'e aktar",
    "compare_soils_in_comparison": "Karşılaştırmadaki zeminler",
    "dlg_save_project_title": "SoilClass Pro projesini kaydet",
    "dlg_open_project_title": "SoilClass Pro projesi aç",
    "dlg_save_failed": "Kaydetme başarısız",
    "dlg_open_failed": "Proje açılamadı",
    "dlg_unsaved_changes": "Kaydedilmemiş değişiklikler",

    "chart_gsd_title": "Dane Dağılımı Eğrisi",
    "chart_gsd_xlabel": "Dane boyutu (mm)",
    "chart_gsd_ylabel": "Kümülatif Geçen Yüzde (%)",
    "chart_gsd_gravel": "Çakıl",
    "chart_gsd_sand": "Kum",
    "chart_gsd_fines": "İnce dane (silt & kil)",
    "chart_gsd_cobbles": "Kaya parçası",
    "chart_gsd_boulders_cobbles": "Blok/Kaya parçası",
    "chart_gsd_silt_clay": "Silt-kil",
    "chart_gsd_clay": "Kil",
    "chart_gsd_silt": "Silt",
    "chart_gsd_boundaries_suffix": "dane boyutu sınırları",
    "chart_astm_title": "Plastisite Grafiği — USCS (ASTM D2487)",
    "chart_bs_title": "Plastisite Grafiği — İngiliz Standardı (BS 5930)",
    "chart_iso14688_title": "Plastisite Grafiği — TS EN ISO 14688",
    "chart_aashto_title": "AASHTO M 145 — Siltli-Killi Malzemeler için LL–PI Aralıkları",
    "chart_rscs_title": "RSCS üçgen diyagramı",
    "chart_xlabel_ll": "Likit Limit, LL (%)",
    "chart_ylabel_pi": "Plastisite İndisi, PI (%)",
    "chart_comparison_suffix": "karşılaştırma",
    "chart_no_sieve_data": "Çizilecek elek verisi yok",
    "chart_non_plastic_note": "plastik değil — Likit Limit ölçülmedi, "
                             "burada çizilecek bir şey yok",
    "chart_rscs_gravel_axis": "ÇAKIL  [%]",
    "chart_rscs_sand_axis": "KUM  [%]",
    "chart_rscs_fines_axis": "İNCE DANE  [%]",
    "chart_rscs_mech_boundary": "Mekanik kontrol sınırı",
    "chart_rscs_flow_boundary": "Akışkan akışı kontrol sınırı",
    "chart_rscs_notable_mixtures": "Belirgin karışımlar 1–13",
    "chart_rscs_gravel_e": "çakıl e",
    "chart_rscs_sand_e": "kum e",
    "chart_rscs_letter_gravel": "Ç",
    "chart_rscs_letter_sand": "K",
    "chart_rscs_letter_fines": "İ",
    "chart_a_line": "A-hattı",
    "chart_aashto_and": "ve",
    "chart_or": "veya",
    "tb_home": "Başlangıç görünümüne dön",
    "tb_back": "Önceki görünüm",
    "tb_forward": "Sonraki görünüm",
    "tb_pan": "Sol tuş kaydırır, sağ tuş yakınlaştırır",
    "tb_zoom": "Dikdörtgen seçerek yakınlaştır",
    "tb_subplots": "Kenar boşluklarını ayarla",
    "tb_save": "Grafiği kaydet",
    "chart_sample": "Numune",
    "chart_u_line": "U-hattı",
    "chart_rscsf_ratio_title": "RSCS İnce Daneler — Likit limit oranları düzlemi (Jang ve Santamarina 2016)",
    "chart_rscsf_sens_title": "RSCS İnce Daneler — Plastisite ve elektriksel duyarlılık (Jang ve Santamarina 2016)",
    "chart_rscsf_sens_xlabel": "Tuzlu su ile likit limit, LL$_{brine}$ (düzeltilmiş)",
    "chart_rscsf_sens_ylabel": "Elektriksel duyarlılık, S$_E$",
    "chart_rscsf_fines": "ince dane",
    "chart_rscsf_band_legend": "Plastisite bandı (x):  N plastik değil   ·   L düşük   ·   I orta   ·   H yüksek          Duyarlılık bandı (y):  L düşük   ·   I orta   ·   H yüksek",
    "chart_rscsf_no_data": "{name}: 2-M NaCl tuzlu su ve gazyağı ile likit limit ölçülmemiş\n— bu zemini çizmek için Veri Girişi sekmesindeki 'RSCS parametreleri' bölümüne girin",
    "bs_band_low": "düşük",
    "bs_band_intermediate": "orta",
    "bs_band_high": "yüksek",
    "bs_band_very_high": "çok yüksek",
    "bs_band_extremely_high": "aşırı yüksek",
    "iso_band_low": "düşük",
    "iso_band_medium": "orta",
    "iso_band_high": "yüksek",
    "iso_band_very_high": "çok yüksek",

    "pdf_title": "ZEMİN SINIFLANDIRMA RAPORU",
    "pdf_sample": "Numune",
    "pdf_project": "Proje",
    "pdf_untitled": "İsimsiz",
    "pdf_location": "Konum",
    "pdf_tested_by": "Deneyi yapan",
    "pdf_date": "Tarih",
    "pdf_classification_summary": "Sınıflandırma özeti",
    "pdf_col_system": "Sistem",
    "pdf_col_group_symbol": "Grup sembolü",
    "pdf_col_group_name": "Grup adı",
    "pdf_index_properties": "İndis özellikleri",
    "pdf_sieve_analysis": "Elek analizi",
    "pdf_sieve_analysis_continued": "Elek analizi (devamı)",
    "pdf_continued_suffix": "(devamı)",
    "pdf_size_mm": "Boyut (mm)",
    "pdf_passing_pct": "Geçen (%)",
    "pdf_decision_trails_title": "Sınıflandırma detayları ve karar izlemeleri",
    "pdf_decision_trails_continued": "Sınıflandırma detayları ve karar "
                                    "izlemeleri (devamı)",
    "pdf_generated": "SoilClass Pro — oluşturulma",
    "title_untitled": "Adsız proje",
    "example_project": "Örnek Proje - Nehir Kenarı Dolgusu",
    "example_location": "BH-1 sondajı, 3,5 m derinlik",
    "example_operator": "Geoteknik Laboratuvarı",
    "title_not_saved": "kaydedilmedi",
    "pdf_disclaimer": "Sonuçlar kullanılmadan önce yetkin bir mühendis tarafından kontrol edilmelidir; yazılım garanti verilmeksizin sunulur (MIT Lisansı).",
    "pdf_page": "sayfa",
    "res_group_symbol_label": "Grup sembolü :",
    "res_group_name_label": "Grup adı     :",
    "res_decision_trail_label": "Karar izlemesi:",
    "res_liquid_limit": "Likit Limit, LL",
    "res_plastic_limit": "Plastik Limit, PL",
    "res_plasticity_index": "Plastisite İndisi, PI",
    "res_organic_soil": "Organik zemin",
    "res_yes": "Evet",
    "res_no": "Hayır",
    "res_gravel_sand_fines": "Çakıl / Kum / İnce dane",

    "classify_button": "SINIFLANDIR",
    "results_hero_placeholder": "Sonuçları görmek için 'Sınıflandır'a basın.",
    "results_hero_primary": "Ana grup sembolü",

    "input_sieve_size": "Elek Boyutu",
    "input_cumulative_passing": "Kümülatif Geçen",
    "input_atterberg_box_title": "Atterberg limitleri",
    "input_organic_soil": "Organik zemin",
    "input_non_plastic_tag": "PLASTİK DEĞİL",
    "input_above_a_line": "A-HATTI ÜZERİNDE",
    "input_a_line_pi": "A-HATTI PI =",
    "input_below_a_line": "A-HATTI ALTINDA",
    "rail_points_logged": "Kayıtlı nokta",
    "rail_fractions": "Fraksiyonlar %",
    "rail_gradation": "Derecelenme",
    "rail_gravel": "Çakıl > 4,75",
    "rail_sand": "Kum 4,75-0,075",
    "rail_fines": "İnce dane < 0,075",
    "rscs_checkbox_label": "RSCS parametreleri (paketleme boşluk oranları "
                           "ve iki ek likit limit) — isteğe bağlı",
    "rscs_help_text": "Ölçüldüyse e_min/e_max verin, aksi halde R (0,2 "
                      "köşeli … 0,9 yuvarlak) ve Cu girin; boş bırakılan "
                      "alanlar belgelenmiş varsayılanlara döner. "
                      "Yukarıdaki LL, deiyonize su ile ölçülen LL'dir.",
    "rscs_field_gravel_emin": "Çakıl  e_min",
    "rscs_field_sand_emin": "Kum  e_min",
    "rscs_field_fines_ll_brine": "İnce dane  LL_tuzlusu (2M NaCl)",
    "rscs_field_or": "veya  R",

    "msg_invalid_value_title": "Geçersiz değer",
    "msg_invalid_point_title": "Geçersiz nokta",
    "msg_enter_size": "Pozitif bir boyut (mm) girin.",
    "msg_enter_passing": "0 ile 100 % arasında bir geçen değeri girin.",
    "msg_enter_size_and_passing": "Pozitif bir boyut (mm) ve 0 ile 100 % "
                                  "arasında bir geçen değeri girin.",
    "msg_need_two_points": "En az iki elek noktası girin (veya 'Örnek "
                           "veriyi yükle'yi kullanın).",
    "msg_sieve_contradiction": "Elek verisinde çelişki: geçen yüzde, "
                               "{d1:g} mm'de %{p1:g} iken daha ince elek "
                               "{d2:g} mm'de %{p2:g}'e yükseliyor. Elek "
                               "boyutu küçüldükçe geçen yüzde artamaz - "
                               "lütfen bu iki satırı kontrol edin.",
    "msg_number_or_blank": "{label} bir sayı olmalı (veya boş bırakın).",
    "msg_out_of_range": "{label} makul bir aralığın dışında.",
    "msg_pl_exceeds_ll": "Plastik Limit, Likit Limiti aşamaz.",
    "msg_rscs_must_be_number": "RSCS: {label} bir sayı olmalı (veya boş "
                               "bırakın).",
    "msg_rscs_must_be_positive": "RSCS: {label} pozitif olmalı.",
    "msg_rscs_roundness_range": "RSCS: yuvarlaklık R değeri 0,05 ile 1,0 "
                                "arasında olmalı.",
    "dlg_import_file_title": "Dosyadan elek verisi içe aktar",
    "msg_import_title": "İçe aktarma",
    "import_warn_increasing": "Geçen yüzde {d1} mm'de %{p1} iken {d2} mm'de %{p2} değerine yükseliyor - lütfen bu satırları kontrol edin.",
    "import_warn_pl_gt_ll": "PL > LL okundu - lütfen kıvam limitlerini kontrol edin.",
    "import_warn_too_few": "İkiden az elek noktası tanınabildi.",
    "import_warn_openpyxl": ".xlsx dosyalarını okumak için 'openpyxl' paketi gerekir. Alternatif olarak sayfayı CSV olarak kaydedin.",
    "import_warn_unreadable": "Dosya bir Excel çalışma kitabı olarak açılamadı.",
    "dlg_import_filetypes": "Desteklenen dosyalar",
    "dlg_all_files": "Tüm dosyalar",
    "import_help_hint": "SoilClass Pro'nun okuyabildiği düzenler için Menü > İçe Aktar > Desteklenen dosya biçimleri bölümüne bakın.",
    "import_warn_convert_xlsx": "Bu dosya türü doğrudan okunamıyor. Lütfen dosyayı Excel (.xlsx) veya CSV olarak kaydedip tekrar içe aktarın.",
    "import_warn_xlrd": "Eski Excel (.xls) dosyalarını okumak için 'xlrd' paketi gerekir. Alternatif olarak dosyayı .xlsx olarak kaydedin.",
    "import_method_passing": "Geçen yüzde doğrudan dosyadan okundu.",
    "import_method_cum_ret_pct": "Geçen yüzde, 100 - kümülatif kalan (%) olarak hesaplandı.",
    "import_method_ret_pct": "Geçen yüzde, her elekte kalan yüzdeden hesaplandı.",
    "import_method_cum_ret_mass": "Geçen yüzde, kümülatif kalan kütleden hesaplandı.",
    "import_method_ret_mass": "Geçen yüzde, her elekte kalan kütleden hesaplandı.",
    "import_method_ags": "AGS dosyasından okundu (tane dağılımı ve kıvam limitleri grupları).",
    "import_sample": "Numune:",
    "import_samples_found": "Bu dosyada {count} numune bulundu.",
    "import_help_menu": "Desteklenen dosya biçimleri…",
    "import_save_examples": "Örnek dosyaları kaydet…",
    "import_examples_saved": "Örnek dosyalar şu klasöre kaydedildi:\n{path}",
    "import_help_title": "Excel / CSV'den veri içe aktarma",
    "import_help_intro": "SoilClass Pro sabit bir şablon istemez. İlk görünür sayfada elek tablosunu nerede olursa olsun bulur, Türkçe ve İngilizce başlıkları tanır ve laboratuvar föyünde hangi sütunlar varsa geçen yüzdeyi onlardan hesaplar. Aşağıdaki düzenlerin hepsi otomatik okunur; örnek dosyaları kaydedip Excel'de açabilirsiniz.",
    "import_help_tips": "•  Sütun sırası ve başlık dili önemli değildir; tablo herhangi bir hücreden başlayabilir.\n•  Boyutlar mm, µm veya inç ya da elek adı (No. 200, #4, 3/4\") olarak verilebilir.\n•  Geçen %, kalan %, kümülatif kalan %, kalan kütle veya kümülatif kalan kütle sütunlarının hepsi kabul edilir; Tava ve Toplam satırları yok sayılır.\n•  Tablonun yanındaki Numune, Proje, Konum, Tarih, LL ve PL gibi etiketler otomatik doldurulur.\n•  İçe aktarılan her değer uygulanmadan önce kontrol için gösterilir - mutlaka deney föyüyle karşılaştırın.",
    "import_layout_basit_iki_sutun": "Basit iki sütun",
    "import_layout_basit_iki_sutun_desc": "Elek açıklığı (mm) ve geçen yüzde sütunları. Tablonun üstündeki etiket-değer çiftleri (numune adı, proje, konum, tarih, LL, PL) de okunur.",
    "import_layout_laboratuvar_foyu": "Laboratuvar föyü",
    "import_layout_laboratuvar_foyu_desc": "Tipik bir TS EN ISO 17892-4 / ASTM D6913 föyündeki gibi iki satırlı başlıklar, elek numaraları, kalan kütle, kalan %, kümülatif kalan % ve geçen % sütunları. Tava ve Toplam satırları atlanır.",
    "import_layout_sadece_kalan_kutle": "Yalnızca kalan kütle",
    "import_layout_sadece_kalan_kutle_desc": "Sadece her elekte kalan kütle verildiğinde geçen yüzde toplam kuru kütleden hesaplanır. Toplam kütle yoksa kalan kütleler ve tava toplanır.",
    "import_layout_coklu_numune": "Birden çok numune",
    "import_layout_coklu_numune_desc": "Ortak bir elek sütununun yanında her numune için ayrı bir sütun. İçe aktarırken yüklenecek numune listeden seçilir.",
    "import_layout_astm_elek_numarasi_en": "ASTM elek adları, İngilizce",
    "import_layout_astm_elek_numarasi_en_desc": "Göz açıklığı yerine elek adları (#4, #200, 3/4 in) ve Percent Finer gibi İngilizce başlıklar. Yüzde biçimli hücreler (%98) de tanınır.",
    "import_layout_yatay_duzen": "Yatay düzen",
    "import_layout_yatay_duzen_desc": "Elek açıklıkları bir satırda, geçen yüzdeler hemen alt satırda.",
    "import_layout_noktali_virgul": "Noktalı virgüllü CSV",
    "import_layout_noktali_virgul_desc": "Türkçe Excel'in noktalı virgül ayraçlı ve virgül ondalıklı kaydettiği CSV dosyaları. Virgül ve sekme ayraçlı dosyalar da desteklenir.",
    "import_layout_ags4_ornek": "AGS4 dosyası",
    "import_layout_ags4_ornek_desc": "AGS4 veri aktarım dosyaları: tane dağılımı (GRAT / GRAD) ve kıvam limitleri (LLPL) grupları. Dosyadaki her numune seçilebilir.",

    "msg_input_error": "Girdi hatası",
    "msg_no_classification": "Seçili sistemlerin hiçbiri, şu ana kadar "
                             "girilen verilerle bu numuneyi "
                             "sınıflandıramadı - elek verisini kontrol "
                             "edin (her standardın ihtiyaç duyduğu bir "
                             "boyut sınırı eksik olabilir).",
    "status_ready": "HAZIR — örneği yükleyin veya kendi laboratuvar "
                    "verinizi girin.",
    "status_data_changed": "Veri değişti — sonuçları ve grafikleri "
                           "güncellemek için Sınıflandır'a basın.",
    "status_undo_done": "Elek tablosundaki son değişiklik geri alındı.",
    "status_undo_none": "Geri alınacak bir şey yok.",
    "status_classified": "'{name}' sınıflandırıldı   {symbols}",
    "status_opened_project": "Proje açıldı: {path}",
    "status_project_saved": "Proje kaydedildi: {path}",
    "dlg_save_pdf_title": "PDF raporunu kaydet",
    "msg_export_failed": "Dışa aktarma başarısız",
    "status_pdf_saved": "PDF raporu kaydedildi: {path}",
    "msg_report_created_title": "Rapor oluşturuldu",
    "msg_report_created_body": "PDF raporu şuraya kaydedildi:\n{path}",
    "dlg_export_ags4_title": "AGS4 veri dosyasını dışa aktar",
    "status_ags4_saved": "AGS4 veri dosyası kaydedildi: {path}",
    "msg_ags4_created_title": "AGS4 dosyası oluşturuldu",
    "msg_ags4_created_body": "AGS4 veri dosyası şuraya kaydedildi:"
                             "\n{path}\n\nBu, tek numune için hazırlanmış "
                             "en iyi çaba dışa aktarımıdır - resmi bir "
                             "sunumda kullanmadan önce AGS4 Veri Formatı "
                             "Denetleyicisi ile doğrulayın.",
    "msg_unsaved_body": "Bu projede kaydedilmemiş değişiklikler var."
                        "\n\n{what} önce kaydedilsin mi?\n\nEvet = "
                        "kaydet, Hayır = değişiklikleri at, İptal = "
                        "burada kal.",
    "confirm_closing": "kapatmadan",
    "confirm_returning_home": "başlangıç ekranına dönmeden",

    "launcher_window_title": "Bir proje başlat",
    "launcher_workspace": "ÇALIŞMA ALANI",
    "launcher_session_start": "OTURUM BAŞLANGICI",
    "launcher_dossier": "DOSYA",
    "launcher_dossiers": "DOSYA",
    "launcher_resume_or_start": "DEVAM EDİN YA DA YENİ BİR ÇALIŞMA BAŞLATIN",
    "launcher_open_arrow": "AÇ ›",
    "launcher_moisture_footer": "NEM MODÜLÜ BAĞLI  ·  ELEK SETİ ASTM "
                                "E11  ·  BİRİMLER SI",
    "launcher_sieve_note": "Elek verileri ve Atterberg limitleri bir "
                          "sonraki ekranda girilir.",
    "launcher_all_standards": "Tüm Standartlar",
    "launcher_new_project": "Yeni Proje",
    "launcher_group_caption": "Grup",
    "launcher_group_no_data": "VERİ YOK",
    "launcher_group_ready": "HAZIR",
    "launcher_opened_prefix": "AÇILDI",
    "launcher_file_not_found": "DOSYA BULUNAMADI",
    "pill_active": "AKTİF",
    "pill_review": "İNCELEME",
    "pill_signed": "ONAYLI",
    "launcher_samples_caption": "Numune",
    "launcher_standard_placeholder": "PROJE",

    "splash_version": "Sürüm {version}",
    "splash_copyright": "© 2026  ·  MIT Lisansı",
    "splash_thanks": "SoilClass Pro'yu kullandığınız için teşekkür ederiz!",
    "welcome_title": 'Hoş geldiniz',
    "welcome_thanks": "SoilClass Pro'yu kullandığınız için teşekkür ederiz!",
    "welcome_thanks_body": "SoilClass Pro, tek bir laboratuvar veri setinden bir zemini USCS, BS 5930, TS EN ISO 14688, AASHTO ve Revize Zemin Sınıflandırma Sistemi'ne (RSCS) göre sınıflandıran ücretsiz ve açık kaynak bir araçtır.",
    "welcome_developers": 'Geliştirenler',
    "welcome_institution": 'Orta Doğu Teknik Üniversitesi (ODTÜ), İnşaat Mühendisliği Bölümü',
    "acknowledgement": "Rehberliği ve desteği için {name} hocamıza teşekkür ederiz.",
    "welcome_disclaimer_title": 'Sorumluluk reddi',
    "welcome_disclaimer": 'SoilClass Pro eğitim ve araştırma amaçlı, yardımcı bir araçtır. Sonuçlar yalnızca girilen verilere ve standartların yazılımdaki uygulanış biçimine dayanır; hatalı veya eksik olabilir. Sınıflandırma sonuçları, ilgili standartlara göre yetkin bir mühendis tarafından kontrol edilmeden tasarım, uygulama veya resmi raporlarda kullanılmamalıdır. Yazılım, MIT Lisansı kapsamında "olduğu gibi" ve hiçbir garanti verilmeksizin sunulur. Geliştiriciler, yazılımın kullanımından ya da hatalı bir sınıflandırmadan doğabilecek doğrudan veya dolaylı hiçbir zarardan hukuken sorumlu tutulamaz. Devam ederek bu koşulları kabul etmiş olursunuz.',
    "welcome_license": "MIT Lisansı ile yayımlanan açık kaynak bir yazılımdır. Kaynak kodu ve güncellemeler GitHub'da yayımlanır.",
    "welcome_accept": 'Okudum, kabul ediyorum',
    "welcome_exit": 'Çıkış',
    "about_menu": 'SoilClass Pro Hakkında',
    "about_close": 'Kapat',
    "update_available": 'Yeni sürüm v{version} mevcut - indirmek için tıklayın',

    "import_review_title": "İçe aktarılan veriyi gözden geçir — {source}",
    "import_review_source_default": "içe aktarma",
    "import_review_instructions": "Her değeri kağıtla karşılaştırarak "
                                  "kontrol edin. Bir hücreyi düzenlemek "
                                  "için çift tıklayın.",
    "import_review_size_col": "Dane boyutu (mm)",
    "import_review_passing_col": "Geçen yüzde (%)",
    "import_review_delete_rows": "Seçili satır(lar)ı sil",
    "import_review_ll": "LL (%):",
    "import_review_pl": "PL (%):",
    "import_review_cancel": "İptal",
    "import_review_apply": "Giriş tablosuna uygula",
    "import_review_not_enough_title": "Yetersiz veri",
    "import_review_not_enough_body": "En az iki geçerli elek noktası "
                                     "gerekli.",

    "compare_add_dialog_title": "Karşılaştırmaya zemin ekle",
    "compare_some_failed_title": "Bazı dosyalar açılamadı",
    "compare_nothing_to_export_title": "Dışa aktarılacak bir şey yok",
    "compare_save_charts_title": "Karşılaştırma grafiklerini kaydet",
    "compare_export_failed_title": "Dışa aktarma başarısız",
    "compare_charts_exported_title": "Grafikler dışa aktarıldı",
    "compare_col_soil": "Zemin",
    "compare_col_source": "Dosya",
    "compare_unnamed": "(isimsiz)",
    "compare_current_project": "geçerli proje",
    "compare_chart_gsd": "Dane Dağılımı (tüm zeminler)",
    "compare_chart_astm": "Plastisite ASTM (tüm zeminler)",
    "compare_chart_bs": "Plastisite BS (tüm zeminler)",
    "compare_nothing_to_export_body": "Önce en az bir zemin ekleyin.",
    "compare_charts_exported_body": "Karşılaştırma grafikleri şuraya "
                                    "kaydedildi:\n{path}",

    "mode_bs": "İngiliz Standardı (BS 5930)",
    "status_units_si": "BİRİMLER SI",
    "chart_tab_grain_size": "Dane Dağılımı",
    "chart_tab_plasticity_astm": "Plastisite (ASTM)",
    "chart_tab_plasticity_bs": "Plastisite (BS)",
    "chart_tab_plasticity_iso14688": "Plastisite (ISO 14688)",
    "chart_tab_aashto": "AASHTO Grafiği",
    "chart_tab_rscs_ternary": "RSCS Üçgen",
    "chart_tab_rscs_fines_a": "RSCS İnce Dane (a)",
    "chart_tab_rscs_fines_b": "RSCS İnce Dane (b)",
}

_TABLES = {"en": _EN, "tr": _TR}


def get_language() -> str:
    global _current_language
    if _current_language is None:
        try:
            data = json.loads(STORE_FILE.read_text(encoding="utf-8"))
            lang = data.get("language", DEFAULT_LANGUAGE)
        except (OSError, ValueError):
            lang = DEFAULT_LANGUAGE
        _current_language = lang if lang in LANGUAGES else DEFAULT_LANGUAGE
    return _current_language


def set_language(code: str) -> None:
    global _current_language
    if code not in LANGUAGES:
        raise ValueError(f"Unknown language code: {code!r}")
    _current_language = code
    try:
        STORE_DIR.mkdir(parents=True, exist_ok=True)
        existing = {}
        try:
            existing = json.loads(STORE_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
        existing["language"] = code
        STORE_FILE.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    except OSError:
        pass


def t(key: str) -> str:
    lang = get_language()
    table = _TABLES.get(lang, _EN)
    return table.get(key, _EN.get(key, key))


import re as _re

_EXACT_TR: Dict[str, str] = {
    "Excellent to good subgrade (stone fragments, gravel, sand)":
        "Mükemmel ile iyi taban zemini (taş parçaları, çakıl, kum)",
    "Excellent to good subgrade (fine sand)":
        "Mükemmel ile iyi taban zemini (ince kum)",
    "Excellent to good subgrade (silty or clayey gravel and sand)":
        "Mükemmel ile iyi taban zemini (siltli veya killi çakıl ve kum)",
    "Fair to poor subgrade (silty soil)":
        "Orta ile zayıf taban zemini (siltli zemin)",
    "Fair to poor subgrade (clayey soil)":
        "Orta ile zayıf taban zemini (killi zemin)",
    "Group Index": "Grup İndisi",
    "Gravel-controlled; gravel controls fluid flow":
        "Çakıl kontrollü; akışkan akışını çakıl kontrol eder",
    "Gravel and sand carry the load; sand controls fluid flow":
        "Çakıl ve kum yükü taşır; akışkan akışını kum kontrol eder",
    "Sand-controlled; sand controls fluid flow":
        "Kum kontrollü; akışkan akışını kum kontrol eder",
    "Gravel carries the load; fines control fluid flow":
        "Çakıl yükü taşır; akışkan akışını ince dane kontrol eder",
    "Gravel and sand carry the load; fines control fluid flow":
        "Çakıl ve kum yükü taşır; akışkan akışını ince dane kontrol eder",
    "Sand carries the load; fines control fluid flow":
        "Kum yükü taşır; akışkan akışını ince dane kontrol eder",
    "Transitional: gravel and fines carry the load; fines control flow":
        "Geçiş bölgesi: çakıl ve ince dane yükü taşır; akışı ince dane kontrol eder",
    "Transitional: all three fractions carry the load; fines control flow":
        "Geçiş bölgesi: her üç fraksiyon da yükü taşır; akışı ince dane kontrol eder",
    "Transitional: sand and fines carry the load; fines control flow":
        "Geçiş bölgesi: kum ve ince dane yükü taşır; akışı ince dane kontrol eder",
    "Fines-controlled; fines control both load and fluid flow":
        "İnce dane kontrollü; hem yükü hem akışkan akışını ince dane kontrol eder",
    "Insufficient data": "Yetersiz veri",
    "Mechanical control": "Mekanik kontrol",
    "Fluid flow control": "Akışkan akışı kontrolü",
    "Electrical sensitivity, SE": "Elektriksel duyarlılık, SE",
    "LL_brine (corrected)": "LL_tuzlu su (düzeltilmiş)",
    "Fines group": "İnce dane grubu",
}

_PHRASE_TABLE = [
    ("lambda = 1: the flow boundary coincides with the mechanical "
     "boundary, so the G(F), GS(F) and S(F) groups do not exist for "
     "these fines.",
     "lambda = 1: akış sınırı mekanik sınırla çakışıyor, bu yüzden bu "
     "ince daneler için G(F), GS(F) ve S(F) grupları mevcut değil."),
    ("Sieve data (incl. 0.075 mm) required.",
     "Elek verisi gerekli (0,075 mm dahil)."),
    ("Sieve data (incl. 0.063 mm) required.",
     "Elek verisi gerekli (0,063 mm dahil)."),
    ("Sieve analysis is required.", "Elek analizi gerekli."),
    ("Atterberg limits missing; fines assumed silty (M).",
     "Atterberg limitleri eksik; ince dane siltli (M) kabul edildi."),
    ("Atterberg limits required for fine soil.",
     "İnce daneli zemin için Atterberg limitleri gerekli."),
    ("Atterberg limits missing; assumed A-4.",
     "Atterberg limitleri eksik; A-4 kabul edildi."),
    ("Cu/Cc not computable; assumed poorly graded.",
     "Cu/Cc hesaplanamadı; kötü derecelenmiş kabul edildi."),
    ("Organic soil -> suffix 'O'.", "Organik zemin -> 'O' eki."),
    ("Fines assumed silty (no/low plasticity data).",
     "İnce dane siltli kabul edildi (plastisite verisi yok/düşük)."),
    ("Non-plastic fine sand", "Plastik olmayan ince kum"),
    ("Group Index GI", "Grup İndisi GI"),
    ("Meets A-1-a limits.", "A-1-a sınırlarını sağlıyor."),
    ("Meets A-1-b limits.", "A-1-b sınırlarını sağlıyor."),
    ("Granular with plastic fines", "Plastik ince daneli granüler malzeme"),
    ("Silt-clay material", "Silt-kil malzeme"),
    ("Organic silt/clay (low plasticity)",
     "Organik silt/kil (düşük plastisite)"),
    ("Organic silt/clay (high plasticity)",
     "Organik silt/kil (yüksek plastisite)"),
    ("Fine-grained soil", "İnce daneli zemin"),
    ("Lean clay", "Zayıf kil"),
    ("Fat clay", "Yağlı kil"),
    ("Elastic silt", "Elastik silt"),
    ("Silty clay", "Siltli kil"),
    ("fraction dominates the coarse portion", "fraksiyonu iri dane kısmına hakim"),
    ("dominates the coarse portion", "iri dane kısmına hakim"),
    ("dominates the coarse fraction.", "iri dane fraksiyonuna hakim."),
    ("Fines >= 50 % -> fine soil.", "İnce dane >= %50 -> ince daneli zemin."),
    ("Fines < 50 % -> coarse soil;", "İnce dane < %50 -> iri daneli zemin;"),
    ("is the primary fraction.", "ana fraksiyondur."),
    ("> 15 % -> prefix", "> %15 -> ön ek"),
    ("> 15 % -> tertiary prefix", "> %15 -> üçüncül ön ek"),
    ("Fines < 5 % -> no fines prefix.",
     "İnce dane < %5 -> ince dane ön eki yok."),
    ("Fines 5-15 % -> fines prefix and grading letter.",
     "İnce dane %5-15 -> ince dane ön eki ve derecelenme harfi."),
    ("Fines > 15 % -> fines prefix, no grading letter.",
     "İnce dane > %15 -> ince dane ön eki, derecelenme harfi yok."),
    ("Silty-clay fines (ClL-SiL) in a 5-15 % soil -> 'sicl', grading "
     "letter omitted.",
     "%5-15 ince daneli zeminde siltli kil (ClL-SiL) -> 'sicl', "
     "derecelenme harfi yazılmadı."),
    ("On/above the A-line with 4 <= PI <= 7 -> silty clay (ClL-SiL).",
     "A-hattı üzerinde/üstünde ve 4 <= PI <= 7 -> siltli kil (ClL-SiL)."),
    ("Cu/Cc not computable (10 % size not reached); grading letter "
     "omitted.",
     "Cu/Cc hesaplanamadı (D10 ulaşılamadı); derecelenme harfi "
     "yazılmadı."),
    ("Organic soil -> prefix 'or' and the word 'organic'.",
     "Organik zemin -> 'or' ön eki ve 'organik' sözcüğü."),
    ("WARNING: Atterberg limits missing; fines assumed silty - result is "
     "provisional.",
     "UYARI: Atterberg limitleri eksik; ince dane siltli varsayıldı - "
     "sonuç geçicidir."),
    ("(provisional)", "(geçici)"),
    ("A-line PI =", "A-hattı PI ="),
    ("fines are", "ince dane:"),
    ("prefix", "ön ek"),
    ("medium plasticity", "orta plastisite"),
    ("medium graded", "orta derecelenmiş"),
    ("uniformly graded", "düzgün derecelenmiş"),
    ("gap graded", "boşluklu derecelenmiş"),
        ("Well-graded", "İyi derecelenmiş"),
    ("Poorly-graded", "Kötü derecelenmiş"),
    ("Well graded", "İyi derecelenmiş"),
    ("Poorly graded", "Kötü derecelenmiş"),
    ("Uniformly graded", "Düzgün derecelenmiş"),
    ("well graded", "iyi derecelenmiş"),
    ("poorly graded", "kötü derecelenmiş"),
    ("Silty, clayey", "Siltli, killi"),
    ("slightly silty/clayey", "az siltli/killi"),
    ("very silty/clayey", "çok siltli/killi"),
    ("with sand", "(kumlu)"),
    ("with gravel", "(çakıllı)"),
    ("with silt", "(siltli)"),
    ("with clay", "(killi)"),
    ("Sandy", "Kumlu"),
    ("Gravelly", "Çakıllı"),
    ("sandy", "kumlu"),
    ("gravelly", "çakıllı"),
    ("Clayey", "Killi"),
    ("Silty", "Siltli"),
    ("clayey", "killi"),
    ("silty", "siltli"),
    ("Slightly", "Az"),
    ("Very", "Çok"),
    ("extremely high plasticity", "aşırı yüksek plastisite"),
    ("very high plasticity", "çok yüksek plastisite"),
    ("intermediate plasticity", "orta plastisite"),
    ("intermediate-plasticity", "orta plastisite"),
    ("low plasticity", "düşük plastisite"),
    ("high plasticity", "yüksek plastisite"),
    ("low electrical sensitivity", "düşük elektriksel duyarlılık"),
    ("intermediate electrical sensitivity", "orta elektriksel duyarlılık"),
    ("high electrical sensitivity", "yüksek elektriksel duyarlılık"),
    ("non-plastic", "plastik olmayan"),
    ("Non-plastic", "Plastik olmayan"),
    ("Organic clay", "Organik kil"),
    ("Organic silt", "Organik silt"),
    ("Organic soil", "Organik zemin"),
    ("organic", "organik"),
    ("fines are of", "ince danenin özelliği:"),
    ("Sieve analysis", "Elek analizi"),
    ("dual symbol", "çift sembol"),
    ("above A-line", "A-hattı üzerinde"),
    ("below A-line", "A-hattı altında"),
    ("on/above A-line", "A-hattı üzerinde/üstünde"),
    ("Liquid limit of the fines, LL", "İnce danenin likit limiti, LL"),
    ("Liquid limit not measured; LL", "Likit limit ölçülmedi; LL"),
    ("Supply LL with 2-M brine and with kerosene to also classify the "
     "fines by plasticity and electrical sensitivity",
     "İnce daneyi plastisite ve elektriksel duyarlılığa göre de "
     "sınıflandırmak için 2-M tuzlu su ve gazyağı ile LL ölçün"),
    ("electrical sensitivity", "elektriksel duyarlılık"),
    ("The sample lies on a boundary between", "Numune, şu sınır üzerinde:"),
    ("reported as", "olarak raporlandı:"),
    ("no data", "veri yok"),
    ("Fines", "İnce dane"),
    ("fines", "ince dane"),
    ("Gravel", "Çakıl"),
    ("gravel", "çakıl"),
    ("Sand", "Kum"),
    ("sand", "kum"),
    ("Clay", "Kil"),
    ("clay", "kil"),
    ("Silt", "Silt"),
    ("silt", "silt"),
    ("not measured", "ölçülmedi"),
    ("not computable", "hesaplanamadı"),
    ("assumed", "varsayıldı"),
    ("required", "gerekli"),
    ("GRAVEL", "ÇAKIL"),
    ("SAND", "KUM"),
    ("CLAY", "KİL"),
    ("SILT", "SİLT"),
    ("group", "grup"),
    (" and ", " ve "),
]

def _boundary_pattern(en: str):
    left = r"\b" if en[0].isalnum() else ""
    right = r"\b" if en[-1].isalnum() else ""
    return _re.compile(left + _re.escape(en) + right)


_COMPILED_PHRASE_TABLE = [
    (_boundary_pattern(en), tr) for en, tr in _PHRASE_TABLE
]


def translate_domain_text(text) -> str:
    if not text or get_language() != "tr":
        return text
    if text in _EXACT_TR:
        return _EXACT_TR[text]
    out = text
    for pattern, tr in _COMPILED_PHRASE_TABLE:
        out = pattern.sub(tr, out)
    return out
