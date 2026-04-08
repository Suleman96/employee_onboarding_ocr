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
    "reinigungskraft": "reinigungskraft",
    "zimmermädchen": "zimmermaedchen",
    "zimmermadchen": "zimmermaedchen",
    "zimmermaedchen": "zimmermaedchen",
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
    "floor_supervisor": {"befristet": "FLOOR SUPERVISOR", "unbefristet": "SUPERVISOR"},
    "hsk": {"befristet": "HSK", "unbefristet": "HSK"},
    "hsk_supervisor": {"befristet": None, "unbefristet": "SUPERVISOR"},  # no befristet file observed
    "hsk_manager": {"befristet": None, "unbefristet": None},
    "glasreiniger": {"befristet": "GLASREINIGER", "unbefristet": "GLASREINIGER"},
    "hausmann": {"befristet": "HAUSMANN", "unbefristet": "HAUSMANN"},
    "minibar": {"befristet": "MINIBAR", "unbefristet": "MINIBAR"},
    "nr": {"befristet": "NR", "unbefristet": "NR"},
    "public_area": {"befristet": "PUBLIC AREA", "unbefristet": "PUBLIC AREA"},
    "stw": {"befristet": "STW", "unbefristet": "STW"},
    "reinigungskraft": {"befristet": "REINIGUNGSKRAFT", "unbefristet": None},  # unbefristet file not observed
    "zimmermaedchen": {"befristet": None, "unbefristet": None},
}

_KOELN_GROUP_ROLE_TOKEN = {
    "hausmann": "HM-WM",
    "hsk": "HSK",
    "hsk_supervisor": "HSK SUPERVISOR",
    "nr": "NR",
}

_WIEN_ROLE_TOKEN = {
    "reinigungskraft": "Reinigungskraft",
    "zimmermaedchen": "Zimmermädchen",
    "hsk_supervisor": "HSK Supervisor",
    "hsk_manager": "HSK Manager",
    "stw": "STW Supervisor",
}

def _pick_by_contains(dir_path: Path, required_substrings: list[str]) -> Path:
    candidates = sorted(dir_path.glob("*.docx"))
    for path in candidates:
        name = path.name.lower()
        if all(s.lower() in name for s in required_substrings):
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

def _require(value: Any, field: str) -> Any:
    if value is None or value == "":
        raise ValueError(f"{field} is required to resolve a contract template")
    return value


def resolve_berlin_template(attrs: Dict[str, Any]) -> Path:
    contract_type = attrs["contract_type_code"]
    occupation = attrs["occupation_code"]
    subgroup = attrs.get("subgroup_code")
    weekly_hours = attrs.get("weekly_hours")

    _require(contract_type, "contract_type")
    _require(occupation, "occupation")

    if contract_type == "unbefristet":
        subfolder = UNBEFRISTET_SUBGROUP_FOLDER.get(subgroup or "", "VORLAGEN Unbefristet_Adlon")
        base_dir = CONTRACTS_DIR / "berlin" / "unbefristet" / subfolder
    else:
        base_dir = CONTRACTS_DIR / "berlin" / contract_type / "2026"

    # Berlin files are largely "40 Std". Default to 40 if weekly_hours missing.
    hours = weekly_hours or 40

    role_token = (_BERLIN_ROLE_TOKEN.get(occupation) or {}).get(contract_type)
    if role_token is None and occupation == "floor_supervisor" and contract_type == "befristet":
        role_token = "FLOOR SUPERVISOR"
    if role_token is None:
        raise ValueError(f"No Berlin template mapping for occupation '{occupation}' and '{contract_type}'")

    if contract_type == "befristet" and occupation == "floor_supervisor":
        # Example: Berlin_AV_FLOOR SUPERVISOR_BEFRISTET_40 Std_2025.docx
        return _pick_by_contains(base_dir, ["Berlin_AV", role_token, "BEFRISTET", f"{hours} Std"])

    if contract_type == "befristet" and occupation == "minibar":
        # This one doesn't follow the standard naming convention.
        return _pick_by_contains(base_dir, ["Berlin_AV_Minijob_befristet"])

    if contract_type == "befristet":
        return _pick_by_contains(base_dir, ["Berlin_AV", role_token, "BEFRISTET", f"{hours} Std"])

    # unbefristet examples:
    # Berlin_AV_HSK_UNBEFRISTET_40 Std...
    # Berlin_AV_SUPERVISOR_UNBEFRISTET_40 Std...
    return _pick_by_contains(base_dir, ["Berlin_AV", role_token, "UNBEFRISTET", f"{hours} Std"])

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
    # days_per_week and daily_hours are encoded in filenames for some Wien templates,
    # but not all are strictly needed if weekly_hours + role matches uniquely.

    if weekly_hours is None:
        raise ValueError("weekly_hours is required for Wien templates")

    base_dir = CONTRACTS_DIR / "wien"

    role_token = _WIEN_ROLE_TOKEN.get(occupation)
    if role_token is None:
        raise ValueError(f"No Wien template mapping for occupation '{occupation}'")

    # Example: ASN AV_40 Std_HSK Manager_Neu.docx
    return _pick_by_contains(base_dir, ["ASN AV", f"{weekly_hours} Std", role_token, "Neu"])


def resolve_template_path(employee) -> Path:
    attrs = normalize_contract_attributes(employee)
    city = attrs["city_code"]
    
    if city == "berlin":
        return resolve_berlin_template(attrs)
    
    if city in KOELN_GROUP_CITIES:
        return resolve_koeln_group_template(attrs)
    
    if city == "wien":
        return resolve_wien_template(attrs)

    raise ValueError(f"No template found for city: {city}")
