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
│   │       ├── ASN_AV_berlin_minijob_befristet.docx
│   │       ├── ASN_AV_berlin_nr_befristet_40.docx
│   │       ├── ASN_AV_berlin_public_area_befristet_40.docx
│   │       ├── ASN_AV_berlin_reinigungskraft_befristet_40.docx
│   │       └── ASN_AV_berlin_stw_befristet_40.docx
│   └── unbefristet/
│       ├── VORLAGEN Unbefristet_Adlon/
│       │   ├── ASN_AV_berlin_floor_supervisor_unbefristet_adlon_40.docx
│       │   ├── ASN_AV_berlin_glasreiniger_unbefristet_adlon_40.docx
│       │   ├── ASN_AV_berlin_hausmann_unbefristet_adlon_40.docx
│       │   ├── ASN_AV_berlin_hsk_unbefristet_adlon_40.docx
│       │   ├── ASN_AV_berlin_minibar_unbefristet_adlon_40.docx
│       │   ├── ASN_AV_berlin_nr_unbefristet_adlon_40.docx
│       │   ├── ASN_AV_berlin_public_area_unbefristet_adlon_40.docx
│       │   └── ASN_AV_berlin_stw_unbefristet_adlon_40.docx
│       └── VORLAGEN Unbefristet_GHB/
│           ├── ASN_AV_berlin_floor_supervisor_unbefristet_ghb_40.docx
│           ├── ASN_AV_berlin_glasreiniger_unbefristet_ghb_40.docx
│           ├── ASN_AV_berlin_hausmann_unbefristet_ghb_40.docx
│           ├── ASN_AV_berlin_hsk_unbefristet_ghb_40.docx
│           ├── ASN_AV_berlin_minibar_unbefristet_ghb_40.docx
│           ├── ASN_AV_berlin_nr_unbefristet_ghb_40.docx
│           └── ASN_AV_berlin_public_area_unbefristet_ghb_40.docx
├── berlin_template.docx
├── generator.py
├── hours.py
├── koeln_group/
│   ├── bergisch_gladbach/
│   │   ├── ASN_AV_bergisch_gladbach_hausmann_befristet_40_Std_5_Tage_8_Std.docx
│   │   ├── ASN_AV_bergisch_gladbach_hsk_befristet_25_Std_5_Tage_5_Std.docx
│   │   ├── ASN_AV_bergisch_gladbach_hsk_befristet_30_Std_5_Tage_6_Std.docx
│   │   ├── ASN_AV_bergisch_gladbach_hsk_befristet_35_Std_5_Tage_7_Std.docx
│   │   ├── ASN_AV_bergisch_gladbach_hsk_befristet_40_Std_5_Tage_8_Std.docx
│   │   ├── ASN_AV_bergisch_gladbach_hsk_supervisor_befristet_40_Std_5_Tage_8_Std.docx
│   │   └── ASN_AV_bergisch_gladbach_nr_befristet_40_Std_5_Tage_8_Std.docx
│   ├── duesseldorf/
│   │   ├── DUS_AV_NR_UNBEFRISTET_40 Std_NEU.docx
│   │   └── DUS_AV_STW_UNBEFRISTET_40 Std_NEU.docx
│   ├── frankfurt/
│   │   ├── Vorlagen Befristet/
│   │   │   ├── FRA_AV_NR_BEFRISTET_40 Std_NEU.docx
│   │   │   └── FRA_AV_PA-BOH_BEFRISTET_40 Std_NEU.docx
│   │   └── Vorlagen Unbefristet AV/
│   │       ├── MUC_AV_Back of House Manager_UNBEFRISTET_40 Std_NEU mit Probezeit.docx
│   │       ├── MUC_AV_HM-WM_UNBEFRISTET_40 Std_NEU.docx
│   │       ├── MUC_AV_HSK_UNBEFRISTET_40 Std_NEU.docx
│   │       ├── MUC_AV_MB_UNBEFRISTET_40 Std_NEU.docx
│   │       ├── MUC_AV_NR_UNBEFRISTET_40 Std_NEU.docx
│   │       ├── MUC_AV_PA-BOH_UNBEFRISTET_40 Std_NEU.docx
│   │       ├── MUC_AV_STW_UNBEFRISTET_40 Std_NEU.docx
│   │       └── MUC_AV_SV_UNBEFRISTET_40 Std_NEU.docx
│   └── hamburg/
│       ├── Vorlagen Befristet/
│       │   ├── HAM_AV_NR_BEFRISTET_40 Std_NEU.docx
│       │   └── HAM_AV_PA-BOH_BEFRISTET_40 Std_NEU.docx
│       └── Vorlagen Unbefristet AV/
│           ├── MUC_AV_Back of House Manager_UNBEFRISTET_40 Std_NEU mit Probezeit.docx
│           ├── MUC_AV_HM-WM_UNBEFRISTET_40 Std_NEU.docx
│           ├── MUC_AV_HSK_UNBEFRISTET_40 Std_NEU.docx
│           ├── MUC_AV_MB_UNBEFRISTET_40 Std_NEU.docx
│           ├── MUC_AV_NR_UNBEFRISTET_40 Std_NEU.docx
│           ├── MUC_AV_PA-BOH_UNBEFRISTET_40 Std_NEU.docx
│           ├── MUC_AV_STW_UNBEFRISTET_40 Std_NEU.docx
│           └── MUC_AV_SV_UNBEFRISTET_40 Std_NEU.docx
├── resolver.py
├── temp_template/
├── wien/
│   ├── Antrag_Beschäftigungsbewilligung/       ← historical PDFs, not templates
│   ├── NEU/                                     ← historical Abmeldungen/Anmeldungen PDFs
│   ├── ASN_AV_wien_Ass_HSK_Manager_40_Std.docx
│   ├── ASN_AV_wien_HSK_Manager_40_Std.docx
│   ├── ASN_AV_wien_HSK_Supervisor_32_Std_4_Tage_8_Std.docx
│   ├── ASN_AV_wien_HSK_Supervisor_40_Std.docx
│   ├── ASN_AV_wien_Objektleitung_NR_40_Std.docx
│   ├── ASN_AV_wien_Quality_Manager_40_Std.docx
│   ├── ASN_AV_wien_Reinigungskraft_20_Std_5_Tage_4_Std.docx
│   ├── ASN_AV_wien_Reinigungskraft_HM_40_Std.docx
│   ├── ASN_AV_wien_Reinigungskraft_NR_40_Std.docx
│   ├── ASN_AV_wien_Reinigungskraft_PA_32_Std_4_Tage_8_Std.docx
│   ├── ASN_AV_wien_Reinigungskraft_Public_40_Std.docx
│   ├── ASN_AV_wien_Reinigungskraft_STW_40_Std.docx
│   ├── ASN_AV_wien_Reinigungskraft_TD_20_Std_5_Tage_4_Std.docx
│   ├── ASN_AV_wien_Reinigungskraft_TD_25_Std_5_Tage_5_Std.docx
│   ├── ASN_AV_wien_Reinigungskraft_TD_30_Std_5_Tage_6_Std.docx
│   ├── ASN_AV_wien_STW_Manager_40_Std.docx
│   ├── ASN_AV_wien_STW_Supervisor_40_Std.docx
│   ├── ASN_AV_wien_Zimmermädchen_24_Std_3_Tage_8_Std.docx
│   ├── ASN_AV_wien_Zimmermädchen_30_Std_5_Tage_6_Std.docx
│   ├── ASN_AV_wien_Zimmermädchen_32_Std_4_Tage_8_Std.docx
│   └── ASN_AV_wien_Zimmermädchen_40_Std.docx
└── wien_template.docx
```

This document describes the contract template organization for the `employee_onboarding_ocr` project.

## Root Layout

- `contracts/`
  - Contains contract templates for different cities and contract types.
  - Hosts the contract generation helper `generator.py` and supporting modules.
  - Includes default template files (`berlin_template.docx`, `wien_template.docx`) and a temporary unpacked `.docx` template structure.

## Important Files

- `contracts/generator.py`
  - Core contract generation module.
  - Builds a Jinja context from an employee object.
  - Loads a `.docx` template and renders it with `docxtpl`.
  - Saves output to the repository `output/` directory.
  - Converts `.docx` files to PDF when needed.

- `contracts/resolver.py`
  - Resolves the correct template path from employee attributes (city, occupation, contract type, hours, etc.).

- `contracts/hours.py`
  - Helper module for working with weekly/daily hours schedules used in template resolution.

- `contracts/berlin_template.docx`
  - Default Berlin contract template used by `generate_contract_for_employee()` if no other template is specified.

- `contracts/wien_template.docx`
  - Default Wien contract template.

## City-Specific Template Folders

### `contracts/berlin/`

- `befristet/`
  - Contains fixed-term (`befristet`) Berlin contract templates.
  - Includes year-specific subfolders such as `2026/`.
  - Example files:
    - `ASN_AV_berlin_hausmann_befristet_40.docx`
    - `ASN_AV_berlin_hsk_befristet_40.docx`
    - `ASN_AV_berlin_minijob_befristet.docx`

- `unbefristet/`
  - Contains permanent (`unbefristet`) Berlin contract templates.
  - Has separate folders for template families, such as:
    - `VORLAGEN Unbefristet_Adlon/`
    - `VORLAGEN Unbefristet_GHB/`
  - All files follow the `ASN_AV_berlin_` prefix convention.
  - Example files:
    - `ASN_AV_berlin_hsk_unbefristet_adlon_40.docx`
    - `ASN_AV_berlin_minibar_unbefristet_ghb_40.docx`

### `contracts/koeln_group/`

Contains contract templates for all Koeln-group cities. Each city has its own subfolder.

- `bergisch_gladbach/` — all befristet, pattern: `ASN_AV_bergisch_gladbach_{occupation}_befristet_{weekly}_Std_{days}_Tage_{daily}_Std.docx`
  - Occupations: `hausmann`, `hsk`, `hsk_supervisor`, `nr`
  - Schedules: 25/5/5, 30/5/6, 35/5/7, 40/5/8

- `duesseldorf/` — unbefristet only (files not yet renamed to resolver pattern)

- `frankfurt/` — split into `Vorlagen Befristet/` and `Vorlagen Unbefristet AV/` subfolders (files not yet renamed)

- `hamburg/` — split into `Vorlagen Befristet/` and `Vorlagen Unbefristet AV/` subfolders (files not yet renamed)

### `contracts/wien/`

- Contains Vienna contract templates (fully renamed to resolver pattern).
- Filenames follow: `ASN_AV_wien_{occupation}_{weekly}_Std[_{days}_Tage_{daily}_Std].docx`
- Example files:
  - `ASN_AV_wien_HSK_Manager_40_Std.docx`
  - `ASN_AV_wien_Zimmermädchen_32_Std_4_Tage_8_Std.docx`
  - `ASN_AV_wien_Reinigungskraft_TD_25_Std_5_Tage_5_Std.docx`
- Also contains non-template subdirectories (historical records, not used by the generator):
  - `Antrag_Beschäftigungsbewilligung/` — archived employment permit PDFs
  - `NEU/` — archived Abmeldungen and Anmeldungen PDFs by month (2024)

### `contracts/temp_template/`

- Contains the raw `.docx` package extracted into XML.
- Useful for debugging or manually inspecting the internal Word XML structure.
- Includes folders like `word/`, `_rels/`, `docProps/`, and `customXml/`.

## Template Filename Conventions

- **Berlin befristet:** `ASN_AV_berlin_{occupation}_befristet_40.docx`
  - Minijob exception: `ASN_AV_berlin_minijob_befristet.docx` (no hours suffix)
- **Berlin unbefristet:** `ASN_AV_berlin_{occupation}_unbefristet_{subgroup}_40.docx`
  - `{subgroup}` is either `adlon` or `ghb`
- **Koeln group (bergisch_gladbach):** `ASN_AV_bergisch_gladbach_{occupation}_befristet_{weekly}_Std_{days}_Tage_{daily}_Std.docx`
- **Koeln group (other cities):** `ASN_AV_{city}_{occupation}_{contract_type}_{weekly}_Std_{days}_Tage_{daily}_Std.docx` *(duesseldorf, frankfurt, hamburg — not yet renamed)*
- **Wien:** `ASN_AV_wien_{occupation}_{weekly}_Std[_{days}_Tage_{daily}_Std].docx` *(fully renamed)*

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
