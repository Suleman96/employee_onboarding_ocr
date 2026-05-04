# Contract Structure

Describes how contract templates are organised on disk and how `contracts/resolver.py` maps employee attributes to a template file.

---

## Directory Layout

```
contracts/
├── berlin/
│   ├── befristet/
│   │   └── 2026/                          ← active befristet templates
│   │       ASN_AV_berlin_<role>_befristet_<hours>.docx
│   └── unbefristet/
│       ├── VORLAGEN Unbefristet_Adlon/    ← Adlon subgroup
│       │   ASN_AV_berlin_<role>_unbefristet_adlon_<hours>.docx
│       └── VORLAGEN Unbefristet_GHB/     ← GHB subgroup
│           ASN_AV_berlin_<role>_unbefristet_ghb_<hours>.docx
│
├── koeln_group/
│   ├── bergisch_gladbach/                 ← flat folder, befristet only
│   │   ASN_AV_bergisch_gladbach_<role>_befristet_<hours>_Std_<days>_Tage_<daily>_Std.docx
│   ├── duesseldorf/                       ← flat folder
│   │   DUS_AV_<role>_UNBEFRISTET_40 Std_NEU.docx
│   ├── frankfurt/
│   │   ├── befristet/
│   │   │   FRA_AV_<role>_BEFRISTET_40 Std_NEU.docx
│   │   └── unbefristet/
│   │       MUC_AV_<role>_UNBEFRISTET_40 Std_NEU.docx
│   └── hamburg/
│       ├── Vorlagen Befristet/
│       │   HAM_AV_<role>_BEFRISTET_40 Std_NEU.docx
│       └── Vorlagen Unbefristet AV/
│           MUC_AV_<role>_UNBEFRISTET_40 Std_NEU.docx
│
└── wien/                                  ← flat folder
    ASN_AV_wien_<Role>_<hours>_Std[_<days>_Tage_<daily>_Std].docx
```

---

## Resolver Inputs

| Field | Employee Attribute | Notes |
|---|---|---|
| `city_code` | `work_city` | Normalised via `CITY_ALIASES` |
| `contract_type_code` | `contract_type` | `befristet` / `unbefristet` |
| `occupation_code` | `occupation` | Normalised via `OCCUPATION_ALIASES` |
| `weekly_hours` | `weekly_hours` | Integer; required for koeln_group & wien |
| `days_per_week` | `work_days_per_week` | Integer; used for wien narrowing |
| `daily_hours` | `daily_hours` | Float; used for wien narrowing |
| `subgroup_code` | `hotel_name` | Required for Berlin unbefristet (`adlon` / `ghb`) |

---

## City Routing

```
work_city  ──normalize──►  city_code  ──►  resolver function
────────────────────────────────────────────────────────────
berlin                      berlin          resolve_berlin_template()
köln / koeln                koeln_group     resolve_koeln_group_template()
bergisch gladbach           bergisch_gladbach  ↑ (same)
düsseldorf / duesseldorf    duesseldorf        ↑
frankfurt                   frankfurt          ↑
hamburg                     hamburg            ↑
münchen / muenchen          muenchen           ↑
wien / vienna               wien            resolve_wien_template()
```

---

## Berlin Templates

**Befristet** — folder: `contracts/berlin/befristet/2026/`

| Role (occupation_code) | File |
|---|---|
| `floor_supervisor` | `ASN_AV_berlin_floor_supervisor_befristet_40.docx` |
| `glasreiniger` | `ASN_AV_berlin_glasreiniger_befristet_40.docx` |
| `hausmann` | `ASN_AV_berlin_hausmann_befristet_40.docx` |
| `hsk` | `ASN_AV_berlin_hsk_befristet_40.docx` |
| `minibar` | `ASN_AV_berlin_minibar_befristet_40.docx` |
| `minijob` | `ASN_AV_berlin_minijob_befristet.docx` (no hours suffix) |
| `nr` | `ASN_AV_berlin_nr_befristet_40.docx` |
| `public_area` | `ASN_AV_berlin_public_area_befristet_40.docx` |
| `reinigungskraft` | `ASN_AV_berlin_reinigungskraft_befristet_40.docx` |
| `stw` | `ASN_AV_berlin_stw_befristet_40.docx` |

**Unbefristet — Adlon** — folder: `contracts/berlin/unbefristet/VORLAGEN Unbefristet_Adlon/`

`floor_supervisor`, `glasreiniger`, `hausmann`, `hsk`, `minibar`, `nr`, `public_area`, `stw` — all at 40 h.

**Unbefristet — GHB** — folder: `contracts/berlin/unbefristet/VORLAGEN Unbefristet_GHB/`

`floor_supervisor`, `glasreiniger`, `hausmann`, `hsk`, `minibar`, `nr`, `public_area` — all at 40 h.

> Berlin unbefristet requires `subgroup_code` = `adlon` or `ghb` (set from `hotel_name`).

---

## Koeln Group Templates

Cities: `bergisch_gladbach`, `duesseldorf`, `frankfurt`, `hamburg`, `muenchen`

### Bergisch Gladbach — flat folder `contracts/koeln_group/bergisch_gladbach/`

Naming: `ASN_AV_bergisch_gladbach_<role>_befristet_<hours>_Std_<days>_Tage_<daily>_Std.docx`

| Role | Hours / Days / Daily |
|---|---|
| `hsk` | 25/5/5, 30/5/6, 35/5/7, 40/5/8 |
| `hsk_supervisor` | 40/5/8 |
| `hausmann` | 40/5/8 |
| `nr` | 40/5/8 |

### Düsseldorf — flat folder `contracts/koeln_group/duesseldorf/`

`DUS_AV_<role>_UNBEFRISTET_40 Std_NEU.docx`  
Roles: `nr` (`NR`), `stw` (`STW`)

