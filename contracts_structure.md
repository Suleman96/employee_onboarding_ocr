# Contracts Structure

```text
contracts/
├── berlin/
│   ├── befristet/
│   │   └── 2026/
│   │       ├── ASN_AV_berlin_floor_supervisor_befristet_40.docx
│   │       ├── ASN_AV_berlin_glasreiniger_befristet_40.docx
│   │       ├── ASN_AV_berlin_hausmann_befristet_40.docx
│   │       ├── ASN_AV_berlin_hsk_befristet_40.docx
│   │       ├── ASN_AV_berlin_minibar_befristet_40.docx
│   │       ├── ASN_AV_berlin_nr_befristet_40.docx
│   │       ├── ASN_AV_berlin_public_area_befristet_40.docx
│   │       ├── ASN_AV_berlin_reinigungskraft_befristet_40.docx
│   │       ├── ASN_AV_berlin_stw_befristet_40.docx
│   │       └── Berlin_AV_Minijob_befristet_aktuell.docx
│   └── unbefristet/
│       ├── VORLAGEN Unbefristet_Adlon/
│       │   ├── berlin_AV_floor_supervisor_unbefristet_adlon_40.docx
│       │   ├── berlin_AV_glasreiniger_unbefristet_adlon_40.docx
│       │   ├── berlin_AV_hausmann_unbefristet_adlon_40.docx
│       │   ├── berlin_AV_hsk_unbefristet_adlon_40.docx
│       │   ├── berlin_AV_minibar_unbefristet_adlon_40.docx
│       │   ├── berlin_AV_nr_unbefristet_adlon_40.docx
│       │   ├── berlin_AV_public_area_unbefristet_adlon_40.docx
│       │   └── berlin_AV_stw_unbefristet_adlon_40.docx
│       └── VORLAGEN Unbefristet_GHB/
│           ├── berlin_AV_floor_supervisor_unbefristet_ghb_40.docx
│           ├── berlin_AV_glasreiniger_unbefristet_ghb_40.docx
│           ├── berlin_AV_hausmann_unbefristet_ghb_40.docx
│           ├── berlin_AV_hsk_unbefristet_ghb_40.docx
│           ├── berlin_AV_minibar_unbefristet_ghb_40.docx
│           ├── berlin_AV_nr_unbefristet_ghb_40.docx
│           └── berlin_AV_public_area_unbefristet_ghb_40.docx
├── berlin_template.docx
├── generator.py
├── koeln/
│   ├── BERGISCH GLADBACH_AV_HM-WM_BEFRISTET_40 Std.docx
│   ├── BERGISCH GLADBACH_AV_HSK SUPERVISOR_BEFRISTET_40 Std.docx
│   ├── BERGISCH GLADBACH_AV_HSK_BEFRISTET_25 Std_5 Tage-5 Std.docx
│   ├── BERGISCH GLADBACH_AV_HSK_BEFRISTET_30 Std_5 Tage-6 Std.docx
│   ├── BERGISCH GLADBACH_AV_HSK_BEFRISTET_35 Std_5 Tage-7 Std.docx
│   ├── BERGISCH GLADBACH_AV_HSK_BEFRISTET_40 Std.docx
│   └── BERGISCH GLADBACH_AV_NR_BEFRISTET_40 Std.docx
├── registry.py
├── temp_template/
│   ├── [Content_Types].xml
│   ├── _rels/
│   │   └── .rels
│   ├── customXml/
│   │   ├── item1.xml
│   │   ├── itemProps1.xml
│   │   └── _rels/
│   │       └── item1.xml.rels
│   ├── docProps/
│   │   ├── app.xml
│   │   ├── core.xml
│   │   └── custom.xml
│   └── word/
│       ├── document.xml
│       ├── endnotes.xml
│       ├── fontTable.xml
│       ├── footnotes.xml
│       ├── header1.xml
│       ├── header2.xml
│       ├── media/
│       ├── numbering.xml
│       ├── settings.xml
│       ├── styles.xml
│       ├── theme/
│       │   └── theme1.xml
│       ├── webSettings.xml
│       └── _rels/
│           ├── document.xml.rels
│           └── header2.xml.rels
└── wien/
    ├── ASN AV_20 Std_5 Tage-4 Std_Reinigungskraft_TD_Neu.docx
    ├── ASN AV_24 Std_3 Tage-8 Std_Zimmermädchen_Neu.docx
    ├── ASN AV_25 Std_5 Tage-5 Std_Reinigungskraft_TD_Neu.docx
    ├── ASN AV_30 Std_5 Tage-6 Std_Reinigungskraft_TD_Neu.docx
    ├── ASN AV_30 Std_5 Tage-6 Std_Zimmermädchen_Neu.docx
    ├── ASN AV_32 Std_4 Tage-8 Std_HSK Supervisor_Neu.docx
    ├── ASN AV_32 Std_4 Tage-8 Std_Reinigungskraft_PA_Neu.docx
    ├── ASN AV_32 Std_4 Tage-8 Std_Zimmermädchen_Neu.docx
    ├── ASN AV_40 Std_Ass. HSK Manager_Neu.docx
    ├── ASN AV_40 Std_HSK Manager_Neu.docx
    ├── ASN AV_40 Std_HSK Supervisor_Neu.docx
    ├── ASN AV_40 Std_Objektleitung_NR_Neu.docx
    ├── ASN AV_40 Std_Quality Manager_Neu.docx
    ├── ASN AV_40 Std_Reinigungskraft_HM_Neu.docx
    ├── ASN AV_40 Std_Reinigungskraft_NR_Neu.docx
    ├── ASN AV_40 Std_Reinigungskraft_Public_Neu.docx
    ├── ASN AV_40 Std_Reinigungskraft_STW_NEU.docx
    ├── ASN AV_40 Std_STW Manager_Neu.docx
    ├── ASN AV_40 Std_STW Supervisor_Neu.docx
    └── ASN AV_40 Std_Zimmermädchen_Neu.docx
```

