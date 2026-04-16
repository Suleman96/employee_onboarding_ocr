import re
from pathlib import Path
from typing import Any, Dict, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = BASE_DIR / "contracts"

CITY_ALIASES = {
    "berlin": "berlin",
    "berlin ": "berlin",
    "köln": "koeln_group",
    "koeln": "koeln_group",
    "bergisch gladbach": "bergisch_gladbach",
    "bergisch_gladbach": "bergisch_gladbach",
    "düsseldorf": "duesseldorf",
    "dusseldorf": "duesseldorf",
    "duesseldorf": "duesseldorf",
    
    "frankfurt": "frankfurt",
    "hamburg": "hamburg",
    "münchen": "muenchen",
    "munchen": "muenchen",
    "muenchen": "muenchen",

    "wien": "wien",
    "vienna": "wien",
}
CONTRACT_TYPE_ALIASES = {
    "befristet": "befristet",
    "befristet ": "befristet",
    "temporär": "befristet",
    "temporar": "befristet",
    "temporary": "befristet",
    "temp": "befristet",
    
    
    "unbefristet": "unbefristet",
    "permanent ": "unbefristet",
    "permanent": "unbefristet",
}

OCCUPATION_ALIASES = {
    "floor supervisor": "floor_supervisor",
    "floor_supervisor": "floor_supervisor",

    "hsk": "hsk",
    "housekeeping": "hsk",

    "hsk manager": "hsk_manager",
    "housekeeping manager": "hsk_manager",

    "hsk supervisor": "hsk_supervisor",
    "housekeeping supervisor": "hsk_supervisor",
    "hsk_supervisor": "hsk_supervisor",

    "glasreiniger": "glasreiniger",
    "hausmann": "hausmann",
    "hm-wm": "hausmann",
    "hm_wm": "hausmann",
    "minibar": "minibar",
    "nr": "nr",
    "public area": "public_area",
    "public_area": "public_area",
    "stw": "stw",
    "stw supervisor": "stw_supervisor",
    "stw manager": "stw_manager",
    "reinigungskraft": "reinigungskraft",
    "reinigungskraft td": "reinigungskraft_td",
    "reinigungskraft pa": "reinigungskraft_pa",
    "reinigungskraft hm": "reinigungskraft_hm",
    "reinigungskraft nr": "reinigungskraft_nr",
    "reinigungskraft public": "reinigungskraft_public",
    "reinigungskraft stw": "reinigungskraft_stw",
    "zimmermädchen": "zimmermaedchen",
    "zimmermadchen": "zimmermaedchen",
    "zimmermaedchen": "zimmermaedchen",

    # Wien-specific management roles observed in templates
    "quality manager": "quality_manager",
    "objektleitung nr": "objektleitung_nr",
    "objektleitung_nr": "objektleitung_nr",
    "ass. hsk manager": "ass_hsk_manager",
    "ass hsk manager": "ass_hsk_manager",
}


SUBGROUP_ALIASES = {
    # Adlon group
    "adlon": "adlon",
    "adlon group": "adlon",
    "hotel adlon kempinski": "adlon",
    # GHB group
    "ghb": "ghb",
    "ghb group": "ghb",
    "grand hyatt berlin": "ghb",
    "china club berlin": "ghb",
    "kontor haus": "ghb",
    "linden palais": "ghb",
    "pressehaus podium": "ghb",
}

def clean_text(value: Optional[str]) -> Optional[str]:
    """
    Normalize raw DB/form text into a comparable lowercase token.

    Returns None when the input is missing/empty so downstream normalization can
    distinguish "not provided" from an actual value.
    """
    if value is None:
        return None
    raw = str(value).strip().lower()
    return raw or None

def normalize_city(value: Optional[str]) -> Optional[str]:
    raw = clean_text(value)
    if raw is None:
        return None
    if raw in CITY_ALIASES:
        return CITY_ALIASES[raw]
    raise ValueError(f"Unknown city value: {value}")

