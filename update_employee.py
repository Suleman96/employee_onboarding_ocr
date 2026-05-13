from sqlalchemy.orm import Session

from database import Employee, AuditLog


CONF_RANK = {
    "high": 4,
    "medium": 3,
    "low": 2,
    "not_found": 1,
}


def pick_better_value(old_value, new_value, old_conf="not_found", new_conf="not_found"):
    if new_value in (None, "", []):
        return old_value, old_conf

    if old_value in (None, "", []):
        return new_value, new_conf

    if str(old_value).strip() == str(new_value).strip():
        return old_value, max(old_conf, new_conf, key=lambda x: CONF_RANK.get(x, 0))

    if CONF_RANK.get(new_conf, 0) > CONF_RANK.get(old_conf, 0):
        return new_value, new_conf

    return old_value, old_conf


def merge_extraction_results(results: list[dict]) -> dict:
    merged = {}
    merged_conf = {}
    conflicts = []

    for result in results:
        extracted = result.get("extracted_data", {})
        confidence = extracted.get("confidence", {})

        for key, value in extracted.items():
            if key == "confidence":
                continue

            old_value = merged.get(key)
            old_conf = merged_conf.get(key, "not_found")
            new_conf = confidence.get(key, "not_found")

            if old_value not in (None, "", []) and value not in (None, "", []) and str(old_value).strip() != str(value).strip():
                if CONF_RANK.get(new_conf, 0) == CONF_RANK.get(old_conf, 0):
                    conflicts.append({
                        "field": key,
                        "old_value": old_value,
                        "new_value": value,
                        "old_confidence": old_conf,
                        "new_confidence": new_conf,
                    })

            chosen_value, chosen_conf = pick_better_value(old_value, value, old_conf, new_conf)
            merged[key] = chosen_value
            merged_conf[key] = chosen_conf

    merged["confidence"] = merged_conf
    merged["conflicts"] = conflicts
    return merged


def map_extracted_to_employee_fields(data: dict) -> dict:
    return {
        "first_name": data.get("first_name"),
        "middle_name": data.get("middle_name"),
        "last_name": data.get("last_name"),
        "gender": data.get("gender"),
        "marital_status": data.get("marital_status"),
        "date_of_birth": data.get("date_of_birth"),
        "place_of_birth": data.get("place_of_birth"),
        "country_of_birth": data.get("country_of_birth"),
        "nationality": data.get("nationality"),
        "ausweis_number": data.get("id_number"),
        "reise_pass_number": data.get("passport_number"),
        "reise_pass_expiry_date": data.get("passport_expiry"),
        "working_permit_number": data.get("working_permit_number"),
        "working_permit_expiry": data.get("working_permit_expiry"),
        "street_and_house_number": data.get("street_and_number"),
        "zip_code": data.get("zip_code"),
        "city": data.get("city"),
        "country": data.get("country"),
        "bank_iban": data.get("iban"),
        "bank_bic": data.get("bic"),
        "bank_name": data.get("bank_name"),
        "bank_account_holder": data.get("account_owner"),
        "steuer_id": data.get("steuer_id"),
        "sozialversicherungsnummer": data.get("sozialversicherung"),
        "krankenkasse": data.get("health_insurance_name"),
        "krankenkasse_nummer": data.get("health_insurance_number"),
        "phone": data.get("phone"),
        "email": data.get("email"),
    }


def save_employee_draft(db: Session, mapped_data: dict, employee_id: int | None = None, performed_by: str = "ocr_pipeline"):
    if employee_id:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
    else:
        employee = Employee(status="draft")
        db.add(employee)

    for key, value in mapped_data.items():
        if hasattr(employee, key) and value not in (None, ""):
            setattr(employee, key, value)

    employee.status = "draft"

    db.commit()
    db.refresh(employee)

    audit = AuditLog(
        action="ocr_draft_save",
        employee_id=employee.id,
        details="Saved OCR/local-AI extraction draft",
        performed_by=performed_by,
    )
    db.add(audit)
    db.commit()

    return employee