This document describes the contract template organization for the `employee_onboarding_ocr` project.

## Root Layout

- `contracts/`
  - Contains contract templates for different cities and contract types.
  - Hosts the contract generation helper `generator.py`.
  - Includes example/default template files and a temporary unpacked `.docx` template structure.

## Important Files

- `contracts/generator.py`
  - Core contract generation module.
  - Builds a Jinja context from an employee object.
  - Loads a `.docx` template and renders it with `docxtpl`.
  - Saves output to the repository `output/` directory.
  - Converts `.docx` files to PDF when needed.

- `contracts/berlin_template.docx`
  - Default contract template used by `generate_contract_for_employee()` if no other template is specified.

## City-Specific Template Folders

### `contracts/berlin/`

- `befristet/`
  - Contains fixed-term (`befristet`) Berlin contract templates.
  - Includes year-specific subfolders such as `2026/`.
  - Example files:
    - `ASN_AV_berlin_hausmann_befristet_40.docx`
    - `ASN_AV_berlin_hsk_befristet_40.docx`

- `unbefristet/`
  - Contains permanent (`unbefristet`) Berlin contract templates.
  - Has separate folders for template families, such as:
    - `VORLAGEN Unbefristet_Adlon/`
    - `VORLAGEN Unbefristet_GHB/`
  - Example files:
    - `berlin_AV_hsk_unbefristet_adlon_40.docx`
    - `berlin_AV_minibar_unbefristet_ghb_40.docx`

### `contracts/koeln/`

- Contains contract templates for Cologne.
- Filenames include city, contract type, hours, and occupation.
- Example files:
  - `BERGISCH GLADBACH_AV_HSK_SUPERVISOR_BEFRISTET_40 Std.docx`
  - `BERGISCH GLADBACH_AV_NR_BEFRISTET_40 Std.docx`

### `contracts/wien/`

- Contains Vienna contract templates.
- Filenames include city, contract hours, role, and a `Neu` suffix.
- Example files:
  - `ASN AV_40 Std_HSK Manager_Neu.docx`
  - `ASN AV_32 Std_Zimmermädchen_Neu.docx`

### `contracts/temp_template/`

- Contains the raw `.docx` package extracted into XML.
- Useful for debugging or manually inspecting the internal Word XML structure.
- Includes folders like `word/`, `_rels/`, `docProps/`, and `customXml/`.

## Template Filename Conventions

- Berlin befristet: `ASN_AV_berlin_{occupation}_befristet_40.docx`
- Berlin unbefristet (with subgroup): `berlin_AV_{occupation}_unbefristet_{subgroup}_40.docx`
  - `{subgroup}` is either `adlon` or `ghb`
- Template file names generally encode:
  - City or location identifier
  - `AV` prefix for employment contract
  - Occupation code (lowercase, underscores)
  - Contract type (`befristet` or `unbefristet`)
  - Subgroup (`adlon` / `ghb`) where applicable
  - Hours per week (e.g. `40`)

## Generated Output Structure

- Generated contracts are saved to the root `output/` directory.
- Output filenames are built with `contracts/generator.py::build_output_filename()`.
- Example generated filename pattern:
  - `AV_<occupation>_<employee_id>_<first_name>_<last_name>_<start_date>.docx`
- The generator also deletes old contracts for the same employee before saving a new one.

## Available Template Context Keys

The contract templates can use the following Jinja variables built from the employee model:

- `salutation`
- `first_name`
- `last_name`
- `full_name`
- `gender`
- `date_of_birth`
- `place_of_birth`
- `country_of_birth`
- `nationality`
- `ausweis_number`
- `reise_pass_number`
- `phone`
- `email`
- `street_and_house_number`
- `zip_code`
- `city`
- `country`
- `full_address`
- `krankenkasse`
- `krankenkasse_nummer`
- `steuer_id`
- `steuerklasse`
- `sozialversicherungsnummer`
- `bank_name`
- `bank_iban`
- `bank_bic`
- `bank_account_holder`
- `work_city`
- `occupation`
- `employment_type`
- `weekly_hours`
- `work_days_per_week`
- `daily_hours`
- `work_schedule`
- `contract_type`
- `start_date`
- `end_date`
- `disabled`
- `status`
- `ordio_id`

## Notes

- The actual contract text is stored in `.docx` templates and may contain Jinja tags like `{{ first_name }}`.
- To add a new template, place a `.docx` file in the appropriate city folder and use its path as `template_name` when calling the generator.
- `contracts/generator.py` ensures templates render properly by merging split Jinja runs inside the Word document XML.