def normalize_contract_type(value: Optional[str]) -> Optional[str]:
    raw = clean_text(value)
    if raw is None:
        return None
    if raw in CONTRACT_TYPE_ALIASES:
        return CONTRACT_TYPE_ALIASES[raw]
    raise ValueError(f"Unknown contract type value: {value}")

def normalize_occupation(value: Optional[str]) -> str:
    raw = clean_text(value)
    if raw is None:
        raise ValueError("Missing occupation value")
    if raw in OCCUPATION_ALIASES:
        return OCCUPATION_ALIASES[raw]
    raise ValueError(f"Unknown occupation value: {value}")

def normalize_subgroup(value: Optional[str]) -> Optional[str]:
    raw = clean_text(value)
    if raw is None:
        return None
    if raw in SUBGROUP_ALIASES:
        return SUBGROUP_ALIASES[raw]
    return raw

def normalize_weekly_hours(value: Optional[Any]) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        hours = float(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid weekly hours value: {value}")

    rounded = round(hours)
    if abs(hours - rounded) <= 1e-6:
        return int(rounded)
    raise ValueError(f"weekly_hours must be a whole number; got {value}")

def normalize_days_per_week(value: Optional[Any]) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        raise ValueError(f"Invalid days per week value: {value}")

def normalize_hours_per_day(value: Optional[Any]) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid hours per day value: {value}")


def normalize_department(value: Optional[str]) -> Optional[str]:
    # Department is not currently used for template resolution, 
    # but we normalize it here in case it's needed in the future.
    
    raw = clean_text(value)
    if raw is None:
        return None
    
    mapping = {
        "reinigung": "reinigung",
        "housekeeping/zimmermädchen": "housekeeping/zimmermaedchen",
        "nachtrieinigung": "nachtrieinigung",
        "hausmann-/wäschemannabteilung": "hausmann",
        "hausmann-/waschenmannabteilung": "hausmann",
        "public area": "public_area",
        "stwearding/geschirrspüler-abteilung": "stw",
        "stewarding/geschirrspueler-abteilung": "stw",
    }
    
    return mapping.get(raw, raw)


def normalize_contract_attributes(employee) -> Dict[str, Any]:
    return {
        "city_code": normalize_city(getattr(employee, "work_city", None)),
        "contract_type_code": normalize_contract_type(getattr(employee, "contract_type", None)),
        "occupation_code": normalize_occupation(getattr(employee, "occupation", None)),
        "weekly_hours": normalize_weekly_hours(getattr(employee, "weekly_hours", None)),
        "days_per_week": normalize_days_per_week(getattr(employee, "work_days_per_week", None)),
        "daily_hours": normalize_hours_per_day(getattr(employee, "daily_hours", None)),
        "subgroup_code": normalize_subgroup(getattr(employee, "hotel_name", None)),
    }


def ensure_exists(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Template file not found: {path}")
    return path


def find_first_existing(candidates: list[Path]) -> Path:
    for path in candidates:
        if path.exists():
            return path
    checked = "\n".join(str(p) for p in candidates)
    raise FileNotFoundError(f"No matching template found. Checked:\n{checked}")


UNBEFRISTET_SUBGROUP_FOLDER = {
    "adlon": "VORLAGEN Unbefristet_Adlon",
    "ghb": "VORLAGEN Unbefristet_GHB",
}

_BERLIN_ROLE_TOKEN = {
    # Berlin befristet templates use "FLOOR SUPERVISOR" in the filename.
    "floor_supervisor": {"befristet": "floor_supervisor", "unbefristet": "floor_supervisor"},
    "hsk": {"befristet": "HSK", "unbefristet": "HSK"},
    "glasreiniger": {"befristet": "GLASREINIGER", "unbefristet": "GLASREINIGER"},
    "hausmann": {"befristet": "HAUSMANN", "unbefristet": "HAUSMANN"},
    "minibar": {"befristet": "MINIBAR", "unbefristet": "MINIBAR"},
    "minijob": {"befristet": "minijob", "unbefristet": None},
    "nr": {"befristet": "NR", "unbefristet": "NR"},
    "public_area": {"befristet": "PUBLIC AREA", "unbefristet": "PUBLIC AREA"},
    "stw": {"befristet": "STW", "unbefristet": "STW"},
    "reinigungskraft": {"befristet": "REINIGUNGSKRAFT", "unbefristet": None},  # unbefristet file not observed
    # "zimmermaedchen": {"befristet": None, "unbefristet": None},
}


_KOELN_GROUP_ROLE_TOKEN = {
    "hausmann": "HM-WM",
    "hsk": "HSK",
    "hsk_supervisor": "HSK SUPERVISOR",
    "nr": "NR",
}

_WIEN_ROLE_TOKEN = {
    # No plain "Reinigungskraft" Wien file exists; the 20h/5-day/4h template is the TD variant.
    "reinigungskraft": "Reinigungskraft_TD",
    "reinigungskraft_td": "Reinigungskraft_TD",
    "reinigungskraft_pa": "Reinigungskraft_PA",
    "reinigungskraft_hm": "Reinigungskraft_HM",
    "reinigungskraft_nr": "Reinigungskraft_NR",
    "reinigungskraft_public": "Reinigungskraft_Public",
    "reinigungskraft_stw": "Reinigungskraft_STW",
    "zimmermaedchen": "Zimmermädchen",
    "hsk_supervisor": "HSK_Supervisor",
    "hsk_manager": "HSK_Manager",
    "ass_hsk_manager": "Ass_HSK_Manager",
    "stw_supervisor": "STW_Supervisor",
    "stw_manager": "STW_Manager",
    "objektleitung_nr": "Objektleitung_NR",
    "quality_manager": "Quality_Manager",
}

CITY_ROLE_SCHEDULE_RULES = {
    "wien": {
        "reinigungskraft": [(20, 5, 4)],
        "reinigungskraft_td": [(20, 5, 4), (25, 5, 5), (30, 5, 6)],
        "reinigungskraft_pa": [(32, 4, 8)],
        "reinigungskraft_hm": [(40, 5, 8)],
        "reinigungskraft_nr": [(40, 5, 8)],
        "reinigungskraft_public": [(40, 5, 8)],
        "reinigungskraft_stw": [(40, 5, 8)],
        "zimmermaedchen": [(24, 3, 8), (30, 5, 6), (32, 4, 8), (40, 5, 8)],
        "hsk_supervisor": [(32, 4, 8), (40, 5, 8)],
        "hsk_manager": [(40, 5, 8)],
        "ass_hsk_manager": [(40, 5, 8)],
        "stw_supervisor": [(40, 5, 8)],
        "stw_manager": [(40, 5, 8)],
        "objektleitung_nr": [(40, 5, 8)],
        "quality_manager": [(40, 5, 8)],
    }
}



def _pick_by_contains(dir_path: Path, required_substrings: list[str]) -> Path:
    candidates = sorted(dir_path.glob("*.docx"))
    for path in candidates:
        # Make matching resilient to "PUBLIC AREA" vs "public_area" filename drift.
        name_norm = path.name.lower().replace("_", " ").replace(".", "")
        if all(s.lower().replace("_", " ").replace(".", "") in name_norm for s in required_substrings):
            return path
    checked = "\n".join(str(p) for p in candidates) or f"(no .docx files in {dir_path})"
    raise FileNotFoundError(
        "No matching template found in "
        + str(dir_path)
        + " for: "
        + ", ".join(required_substrings)
        + "\nChecked:\n"
        + checked
    )

def _wien_role_candidates(base_dir: Path, role_token: str) -> list[Path]:
    role_slug = role_token.lower().replace(" ", "_").replace(".", "")
    prefix = f"asn_av_wien_{role_slug}_"
    return [
        path
        for path in sorted(base_dir.glob("*.docx"))
        if path.stem.lower().replace(".", "").startswith(prefix)
    ]

def _wien_role_hour_candidates(base_dir: Path, role_token: str, weekly_hours: int) -> list[Path]:
    role_slug = role_token.lower().replace(" ", "_").replace(".", "")
    prefix = f"asn_av_wien_{role_slug}_"
    hour_token = f"_{weekly_hours}_std"
    return [
        path
        for path in sorted(base_dir.glob("*.docx"))
        if path.stem.lower().replace(".", "").startswith(prefix)
        and hour_token in path.stem.lower().replace(".", "")
    ]

def _extract_hours_from_filename(path: Path) -> Optional[int]:
    match = re.search(r"_(\d+)_std", path.stem.lower())
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None

def _pick_by_contains_fallback(dir_path: Path, required_options: list[list[str]]) -> Path:
    """
    Try multiple required-substring sets (in order) and return the first match.

    This is useful when template naming conventions drift across years/folders
    (e.g., "40 Std" vs "_40").
    """
    last_err: Optional[Exception] = None
    for required in required_options:
        try:
            return _pick_by_contains(dir_path, required)
        except FileNotFoundError as e:
            last_err = e
            continue
    # Bubble up the last error (includes the checked file list).
    if last_err:
        raise last_err
    raise FileNotFoundError(f"No matching template found in {dir_path}")

def _require(value: Any, field: str) -> Any:
    
    if value is None or value == "":
        raise ValueError(f"{field} is required to resolve a contract template")
    return value

def validate_contract_selection(attrs: Dict[str, Any]) -> None:
    city = attrs.get("city_code")
    occupation = attrs.get("occupation_code")
    weekly_hours = attrs.get("weekly_hours")
    days_per_week = attrs.get("days_per_week")
    daily_hours = attrs.get("daily_hours")
    
    if not city:
        raise ValueError("work_city is required to resolve a contract template")
    
    if not occupation:
        raise ValueError("occupation is required to resolve a contract template")
    
    city_rules = CITY_ROLE_SCHEDULE_RULES.get(city)
    if not city_rules:
        return # no special validation for this city 
    
    allowed_combinations = city_rules.get(occupation)
    if not allowed_combinations:
        raise ValueError(
            f"Occupation '{occupation}' is not supported for city '{city}'"
        )
    if weekly_hours is None:
        available_hours = sorted({combo[0] for combo in allowed_combinations})
        raise ValueError(
            f"weekly_hours is required for city '{city}' and occupation '{occupation}'. "
            f"Available hours: {', '.join(str(h) for h in available_hours)}"
        )
        
    if days_per_week is None:
        available_days = sorted({combo[1] for combo in allowed_combinations })
        raise ValueError(
            f"work_day_per_week is required for city '{city}' and occupation '{occupation}'."
            f"Available days/week: {', '.join(str(d) for d in available_days)}"
            
        )
        
    if daily_hours is None:
        available_daily = sorted({combo[2] for combo in allowed_combinations })
        raise ValueError(
            f"daily_hours is required for city '{city}' and occupation '{occupation}'. "
            f"Available daily hours: {', '.join(str(d) for d in available_daily)}"
        )
        
    # Normalize daily hours for comparison: 8 == 8.0 should match
    actual = (int(weekly_hours), int(days_per_week), float(daily_hours))
    
    def _combo_matches(candidate: tuple[int, int, int]) -> bool:
        return (
        int(candidate[0]) == actual[0]
        and int(candidate[1]) == actual[1]
        and float(candidate[2]) == actual[2]
    )
        
    if not any(_combo_matches(combo) for combo in allowed_combinations):
        allowed_text = "; ".join(
            f"{w}/{d}/{dh}" for w, d, dh in allowed_combinations
        )
        
        raise ValueError(
            f"Invalid schedule for city '{city}' and occupation '{occupation}'."
            f"Got {actual[0]}/{actual[1]}/{actual[2]}. "
            f"Allowed combinations: {allowed_text}"
        )
            
    

def resolve_berlin_template(attrs: Dict[str, Any]) -> Path:
    contract_type = attrs["contract_type_code"]
    occupation = attrs["occupation_code"]
    subgroup = attrs.get("subgroup_code")
    weekly_hours = attrs.get("weekly_hours")

    _require(contract_type, "contract_type")
    _require(occupation, "occupation")

    if contract_type == "unbefristet":
        subgroup_folder  = UNBEFRISTET_SUBGROUP_FOLDER.get(subgroup or "")
        if not subgroup_folder:
            raise ValueError(
                f"Berlin unbefristet requires subgroup 'adlon' or 'ghb'. Got '{subgroup}'"
            )
        base_dir = CONTRACTS_DIR / "berlin" / "unbefristet" / subgroup_folder
    else:
        base_dir = CONTRACTS_DIR / "berlin" / contract_type / "2026"

    # Berlin files are largely "40 Std". Default to 40 if weekly_hours missing.
    hours = weekly_hours or 40

    role_token = (_BERLIN_ROLE_TOKEN.get(occupation) or {}).get(contract_type)
    if role_token is None and occupation == "floor_supervisor" and contract_type == "befristet":
        role_token = "FLOOR SUPERVISOR"
    if role_token is None:
        raise ValueError(f"No Berlin template mapping for occupation '{occupation}' and '{contract_type}'")

    # Berlin filenames have appeared in two conventions:
    # - older: "..._40 Std_..." (with a space + "Std")
    # - current repo (2026 befristet): "..._befristet_40.docx" (underscore + number, no "Std")
    hours_required_sets = [
        ["ASN_AV_berlin", role_token, "BEFRISTET", f"{hours} Std"],
        ["ASN_AV_berlin", role_token, "BEFRISTET", f"_{hours}"],
    ]

    if contract_type == "befristet" and occupation == "floor_supervisor":
        # Example (older): Berlin_AV_FLOOR SUPERVISOR_BEFRISTET_40 Std_2025.docx
        # Example (current): ASN_AV_berlin_floor_supervisor_befristet_40.docx
        return _pick_by_contains_fallback(base_dir, hours_required_sets)

    if contract_type == "befristet" and occupation == "minijob":
        # This one doesn't follow the standard naming convention.
        return _pick_by_contains(base_dir, ["ASN_AV_berlin_Minijob_befristet"])

    if contract_type == "befristet":
        return _pick_by_contains_fallback(base_dir, hours_required_sets)

    # unbefristet files use _40 suffix (no "Std"), e.g.:
    # ASN_AV_berlin_hsk_unbefristet_adlon_40.docx
    # Fall back from the older "40 Std" convention to the current "_40" convention.
    hours_unbefristet_sets = [
        ["ASN_AV_berlin", role_token, "UNBEFRISTET", f"{hours} Std"],
        ["ASN_AV_berlin", role_token, "UNBEFRISTET", f"_{hours}"],
    ]
    return _pick_by_contains_fallback(base_dir, hours_unbefristet_sets)

KOELN_GROUP_CITIES = {
    "bergisch_gladbach",
    "duesseldorf",
    "frankfurt",
    "hamburg",
    "muenchen",
}

def resolve_koeln_group_template(attrs: Dict[str, Any]) -> Path:
    city = attrs["city_code"]
    contract_type = attrs["contract_type_code"]
    occupation = attrs["occupation_code"]
    weekly_hours = attrs["weekly_hours"]
    days_per_week = attrs["days_per_week"]
    daily_hours = attrs["daily_hours"]

    if city not in KOELN_GROUP_CITIES:
        raise ValueError(f"City '{city}' is not part of koeln_group")

    if weekly_hours is None:
        raise ValueError("weekly_hours is required for koeln_group templates")

    base_dir = CONTRACTS_DIR / "koeln_group" / city

    role_token = _KOELN_GROUP_ROLE_TOKEN.get(occupation)
    if role_token is None:
        raise ValueError(f"No koeln_group template mapping for occupation '{occupation}'")

    # Examples:
    # BERGISCH GLADBACH_AV_HSK_BEFRISTET_25 Std_5 Tage-5 Std.docx
    # BERGISCH GLADBACH_AV_HSK SUPERVISOR_BEFRISTET_40 Std.docx
    city_token = city.replace("_", " ").upper()
    hours_token = f"{weekly_hours} Std"
    required = [f"{city_token}_AV", role_token, "BEFRISTET", hours_token]
    # Some files add "5 Tage-5 Std" etc; we don't require that to match.
    return _pick_by_contains(base_dir, required)


def resolve_wien_template(attrs: Dict[str, Any]) -> Path:
    occupation = attrs["occupation_code"]
    weekly_hours = attrs["weekly_hours"]
    days_per_week = attrs.get("days_per_week")
    daily_hours = attrs.get("daily_hours")

    base_dir = CONTRACTS_DIR / "wien"

    role_token = _WIEN_ROLE_TOKEN.get(occupation)
    if role_token is None:
        raise ValueError(f"No Wien template mapping for occupation '{occupation}'")

    # Some Wien roles have exactly one template. In that case we can safely
    # resolve without weekly_hours.
    if weekly_hours is None:
        role_candidates = _wien_role_candidates(base_dir, role_token)
        if len(role_candidates) == 1:
            return role_candidates[0]

        available_hours = sorted(
            {
                h
                for h in (_extract_hours_from_filename(path) for path in role_candidates)
                if h is not None
            }
        )
        if available_hours:
            raise ValueError(
                "weekly_hours is required for Wien templates "
                f"for occupation '{occupation}'. Available hours: {', '.join(str(h) for h in available_hours)}"
            )
        raise ValueError(
            "weekly_hours is required for Wien templates "
            f"for occupation '{occupation}'"
        )
    
    
    hour_candidates = _wien_role_hour_candidates(base_dir, role_token, weekly_hours)
    if len(hour_candidates) == 1:
        return hour_candidates[0]
    # If multiple templates match same role + weekly hours, narrow by days/daily hours
    if len(hour_candidates) > 1 and days_per_week is not None and daily_hours is not None:
        narrowed = []
        for path in hour_candidates:
            stem = path.stem.lower().replace(".", "")
            day_token = f"_{int(days_per_week)}_tage_"
            daily_token = f"_{int(float(daily_hours))}_std"
            if day_token in stem and daily_token in stem:
                narrowed.append(path)
                #If:
                #days_per_week = 5
                #daily_hours = 5.0

                #Then:
                #day_token = "_5_tage_"
                #daily_token = "_5_std"

        if len(narrowed) == 1:
            return narrowed[0]

        if len(narrowed) > 1:
            raise FileNotFoundError(
                "Multiple Wien templates matched for "
                f"occupation '{occupation}', weekly_hours '{weekly_hours}', "
                f"days_per_week '{days_per_week}', daily_hours '{daily_hours}':\n"
                + "\n".join(str(path) for path in narrowed)
            )
            
    if len(hour_candidates) > 1:
        raise FileNotFoundError(
            "Multiple Wien templates matched for "
            f"occupation '{occupation}' and weekly_hours '{weekly_hours}':\n"
            + "\n".join(str(path) for path in hour_candidates)
        )

    # Examples observed in this repo:
    # - ASN AV_40 Std_HSK Manager.docx
    # - ASN AV_32 Std_4 Tage-8 Std_Reinigungskraft_PA.docx
    # - ASN_AV_wien_Reinigungskraft_20_Std_5_Tage_4_Std.docx
    #
    # Prefer the explicit ASN_AV_wien_* naming when present to avoid
    # unintentionally matching a more specific variant (e.g. Reinigungskraft_TD).
    required_sets = [
        ["ASN_AV_wien", role_token, f"{weekly_hours}", "Std"],
        ["ASN AV", f"{weekly_hours} Std", role_token],
    ]
    return _pick_by_contains_fallback(base_dir, required_sets)


def resolve_template_path(employee) -> Path:
    
    attrs = normalize_contract_attributes(employee)
    city = attrs["city_code"]
    
    validate_contract_selection(attrs)
    
    if city == "berlin":
        return resolve_berlin_template(attrs)
    
    if city in KOELN_GROUP_CITIES:
        return resolve_koeln_group_template(attrs)
    
    if city == "wien":
        return resolve_wien_template(attrs)

    raise ValueError(f"No template found for city: {city}")