### Frankfurt

- Befristet: `contracts/koeln_group/frankfurt/befristet/`  
  `FRA_AV_<role>_BEFRISTET_40 Std_NEU.docx`  
  Roles: `nr` (`NR`), `public_area` / back-of-house (`PA-BOH`)

- Unbefristet: `contracts/koeln_group/frankfurt/unbefristet/`  
  `MUC_AV_<role>_UNBEFRISTET_40 Std_NEU.docx`  
  Roles: `hausmann` (`HM-WM`), `hsk` (`HSK`), `nr` (`NR`), `public_area` (`PA-BOH`), `stw` (`STW`), `hsk_supervisor` (`SV`), back-of-house manager

### Hamburg

- Befristet: `contracts/koeln_group/hamburg/Vorlagen Befristet/`  
  `HAM_AV_<role>_BEFRISTET_40 Std_NEU.docx`  
  Roles: `nr` (`NR`), `public_area` / back-of-house (`PA-BOH`)

- Unbefristet: `contracts/koeln_group/hamburg/Vorlagen Unbefristet AV/`  
  `MUC_AV_<role>_UNBEFRISTET_40 Std_NEU.docx`  
  Same roles as Frankfurt unbefristet.

> The resolver matches koeln_group templates using city token + role token + `BEFRISTET` + hours in the filename. The role token mapping is: `hausmann→HM-WM`, `hsk→HSK`, `hsk_supervisor→HSK SUPERVISOR`, `nr→NR`.

---

## Wien Templates

Folder: `contracts/wien/` (flat)

Naming: `ASN_AV_wien_<Role>_<hours>_Std[_<days>_Tage_<daily>_Std].docx`

All templates are effectively unbefristet (no contract_type suffix in filenames).

| Role (occupation_code) | File(s) |
|---|---|
| `reinigungskraft` / `reinigungskraft_td` | `Reinigungskraft_TD_20_Std_5_Tage_4_Std`, `_25_Std_5_Tage_5_Std`, `_30_Std_5_Tage_6_Std` |
| `reinigungskraft_pa` | `Reinigungskraft_PA_32_Std_4_Tage_8_Std` |
| `reinigungskraft_hm` | `Reinigungskraft_HM_40_Std` |
| `reinigungskraft_nr` | `Reinigungskraft_NR_40_Std` |
| `reinigungskraft_public` | `Reinigungskraft_Public_40_Std` |
| `reinigungskraft_stw` | `Reinigungskraft_STW_40_Std` |
| `zimmermaedchen` | `Zimmermädchen_24_Std_3_Tage_8_Std`, `_30_Std_5_Tage_6_Std`, `_32_Std_4_Tage_8_Std`, `_40_Std` |
| `hsk_supervisor` | `HSK_Supervisor_32_Std_4_Tage_8_Std`, `_40_Std` |
| `hsk_manager` | `HSK_Manager_40_Std` |
| `ass_hsk_manager` | `Ass_HSK_Manager_40_Std` |
| `stw_supervisor` | `STW_Supervisor_40_Std` |
| `stw_manager` | `STW_Manager_40_Std` |
| `objektleitung_nr` | `Objektleitung_NR_40_Std` |
| `quality_manager` | `Quality_Manager_40_Std` |

### Wien Schedule Validation (`CITY_ROLE_SCHEDULE_RULES`)

The resolver enforces allowed `(weekly_hours, days_per_week, daily_hours)` combinations before picking a file:

| Role | Allowed combinations (h/days/h-per-day) |
|---|---|
| `reinigungskraft` / `reinigungskraft_td` | 20/5/4 · 25/5/5 · 30/5/6 |
| `reinigungskraft_pa` | 32/4/8 |
| `reinigungskraft_hm/nr/public/stw` | 40/5/8 |
| `zimmermaedchen` | 24/3/8 · 30/5/6 · 32/4/8 · 40/5/8 |
| `hsk_supervisor` | 32/4/8 · 40/5/8 |
| `hsk_manager`, `ass_hsk_manager`, `stw_supervisor`, `stw_manager`, `objektleitung_nr`, `quality_manager` | 40/5/8 |

---

## Occupation Alias Map (input → code)

| User input | occupation_code |
|---|---|
| floor supervisor | `floor_supervisor` |
| hsk / housekeeping | `hsk` |
| hsk manager / housekeeping manager | `hsk_manager` |
| hsk supervisor / housekeeping supervisor | `hsk_supervisor` |
| glasreiniger | `glasreiniger` |
| hausmann / hm-wm | `hausmann` |
| minibar | `minibar` |
| nr | `nr` |
| public area | `public_area` |
| stw | `stw` |
| stw supervisor | `stw_supervisor` |
| stw manager | `stw_manager` |
| reinigungskraft | `reinigungskraft` |
| reinigungskraft td/pa/hm/nr/public/stw | `reinigungskraft_*` |
| zimmermädchen / zimmermaedchen | `zimmermaedchen` |
| quality manager | `quality_manager` |
| objektleitung nr | `objektleitung_nr` |
| ass. hsk manager | `ass_hsk_manager` |

---

## Adding a New Template

1. Drop the `.docx` file in the correct city/type folder following the naming convention for that city.
2. If the role is new, add an entry to `OCCUPATION_ALIASES` in `resolver.py`.
3. For Wien roles with multiple hour variants, add an entry to `CITY_ROLE_SCHEDULE_RULES["wien"]`.
4. For Wien roles, add the role token to `_WIEN_ROLE_TOKEN`.
5. For Berlin roles, add the role token to `_BERLIN_ROLE_TOKEN`.
6. For Koeln group roles, add the role token to `_KOELN_GROUP_ROLE_TOKEN`.
